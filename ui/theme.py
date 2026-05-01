def app_stylesheet() -> str:
    """
    Premium dark medical UI:
    - deep slate background
    - soft card surfaces
    - crisp text
    - subtle blue accent
    """
    return """
    QMainWindow {
        background: #0b1220;
        color: #e7eefc;
        font-family: "Segoe UI";
    }

    /* Surfaces */
    #TopBar, #BottomBar, #Card, #Panel {
        background: #0f1b2d;
        border: 1px solid #1f3352;
        border-radius: 18px;
    }

    /* Titles */
    QLabel#AppTitle {
        color: #eaf2ff;
        font-size: 20px;
        font-weight: 900;
        letter-spacing: 0.6px;
    }
    QLabel#Subtle {
        color: #b8c7e6;
        font-size: 12px;
        font-weight: 700;
    }

    QLabel {
        color: #dbe7ff;
        font-size: 12px;
        font-weight: 700;
    }

    /* Buttons */
    QPushButton, QToolButton {
        background: #152a46;
        border: 1px solid #2a4b7a;
        color: #eaf2ff;
        padding: 10px 14px;
        border-radius: 14px;
        font-weight: 900;
        font-size: 12px;
    }
    QPushButton:hover, QToolButton:hover {
        background: #183253;
        border: 1px solid #3b6fb3;
    }
    QPushButton:pressed, QToolButton:pressed {
        background: #10243c;
    }

    /* “Primary” button look */
    QPushButton#Primary {
        background: #1f6feb;
        border: 1px solid #3b82f6;
        color: #ffffff;
    }
    QPushButton#Primary:hover {
        background: #2b79f0;
    }

    /* Inputs */
    QLineEdit {
        background: #0c1728;
        border: 1px solid #223a5d;
        color: #eaf2ff;
        padding: 10px 12px;
        border-radius: 14px;
        font-weight: 800;
    }
    QLineEdit:focus {
        border: 1px solid #3b82f6;
    }

    /* Combo/List widgets */
    QComboBox, QListWidget {
        background: #0c1728;
        border: 1px solid #223a5d;
        color: #eaf2ff;
        border-radius: 14px;
        padding: 8px 10px;
        font-weight: 800;
    }
    QListWidget::item {
        padding: 10px 10px;
        border-radius: 12px;
    }
    QListWidget::item:selected {
        background: #1f6feb;
        color: #ffffff;
    }

    /* Menu */
    QMenu {
        background: #0f1b2d;
        border: 1px solid #223a5d;
        border-radius: 14px;
        padding: 8px;
    }
    QMenu::item {
        padding: 10px 14px;
        border-radius: 12px;
        color: #eaf2ff;
        font-weight: 900;
    }
    QMenu::item:selected {
        background: #152a46;
        border: 1px solid #2a4b7a;
    }

    /* Scroll area */
    QScrollArea {
        border: none;
    }
    """
