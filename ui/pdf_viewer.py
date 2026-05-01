import os
import shutil
import fitz  # PyMuPDF

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QScrollArea, QDialog, QListWidget, QMessageBox, QFrame
)


class PDFLibraryDialog(QDialog):
    def __init__(self, parent, uploads_dir: str, on_open_callback):
        super().__init__(parent)
        self.uploads_dir = uploads_dir
        self.on_open_callback = on_open_callback

        self.setWindowTitle("PDF Library")
        self.setMinimumSize(520, 520)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        header = QLabel("PDF Library")
        header.setObjectName("AppTitle")
        root.addWidget(header)

        sub = QLabel("Upload multiple PDFs and choose which one to open.")
        sub.setObjectName("Subtle")
        root.addWidget(sub)

        self.list = QListWidget()
        root.addWidget(self.list, 1)

        row = QHBoxLayout()
        self.btn_upload = QPushButton("Upload PDFs")
        self.btn_upload.setObjectName("Primary")
        self.btn_open = QPushButton("Open Selected")
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_clear = QPushButton("Clear Library")

        row.addWidget(self.btn_upload)
        row.addWidget(self.btn_open)
        row.addWidget(self.btn_remove)
        row.addWidget(self.btn_clear)
        root.addLayout(row)

        self.btn_upload.clicked.connect(self.upload_multi)
        self.btn_open.clicked.connect(self.open_selected)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_clear.clicked.connect(self.clear_library)

        self.refresh()

    def refresh(self):
        self.list.clear()
        for fn in sorted(os.listdir(self.uploads_dir)):
            if fn.lower().endswith(".pdf"):
                self.list.addItem(fn)

    def upload_multi(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if not paths:
            return

        for path in paths:
            base = os.path.basename(path)
            dest = os.path.join(self.uploads_dir, base)

            if os.path.exists(dest):
                i = 2
                name, ext = os.path.splitext(base)
                while os.path.exists(dest):
                    dest = os.path.join(self.uploads_dir, f"{name}_{i}{ext}")
                    i += 1

            shutil.copy2(path, dest)

        self.refresh()

    def open_selected(self):
        item = self.list.currentItem()
        if not item:
            return
        path = os.path.join(self.uploads_dir, item.text())
        self.on_open_callback(path)
        self.accept()

    def remove_selected(self):
        item = self.list.currentItem()
        if not item:
            return
        fn = item.text()
        path = os.path.join(self.uploads_dir, fn)

        reply = QMessageBox.question(
            self, "Remove PDF",
            f"Delete '{fn}' from library?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

        self.refresh()

    def clear_library(self):
        reply = QMessageBox.question(
            self, "Clear Library",
            "Delete ALL PDFs from library?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        for fn in os.listdir(self.uploads_dir):
            if fn.lower().endswith(".pdf"):
                try:
                    os.remove(os.path.join(self.uploads_dir, fn))
                except Exception:
                    pass

        self.refresh()


class PDFViewer(QWidget):
    """
    Premium viewer:
    - Default fit-to-width ON
    - Zoom in/out disables fit-to-width
    - Reset zoom restores fit-to-width
    """
    def __init__(self, uploads_dir="uploads"):
        super().__init__()
        self.uploads_dir = uploads_dir
        os.makedirs(self.uploads_dir, exist_ok=True)

        self.doc = None
        self.page_index = 0
        self.current_path = None

        self.zoom = 1.0
        self.base_render = 2.3
        self.fit_to_width = True
        self._last_viewport_w = 0
        self.scroll_step = 220

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # Top controls (compact)
        top = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        self.page_lbl = QLabel("Page: -/-")
        self.page_lbl.setAlignment(Qt.AlignCenter)
        self.page_lbl.setObjectName("Subtle")

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        top.addWidget(self.btn_prev)
        top.addWidget(self.page_lbl, 1)
        top.addWidget(self.btn_next)
        root.addLayout(top)

        # Viewer surface
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)

        self.image_label = QLabel("No PDF loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            "background:#0c1728; border:1px solid #223a5d; border-radius:16px; padding:18px; color:#b8c7e6;"
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        card_layout.addWidget(self.scroll_area, 1)
        root.addWidget(card, 1)

    # ---------- Library ----------
    def open_library_dialog(self):
        dlg = PDFLibraryDialog(self, self.uploads_dir, self.load_pdf)
        dlg.exec()

    # ---------- Rendering ----------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.doc and self.fit_to_width:
            vw = self.scroll_area.viewport().width()
            if abs(vw - self._last_viewport_w) > 8:
                self._last_viewport_w = vw
                self.render_page()

    def load_pdf(self, path: str):
        try:
            self.doc = fitz.open(path)
            self.current_path = path
            self.page_index = 0
            self.zoom = 1.0
            self.fit_to_width = True
            self._last_viewport_w = self.scroll_area.viewport().width()
            self.render_page()
            self.scroll_to_top()
        except Exception:
            self.doc = None
            self.current_path = None
            self.image_label.setText("Failed to load PDF")
            self.page_lbl.setText("Page: -/-")

    def render_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_index)
        scale = self.base_render * self.zoom
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)

        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pm = QPixmap.fromImage(img)

        if self.fit_to_width:
            viewport_w = max(560, self.scroll_area.viewport().width() - 30)
            pm = pm.scaledToWidth(viewport_w, Qt.SmoothTransformation)

        self.image_label.setPixmap(pm)
        self.image_label.setMinimumSize(pm.size())
        self.page_lbl.setText(f"Page: {self.page_index + 1}/{self.doc.page_count}")

    # ---------- Pages ----------
    def prev_page(self):
        if self.doc and self.page_index > 0:
            self.page_index -= 1
            self.render_page()
            self.scroll_to_top()

    def next_page(self):
        if self.doc and self.page_index < self.doc.page_count - 1:
            self.page_index += 1
            self.render_page()
            self.scroll_to_top()

    # ---------- Zoom ----------
    def zoom_in(self):
        if not self.doc:
            return
        self.fit_to_width = False
        self.zoom = min(3.0, self.zoom + 0.25)
        self.render_page()

    def zoom_out(self):
        if not self.doc:
            return
        self.fit_to_width = False
        self.zoom = max(0.75, self.zoom - 0.25)
        self.render_page()

    def reset_zoom(self):
        if not self.doc:
            return
        self.zoom = 1.0
        self.fit_to_width = True
        self._last_viewport_w = self.scroll_area.viewport().width()
        self.render_page()
        self.scroll_to_top()

    # ---------- Scroll ----------
    def scroll_up(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() - self.scroll_step
        )

    def scroll_down(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() + self.scroll_step
        )

    def scroll_left(self):
        self.scroll_area.horizontalScrollBar().setValue(
            self.scroll_area.horizontalScrollBar().value() - self.scroll_step
        )

    def scroll_right(self):
        self.scroll_area.horizontalScrollBar().setValue(
            self.scroll_area.horizontalScrollBar().value() + self.scroll_step
        )

    def scroll_to_top(self):
        self.scroll_area.verticalScrollBar().setValue(0)
