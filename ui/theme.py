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
        background: #0a1522;
        color: #eaf2ff;
        font-family: "Segoe UI";
    }

    /* Surfaces */
    #TopBar, #BottomBar, #Card, #Panel {
        background: #112031;
        border: 1px solid #1c3a51;
        border-radius: 18px;
    }

    /* Titles */
    QLabel#AppTitle {
        color: #f2f8ff;
        font-size: 20px;
        font-weight: 900;
        letter-spacing: 0.6px;
    }
    QLabel#Subtle {
        color: #bdd0e6;
        font-size: 11px;
        font-weight: 700;
    }

    QLabel {
        color: #dceafe;
        font-size: 12px;
        font-weight: 700;
    }

    /* Buttons */
    QPushButton, QToolButton {
        background: #173049;
        border: 1px solid #2b597f;
        color: #edf5ff;
        padding: 9px 14px;
        border-radius: 14px;
        font-weight: 900;
        font-size: 12px;
    }
    QPushButton:hover, QToolButton:hover {
        background: #1c3a58;
        border: 1px solid #4e86b1;
    }
    QPushButton:pressed, QToolButton:pressed {
        background: #12283c;
    }

    /* “Primary” button look */
    QPushButton#Primary {
        background: #0f8b8d;
        border: 1px solid #26a6a8;
        color: #ffffff;
    }
    QPushButton#Primary:hover {
        background: #13979a;
    }

    /* Inputs */
    QLineEdit {
        background: #0d1c2e;
        border: 1px solid #245070;
        color: #eaf2ff;
        padding: 10px 12px;
        border-radius: 14px;
        font-weight: 800;
    }
    QLineEdit:focus {
        border: 1px solid #26a6a8;
    }

    /* Combo/List widgets */
    QComboBox, QListWidget {
        background: #0d1c2e;
        border: 1px solid #245070;
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
        background: #0f8b8d;
        color: #ffffff;
    }

    /* Menu */
    QMenu {
        background: #112031;
        border: 1px solid #245070;
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
        background: #173049;
        border: 1px solid #2b597f;
    }

    /* Scroll area */
    QScrollArea {
        border: none;
    }

    /* Soft info panel styles */
    QFrame#Card QLabel {
        letter-spacing: 0.2px;
    }
    """
