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
        background-color: #1a1a1a;
    }

    QWidget#centralWidget {
        background-color: #1a1a1a;
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #141414;
        color: #cccccc;
        border-bottom: 1px solid #2d2d2d;
        padding: 2px 6px;
    }

    QMenuBar::item {
        background: transparent;
        padding: 4px 10px;
        border-radius: 4px;
    }

    QMenuBar::item:selected {
        background-color: #2a2a2a;
        color: #ffffff;
    }

    QMenu {
        background-color: #202020;
        border: 1px solid #3d3d3d;
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
        background: #141414;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #3a3a3a;
        min-height: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #555555;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background: #141414;
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background: #3a3a3a;
        min-width: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #555555;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #2e2e2e;
        background-color: #1a1a1a;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #151515;
        color: #9e9e9e;
        padding: 7px 16px;
        margin-right: 2px;
        border: 1px solid #2e2e2e;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }

    QTabBar::tab:hover {
        background-color: #242424;
        color: #ffffff;
    }

    QTabBar::tab:selected {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #3e3e3e;
        border-bottom: 2px solid #1a1a1a;
    }

    /* Group Boxes */
    QGroupBox {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 4px;
        margin-top: 10px;
        padding: 10px 8px 8px 8px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        top: 2px;
        padding: 0 4px;
        color: #e5e7eb;
        font-size: 12px;
        font-weight: 700;
        background-color: #1a1a1a;
    }

    /* Text Inputs */
    QLineEdit, QPlainTextEdit, QTextEdit {
        background-color: #121212;
        border: 1px solid #3d3d3d;
        border-radius: 3px;
        padding: 5px 8px;
        color: #f1f5f9;
        font-size: 12px;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {
        border: 1px solid #3b82f6;
        background-color: #151515;
    }

    QLineEdit:disabled, QPlainTextEdit:disabled {
        background-color: #161616;
        color: #555555;
        border: 1px solid #2a2a2a;
    }

    /* Combo Boxes */
    QComboBox {
        background-color: #161616;
        border: 1px solid #3d3d3d;
        border-radius: 3px;
        padding: 4px 8px;
        color: #f1f5f9;
        min-height: 20px;
    }

    QComboBox:hover {
        border: 1px solid #555555;
    }

    QComboBox:focus {
        border: 1px solid #3b82f6;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
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
        background-color: #1e1e1e;
        border: 1px solid #3d3d3d;
        color: #f1f5f9;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
        padding: 2px;
        outline: none;
    }

    /* SpinBoxes */
    QSpinBox, QDoubleSpinBox {
        background-color: #121212;
        border: 1px solid #3d3d3d;
        border-radius: 3px;
        padding: 4px 6px;
        color: #f1f5f9;
    }

    /* Buttons */
    QPushButton {
        background-color: #262626;
        border: 1px solid #3d3d3d;
        border-radius: 3px;
        padding: 5px 14px;
        color: #e2e8f0;
        font-weight: 600;
        font-size: 12px;
    }

    QPushButton:hover {
        background-color: #333333;
        border-color: #555555;
        color: #ffffff;
    }

    QPushButton:pressed {
        background-color: #1c1c1c;
    }

    QPushButton:disabled {
        background-color: #181818;
        color: #444444;
        border-color: #262626;
    }

    /* Start / Download Button (Green) */
    QPushButton#btnStartDownload {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b6e3f, stop:1 #1e522d);
        border: 1px solid #388e3c;
        color: #ffffff;
        font-weight: 700;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
    }

    QPushButton#btnStartDownload:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34834b, stop:1 #246337);
        border-color: #4caf50;
    }

    QPushButton#btnStartDownload:disabled {
        background: #1e3324;
        border-color: #25422c;
        color: #55775e;
    }

    /* Add to Queue Button */
    QPushButton#btnQueueAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333942, stop:1 #242930);
        border: 1px solid #47505d;
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
    }

    QPushButton#btnQueueAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d444f, stop:1 #2c323b);
        border-color: #5c6778;
    }

    /* Cancel Button (Red) */
    QPushButton#btnCancelAction {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #752828, stop:1 #521c1c);
        border: 1px solid #8e3838;
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        border-radius: 3px;
        padding: 8px 16px;
    }

    QPushButton#btnCancelAction:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8a3030, stop:1 #612222);
        border-color: #ad4747;
    }

    QPushButton#btnCancelAction:disabled {
        background: #2b1818;
        border-color: #382020;
        color: #5c3b3b;
    }

    /* Checkboxes & Radio */
    QCheckBox, QRadioButton {
        spacing: 6px;
        color: #cbd5e1;
        font-size: 12px;
    }

    QCheckBox::indicator, QRadioButton::indicator {
        width: 14px;
        height: 14px;
        background-color: #121212;
        border: 1px solid #444444;
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
        background-color: #121212;
        border: 1px solid #333333;
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
        background-color: #222222;
        color: #888888;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 500;
        border: 1px solid #333333;
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
    }

    QLabel#infoVal {
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 600;
    }

    QLabel#infoAvailable {
        color: #22c55e;
        font-size: 12px;
        font-weight: 700;
    }

    /* Table Widget */
    QTableWidget {
        background-color: #121212;
        border: 1px solid #2e2e2e;
        gridline-color: #1e1e1e;
        color: #e2e8f0;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }

    QHeaderView::section {
        background-color: #1e1e1e;
        color: #aaaaaa;
        padding: 6px 10px;
        font-weight: 600;
        border: none;
        border-bottom: 1px solid #2e2e2e;
    }

    /* Status Bar */
    QStatusBar {
        background-color: #121212;
        color: #9e9e9e;
        border-top: 1px solid #2b2b2b;
        font-size: 11px;
        padding: 2px 8px;
    }
    """
