"""
Dark Industrial & Modern Design System matching classic media downloader UI
"""

def get_app_stylesheet(accent: str = "cyan") -> str:
    return """
    * {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
        color: #e2e8f0;
        font-size: 12px;
    }

    QMainWindow, QDialog {
        background-color: #141414;
    }

    QWidget#centralWidget {
        background-color: #141414;
    }

    /* Scroll Area */
    QScrollArea {
        background-color: transparent;
        border: none;
    }

    QWidget#scrollContent {
        background-color: transparent;
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #111111;
        color: #cccccc;
        border-bottom: 1px solid #282828;
        padding: 2px 6px;
    }

    QMenuBar::item {
        background: transparent;
        padding: 4px 10px;
        border-radius: 3px;
    }

    QMenuBar::item:selected {
        background-color: #252525;
        color: #ffffff;
    }

    QMenu {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 4px;
    }

    QMenu::item {
        padding: 6px 20px;
        border-radius: 3px;
    }

    QMenu::item:selected {
        background-color: #2563eb;
        color: #ffffff;
    }

    /* Global ScrollBars */
    QScrollBar:vertical {
        background: #111111;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #333333;
        min-height: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #4f4f4f;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background: #111111;
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background: #333333;
        min-width: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #4f4f4f;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #282828;
        background-color: #141414;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #111111;
        color: #888888;
        padding: 8px 18px;
        margin-right: 2px;
        border: 1px solid #282828;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }

    QTabBar::tab:hover {
        background-color: #222222;
        color: #ffffff;
    }

    QTabBar::tab:selected {
        background-color: #181818;
        color: #ffffff;
        border: 1px solid #383838;
        border-bottom: 2px solid #181818;
    }

    /* Group Boxes */
    QGroupBox {
        background-color: #181818;
        border: 1px solid #2d2d2d;
        border-radius: 4px;
        margin-top: 10px;
        padding: 12px 10px 10px 10px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        top: 2px;
        padding: 0 6px;
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        background-color: #181818;
    }

    /* Text Inputs */
    QLineEdit, QPlainTextEdit, QTextEdit {
        background-color: #101010;
        border: 1px solid #333333;
        border-radius: 3px;
        padding: 4px 8px;
        color: #f1f5f9;
        font-size: 12px;
        min-height: 20px;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {
        border: 1px solid #3b82f6;
        background-color: #121212;
    }

    QLineEdit:disabled, QPlainTextEdit:disabled {
        background-color: #141414;
        color: #555555;
        border: 1px solid #222222;
    }

    /* Combo Boxes */
    QComboBox {
        background-color: #101010;
        border: 1px solid #333333;
        border-radius: 3px;
        padding: 4px 8px;
        color: #f1f5f9;
        min-height: 20px;
    }

    QComboBox:hover {
        border: 1px solid #4a4a4a;
    }

    QComboBox:focus {
        border: 1px solid #3b82f6;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 22px;
        border-left-width: 0px;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #888888;
        margin-right: 6px;
    }

    QComboBox QAbstractItemView {
        background-color: #181818;
        border: 1px solid #333333;
        color: #f1f5f9;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
        padding: 2px;
        outline: none;
    }

    /* SpinBoxes */
    QSpinBox, QDoubleSpinBox {
        background-color: #101010;
        border: 1px solid #333333;
        border-radius: 3px;
        padding: 4px 6px;
        color: #f1f5f9;
        min-height: 20px;
    }

    /* Buttons */
    QPushButton {
        background-color: #242424;
        border: 1px solid #383838;
        border-radius: 3px;
        padding: 5px 14px;
        color: #e2e8f0;
        font-weight: 600;
        font-size: 12px;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #303030;
        border-color: #4a4a4a;
        color: #ffffff;
    }

    QPushButton:pressed {
        background-color: #1a1a1a;
    }

    QPushButton:disabled {
        background-color: #181818;
        color: #444444;
        border-color: #242424;
    }

    /* Start / Download Button (Green) */
    QPushButton#btnStartDownload {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #236836, stop:1 #184c25);
        border: 1px solid #2e7d32;
        color: #ffffff;
        font-weight: 700;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
        min-height: 24px;
    }

    QPushButton#btnStartDownload:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2e8344, stop:1 #1e5c2e);
        border-color: #388e3c;
    }

    QPushButton#btnStartDownload:disabled {
        background: #18281c;
        border-color: #1e3324;
        color: #44664c;
    }

    /* Pause Button (Amber/Orange) */
    QPushButton#btnPauseAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #854d0e, stop:1 #5f3408);
        border: 1px solid #a16207;
        color: #ffffff;
        font-weight: 700;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
        min-height: 24px;
    }

    QPushButton#btnPauseAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a16207, stop:1 #713f12);
        border-color: #ca8a04;
    }

    QPushButton#btnPauseAction:disabled {
        background: #241a10;
        border-color: #2d2014;
        color: #55402d;
    }

    /* Resume Button (Sky/Cyan) */
    QPushButton#btnResumeAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1);
        border: 1px solid #0ea5e9;
        color: #ffffff;
        font-weight: 700;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
        min-height: 24px;
    }

    QPushButton#btnResumeAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0396e6, stop:1 #0284c7);
        border-color: #38bdf8;
    }

    /* Add to Queue Button */
    QPushButton#btnQueueAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d333b, stop:1 #20242a);
        border: 1px solid #3e4652;
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
        min-height: 24px;
    }

    QPushButton#btnQueueAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38404a, stop:1 #282e36);
        border-color: #4f5968;
    }

    /* Cancel Button (Red) */
    QPushButton#btnCancelAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b2424, stop:1 #4a1818);
        border: 1px solid #7d2e2e;
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
        min-height: 24px;
    }

    QPushButton#btnCancelAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #802c2c, stop:1 #591e1e);
        border-color: #993838;
    }

    QPushButton#btnCancelAction:disabled {
        background: #241414;
        border-color: #2d1818;
        color: #4d2828;
    }

    /* Checkboxes & Radio */
    QCheckBox, QRadioButton {
        spacing: 6px;
        color: #cbd5e1;
        font-size: 12px;
        min-height: 20px;
    }

    QCheckBox::indicator, QRadioButton::indicator {
        width: 14px;
        height: 14px;
        background-color: #101010;
        border: 1px solid #383838;
        border-radius: 2px;
    }

    QRadioButton::indicator {
        border-radius: 7px;
    }

    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #3b82f6;
    }

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #2563eb;
        border-color: #3b82f6;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #101010;
        border: 1px solid #2d2d2d;
        border-radius: 2px;
        height: 18px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
        font-size: 11px;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
        border-radius: 1px;
    }

    /* Status Badges in Header */
    QLabel#badgeVersion {
        background-color: #1c1c1c;
        color: #888888;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 500;
        border: 1px solid #2d2d2d;
    }

    QLabel#badgeFfmpegReady {
        color: #22c55e;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 6px;
    }

    QLabel#badgeFfmpegMissing {
        color: #ef4444;
        font-weight: 600;
        font-size: 11px;
        padding: 3px 6px;
    }

    /* Key Value Labels in Section 2 */
    QLabel#infoKey {
        color: #888888;
        font-size: 12px;
        font-weight: 500;
        min-height: 18px;
    }

    QLabel#infoVal {
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 600;
        min-height: 18px;
    }

    QLabel#infoAvailable {
        color: #22c55e;
        font-size: 12px;
        font-weight: 700;
        min-height: 18px;
    }

    /* Table Widget */
    QTableWidget {
        background-color: #101010;
        border: 1px solid #282828;
        gridline-color: #1a1a1a;
        color: #e2e8f0;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }

    QHeaderView::section {
        background-color: #181818;
        color: #999999;
        padding: 6px 10px;
        font-weight: 600;
        border: none;
        border-bottom: 1px solid #282828;
    }

    /* Status Bar */
    QStatusBar {
        background-color: #101010;
        color: #888888;
        border-top: 1px solid #242424;
        font-size: 11px;
        padding: 2px 8px;
    }
    """
