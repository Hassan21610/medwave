from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)

from core.camera_worker import CameraWorker
from core.gesture_engine import GestureEngine, AppMode
from core.safety_layer import SafetyLayer
from core.action_executor import ActionExecutor
from core.voice_worker import VoiceWorker

from ui.widgets import CameraPreview, ConfirmationOverlay, VoiceIndicator
from ui.pdf_viewer import PDFViewer
from ui.theme import app_stylesheet


class MainWindow(QMainWindow):
    def __init__(self, user_name: str = "User"):
        super().__init__()
        self.setWindowTitle("MedWave Control")
        self.setMinimumSize(1380, 780)
        self.setStyleSheet(app_stylesheet())

        self.user_name = user_name

        # Core
        self.mode = AppMode.SURGICAL
        self.gesture_engine = GestureEngine(mode=self.mode)
        self.safety = SafetyLayer(mode=self.mode)
        self.executor = ActionExecutor()

        # Root
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)

        # -----------------------
        # Top Bar
        # -----------------------
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top = QHBoxLayout(self.top_bar)
        top.setContentsMargins(16, 12, 16, 12)
        top.setSpacing(10)

        self.title_lbl = QLabel("MedWave Control")
        self.title_lbl.setObjectName("AppTitle")

        self.mode_btn = QPushButton("Mode: SURGICAL")
        self.mode_btn.setFixedHeight(40)
        self.mode_btn.clicked.connect(self.toggle_mode)

        self.btn_library = QPushButton("PDF Library")
        self.btn_library.setObjectName("Primary")
        self.btn_library.setFixedHeight(40)

        self.btn_controls = QPushButton("PDF Controls")
        self.btn_controls.setFixedHeight(40)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setFixedHeight(40)

        self.user_lbl = QLabel(f"User: {self.user_name} ✅")
        self.user_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.user_lbl.setFont(QFont("Segoe UI", 11, QFont.DemiBold))

        top.addWidget(self.title_lbl, 2)
        top.addWidget(self.mode_btn, 0)
        top.addWidget(self.btn_library, 0)
        top.addWidget(self.btn_controls, 0)
        top.addWidget(self.btn_logout, 0)
        top.addWidget(self.user_lbl, 2)

        # -----------------------
        # Center
        # -----------------------
        center = QFrame()
        center_layout = QHBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)

        self.content_area = QFrame()
        self.content_area.setObjectName("Panel")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        self.pdf_viewer = PDFViewer()
        content_layout.addWidget(self.pdf_viewer, 1)

        right_panel = QFrame()
        right_panel.setObjectName("Panel")
        rp = QVBoxLayout(right_panel)
        rp.setContentsMargins(12, 12, 12, 12)
        rp.setSpacing(10)

        cam_title = QLabel("Camera Preview")
        cam_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        rp.addWidget(cam_title)

        self.camera_preview = CameraPreview()
        rp.addWidget(self.camera_preview, 1)

        voice_title = QLabel("Voice")
        voice_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        rp.addWidget(voice_title)

        self.voice_indicator = VoiceIndicator()
        rp.addWidget(self.voice_indicator, 0)

        # PDF gets most space
        center_layout.addWidget(self.content_area, 10)
        center_layout.addWidget(right_panel, 4)

        # -----------------------
        # Bottom bar
        # -----------------------
        self.bottom_bar = QFrame()
        self.bottom_bar.setObjectName("BottomBar")
        bot = QHBoxLayout(self.bottom_bar)
        bot.setContentsMargins(16, 10, 16, 10)

        self.status_lbl = QLabel("Status: Ready")
        self.status_lbl.setObjectName("Subtle")
        self.gesture_lbl = QLabel("Gesture: -")
        self.gesture_lbl.setObjectName("Subtle")
        self.safety_lbl = QLabel("Safety: Enabled")
        self.safety_lbl.setObjectName("Subtle")
        self.conf_lbl = QLabel("Confirmation: -")
        self.conf_lbl.setObjectName("Subtle")

        bot.addWidget(self.status_lbl, 3)
        bot.addWidget(self.gesture_lbl, 1)
        bot.addWidget(self.safety_lbl, 1)
        bot.addWidget(self.conf_lbl, 1)

        # Overlay
        self.overlay = ConfirmationOverlay(parent=self.centralWidget())
        self.overlay.hide()

        root_layout.addWidget(self.top_bar, 0)
        root_layout.addWidget(center, 1)
        root_layout.addWidget(self.bottom_bar, 0)

        # -----------------------
        # Buttons
        # -----------------------
        self.btn_library.clicked.connect(self.pdf_viewer.open_library_dialog)
        self.btn_controls.clicked.connect(self.show_controls_hint)

        # -----------------------
        # Camera
        # -----------------------
        self.cam = CameraWorker(cam_index=0, model_path="models/hand_landmarker.task", detect_fps=12)
        self.cam.frame_signal.connect(self.on_frame)
        self.cam.landmarks_signal.connect(self.on_landmarks)
        self.cam.start()

        # -----------------------
        # Voice
        # -----------------------
        self.voice = VoiceWorker(model_path="assets/vosk-model-small-en-us-0.15")
        self.voice.partial_signal.connect(self.on_voice_partial)
        self.voice.command_signal.connect(self.on_voice_command)
        self.voice.active_signal.connect(self.voice_indicator.set_active)
        self.voice.start()

    def show_controls_hint(self):
        self.status_lbl.setText("Status: Controls → Voice or Gestures (zoom/scroll/pages). Library button opens multi-upload list.")

    # -----------------------
    # Camera / Mode
    # -----------------------
    @Slot(object)
    def on_frame(self, frame_bgr):
        self.camera_preview.update_frame(frame_bgr)

    @Slot()
    def toggle_mode(self):
        if self.mode == AppMode.SURGICAL:
            self.mode = AppMode.WARD
            self.mode_btn.setText("Mode: WARD")
        else:
            self.mode = AppMode.SURGICAL
            self.mode_btn.setText("Mode: SURGICAL")

        self.gesture_engine.set_mode(self.mode)
        self.safety.set_mode(self.mode)

    # -----------------------
    # Gestures
    # -----------------------
    @Slot(object)
    def on_landmarks(self, lm_data):
        gesture = self.gesture_engine.detect(lm_data)
        if not gesture:
            return

        self.gesture_lbl.setText(f"Gesture: {gesture}")
        decision = self.safety.evaluate(gesture)
        self.conf_lbl.setText(f"Confirmation: {decision.state}")

        if decision.state != "APPROVED":
            return

        # Thumbs gestures
        if gesture == "SWIPE_RIGHT":
            self.status_lbl.setText("Status: Next Page (👍)")
            self.pdf_viewer.next_page()
            return
        if gesture == "SWIPE_LEFT":
            self.status_lbl.setText("Status: Previous Page (👎)")
            self.pdf_viewer.prev_page()
            return

        # Simple gestures
        if gesture == "SCROLL_DOWN":
            self.status_lbl.setText("Status: Scroll Down")
            self.pdf_viewer.scroll_down()
            return
        if gesture == "SCROLL_UP":
            self.status_lbl.setText("Status: Scroll Up")
            self.pdf_viewer.scroll_up()
            return
        if gesture == "ZOOM_IN":
            self.status_lbl.setText("Status: Zoom In")
            self.pdf_viewer.zoom_in()
            return
        if gesture == "ZOOM_OUT":
            self.status_lbl.setText("Status: Zoom Out")
            self.pdf_viewer.zoom_out()
            return

        self.executor.execute_gesture(gesture, mode=self.mode)

    # -----------------------
    # Voice
    # -----------------------
    @Slot(str)
    def on_voice_partial(self, text):
        self.voice_indicator.set_text(text)

    @Slot(str)
    def on_voice_command(self, cmd):
        if cmd == "OPEN_PDF":
            self.status_lbl.setText("Status: Open Library (voice)")
            self.pdf_viewer.open_library_dialog()
            return
        if cmd == "NEXT_PAGE":
            self.status_lbl.setText("Status: Next Page (voice)")
            self.pdf_viewer.next_page()
            return
        if cmd == "PREV_PAGE":
            self.status_lbl.setText("Status: Previous Page (voice)")
            self.pdf_viewer.prev_page()
            return
        if cmd == "ZOOM_IN":
            self.status_lbl.setText("Status: Zoom In (voice)")
            self.pdf_viewer.zoom_in()
            return
        if cmd == "ZOOM_OUT":
            self.status_lbl.setText("Status: Zoom Out (voice)")
            self.pdf_viewer.zoom_out()
            return
        if cmd == "RESET_ZOOM":
            self.status_lbl.setText("Status: Reset Zoom (voice)")
            self.pdf_viewer.reset_zoom()
            return
        if cmd == "SCROLL_UP":
            self.status_lbl.setText("Status: Scroll Up (voice)")
            self.pdf_viewer.scroll_up()
            return
        if cmd == "SCROLL_DOWN":
            self.status_lbl.setText("Status: Scroll Down (voice)")
            self.pdf_viewer.scroll_down()
            return
        if cmd == "SCROLL_LEFT":
            self.status_lbl.setText("Status: Scroll Left (voice)")
            self.pdf_viewer.scroll_left()
            return
        if cmd == "SCROLL_RIGHT":
            self.status_lbl.setText("Status: Scroll Right (voice)")
            self.pdf_viewer.scroll_right()
            return

    def closeEvent(self, event):
        try:
            if hasattr(self, "cam"):
                self.cam.stop()
                self.cam.wait(2000)
        except Exception:
            pass
        try:
            if hasattr(self, "voice"):
                self.voice.stop()
                self.voice.wait(2000)
        except Exception:
            pass
        super().closeEvent(event)
