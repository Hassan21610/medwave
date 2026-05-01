import cv2
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap, QFont

class CameraPreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(320, 240)
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Camera")
        self.setStyleSheet("background:#f2f4f7; border-radius:14px;")

    def update_frame(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pix)

class ConfirmationOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConfirmOverlay")
        self.setStyleSheet("""
            #ConfirmOverlay {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 18px;
            }
            QLabel { color: #0b1220; }
        """)
        self.setFixedSize(520, 180)
        self.msg = QLabel("")
        self.msg.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.sub = QLabel("")
        self.sub.setFont(QFont("Segoe UI", 11))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(self.msg)
        layout.addWidget(self.sub)

    def resizeEvent(self, e):
        if self.parent():
            p = self.parent().rect()
            self.move((p.width() - self.width()) // 2, (p.height() - self.height()) // 2)
        super().resizeEvent(e)

    def show_message(self, title, subtitle):
        self.msg.setText(title)
        self.sub.setText(subtitle)
        self.show()

class VoiceIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.dot = QLabel("•")
        self.dot.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.dot.setStyleSheet("font-size: 22px; color: #3b82f6; font-weight: 900;")

        self.state_lbl = QLabel("Mic: Idle")
        self.state_lbl.setStyleSheet("color: #b8c7e6; font-size: 12px; font-weight: 800;")

        self.text_lbl = QLabel("Voice: -")
        self.text_lbl.setWordWrap(True)
        self.text_lbl.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }
        """)

        layout.addWidget(self.dot)
        layout.addWidget(self.state_lbl)
        layout.addWidget(self.text_lbl)

    def set_text(self, text: str):
        self.text_lbl.setText(f"Voice: {text}")
        lowered = text.lower()
        if "error" in lowered or "disabled" in lowered:
            self.set_error()

    def set_active(self, active: bool):
        self.state_lbl.setText("Mic: Listening" if active else "Mic: Idle")
        self.dot.setStyleSheet(
            "font-size: 22px; font-weight: 900; color: #22c55e;" if active
            else "font-size: 22px; font-weight: 900; color: #3b82f6;"
        )

    def set_error(self):
        self.state_lbl.setText("Mic: Error")
        self.dot.setStyleSheet("font-size: 22px; font-weight: 900; color: #ef4444;")


class GestureGuide(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Gesture Guide")
        title.setStyleSheet("font-size: 13px; font-weight: 900; color: #eaf2ff;")
        layout.addWidget(title)

        hints = QLabel(
            "3 Fingers (I+M+R) -> Next Page\n"
            "4 Fingers -> Previous Page\n"
            "Open Palm (all 5) -> Scroll Down\n"
            "Fist -> Scroll Up\n"
            "One Finger -> Zoom In\n"
            "Two Fingers -> Zoom Out"
        )
        hints.setStyleSheet("font-size: 11px; color: #b8c7e6; font-weight: 700;")
        hints.setWordWrap(True)
        layout.addWidget(hints)

        self.last_lbl = QLabel("Last recognized: -")
        self.last_lbl.setStyleSheet("font-size: 11px; color: #93c5fd; font-weight: 800;")
        layout.addWidget(self.last_lbl)

    def set_last_gesture(self, gesture: str):
        self.last_lbl.setText(f"Last recognized: {gesture}")
