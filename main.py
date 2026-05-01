import sys
from PySide6.QtWidgets import QApplication

from ui.auth_window import AuthWindow
from ui.main_window import MainWindow
from ui.theme import app_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(app_stylesheet())

    auth = AuthWindow(cam_index=0)

    def on_authed(name: str):
        auth.close()
        w = MainWindow(user_name=name)
        w.show()
        # keep reference alive
        app._main_window = w

    auth.authenticated.connect(on_authed)
    auth.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
