import cv2
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit
)

from core.face_auth_manager import FaceAuthManager
from ui.theme import app_stylesheet


class AuthWindow(QMainWindow):
    authenticated = Signal(str)  # emits username

    def __init__(self, cam_index=0):
        super().__init__()
        self.setWindowTitle("MedWave Control — Secure Access")
        self.setMinimumSize(980, 620)
        self.setStyleSheet(app_stylesheet())

        self.face_auth = FaceAuthManager(auth_dir="auth_faces")
        self.face_auth.retrain()

        self.cam = cv2.VideoCapture(cam_index)
        self.latest_frame = None

        # signup state
        self.signup_active = False
        self.signup_name = ""
        self.signup_needed = 15
        self.signup_count = 0

        # UI
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        # Left panel
        left = QFrame()
        left.setObjectName("Panel")
        l = QVBoxLayout(left)
        l.setContentsMargins(18, 18, 18, 18)
        l.setSpacing(12)

        title = QLabel("MedWave Control")
        title.setObjectName("AppTitle")

        subtitle = QLabel("Touchless clinical navigation.\nSecure access via Face ID.")
        subtitle.setObjectName("Subtle")

        l.addWidget(title)
        l.addWidget(subtitle)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Signup name (e.g., Dr Hassan)")
        l.addWidget(self.name_input)

        row = QHBoxLayout()
        self.btn_signup = QPushButton("Sign Up")
        self.btn_signup.setObjectName("Primary")
        self.btn_lock = QPushButton("Lock / Reset")
        row.addWidget(self.btn_signup)
        row.addWidget(self.btn_lock)
        l.addLayout(row)

        self.hint = QLabel("Status: Show your face to sign in.")
        self.hint.setObjectName("Subtle")
        l.addWidget(self.hint)

        l.addStretch(1)

        # Right preview panel
        right = QFrame()
        right.setObjectName("Panel")
        r = QVBoxLayout(right)
        r.setContentsMargins(18, 18, 18, 18)
        r.setSpacing(12)

        cam_title = QLabel("Camera Preview")
        cam_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        r.addWidget(cam_title)

        self.preview = QLabel("Starting camera…")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet(
            "background:#0c1728; border:1px solid #223a5d; border-radius:18px; padding:12px; color:#b8c7e6;"
        )
        self.preview.setMinimumHeight(420)
        r.addWidget(self.preview, 1)

        r2 = QLabel("Tip: Keep face centered. Sign in happens automatically.")
        r2.setObjectName("Subtle")
        r.addWidget(r2)

        outer.addWidget(left, 2)
        outer.addWidget(right, 3)

        # signals
        self.btn_signup.clicked.connect(self.start_signup)
        self.btn_lock.clicked.connect(self.reset_lock)

        # timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

        self.auth_timer = QTimer(self)
        self.auth_timer.timeout.connect(self.try_auth)
        self.auth_timer.start(800)

        self.signup_timer = QTimer(self)
        self.signup_timer.timeout.connect(self.signup_tick)

    def reset_lock(self):
        self.signup_active = False
        self.signup_count = 0
        self.hint.setText("Status: Locked. Show your face to sign in.")

    def start_signup(self):
        name = self.name_input.text().strip()
        if not name:
            self.hint.setText("Status: Enter a name first, then Sign Up.")
            return
        if self.latest_frame is None:
            self.hint.setText("Status: Camera not ready yet.")
            return

        self.signup_active = True
        self.signup_name = name
        self.signup_count = 0
        self.hint.setText(f"Status: Signing up {name}… look at camera.")
        self.signup_timer.start(320)

    def signup_tick(self):
        if not self.signup_active or self.latest_frame is None:
            return

        ok = self.face_auth.enroll_from_frame(self.signup_name, self.latest_frame)
        if ok:
            self.signup_count += 1
            self.hint.setText(f"Status: Capturing {self.signup_name}… {self.signup_count}/{self.signup_needed}")

        if self.signup_count >= self.signup_needed:
            self.signup_timer.stop()
            self.signup_active = False
            self.face_auth.retrain()
            self.hint.setText(f"Status: Signup complete ✅ for {self.signup_name}. Now show face to sign in.")

    def tick(self):
        if not self.cam.isOpened():
            return
        ok, frame = self.cam.read()
        if not ok:
            return
        self.latest_frame = frame

        # show preview
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        pm = QPixmap.fromImage(qimg).scaled(
            self.preview.width(), self.preview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview.setPixmap(pm)

    def try_auth(self):
        if self.signup_active:
            return
        if self.latest_frame is None:
            return

        ok, name, conf = self.face_auth.recognize(self.latest_frame, threshold=70)
        if ok:
            self.hint.setText(f"Status: Authenticated ✅ {name}")
            self.auth_timer.stop()  # stop checking once authenticated
            self.authenticated.emit(name)

    def closeEvent(self, event):
        try:
            if self.cam:
                self.cam.release()
        except Exception:
            pass
        super().closeEvent(event)
