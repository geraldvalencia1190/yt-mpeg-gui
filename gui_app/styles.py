"""
Modern Glassmorphic Dark Design System for yt-mpeg-gui
"""

def get_app_stylesheet(accent: str = "cyan") -> str:
    accents = {
        "cyan": {
            "primary": "#00d2ff",
            "primary_hover": "#38bdf8",
            "primary_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00b4d8)",
            "primary_gradient_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096c7, stop:1 #48cae4)",
            "accent_glow": "rgba(0, 210, 255, 0.25)",
            "tag_bg": "rgba(0, 210, 255, 0.15)",
            "tag_border": "rgba(0, 210, 255, 0.4)",
        },
        "purple": {
            "primary": "#a855f7",
            "primary_hover": "#c084fc",
            "primary_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7928ca, stop:1 #a855f7)",
            "primary_gradient_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #c084fc)",
            "accent_glow": "rgba(168, 85, 247, 0.25)",
            "tag_bg": "rgba(168, 85, 247, 0.15)",
            "tag_border": "rgba(168, 85, 247, 0.4)",
        },
        "emerald": {
            "primary": "#10b981",
            "primary_hover": "#34d399",
            "primary_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981)",
            "primary_gradient_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399)",
            "accent_glow": "rgba(16, 185, 129, 0.25)",
            "tag_bg": "rgba(16, 185, 129, 0.15)",
            "tag_border": "rgba(16, 185, 129, 0.4)",
        }
    }
    
    theme = accents.get(accent, accents["cyan"])

    return f"""
    * {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
        color: #e2e8f0;
        font-size: 13px;
    }}

    QMainWindow, QDialog {{
        background-color: #0b0f17;
    }}

    QWidget#centralWidget {{
        background-color: #0b0f17;
    }}

    /* Global ScrollBars */
    QScrollBar:vertical {{
        background: #0f141c;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: #334155;
        min-height: 25px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {theme["primary"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: #0f141c;
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: #334155;
        min-width: 25px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {theme["primary"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* Navigation Sidebar / Tabs */
    QTabWidget::pane {{
        border: none;
        background-color: transparent;
    }}

    QTabBar::tab {{
        background-color: #151d2a;
        color: #94a3b8;
        padding: 10px 20px;
        margin-right: 6px;
        margin-bottom: 2px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #1e293b;
        border-bottom: none;
    }}

    QTabBar::tab:hover {{
        background-color: #1e293b;
        color: #f1f5f9;
    }}

    QTabBar::tab:selected {{
        background-color: #1e293b;
        color: {theme["primary"]};
        border-bottom: 3px solid {theme["primary"]};
    }}

    /* Cards / Frames */
    QFrame#cardFrame, QFrame#previewCard, QFrame#progressCard, QFrame#settingsCard {{
        background-color: #131b26;
        border: 1px solid #233044;
        border-radius: 12px;
    }}

    QFrame#glassHeader {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #111827, stop:1 #1e1e38);
        border-bottom: 1px solid #2d3748;
        border-radius: 0px;
    }}

    /* Text Inputs */
    QLineEdit, QPlainTextEdit, QTextEdit {{
        background-color: #0d131d;
        border: 1.5px solid #253347;
        border-radius: 8px;
        padding: 9px 14px;
        color: #f8fafc;
        font-size: 13px;
        selection-background-color: {theme["primary"]};
        selection-color: #0b0f17;
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1.5px solid {theme["primary"]};
        background-color: #0f1724;
    }}

    QLineEdit:disabled, QPlainTextEdit:disabled {{
        background-color: #121822;
        color: #64748b;
        border: 1px solid #1e293b;
    }}

    /* Combo Boxes */
    QComboBox {{
        background-color: #0d131d;
        border: 1.5px solid #253347;
        border-radius: 8px;
        padding: 7px 12px;
        color: #f8fafc;
        font-weight: 500;
        min-height: 22px;
    }}

    QComboBox:hover {{
        border: 1.5px solid #3b82f6;
    }}

    QComboBox:focus {{
        border: 1.5px solid {theme["primary"]};
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left-width: 0px;
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #94a3b8;
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: #131c2b;
        border: 1px solid #2d3f58;
        border-radius: 8px;
        color: #f8fafc;
        selection-background-color: #1e293b;
        selection-color: {theme["primary"]};
        padding: 4px;
        outline: none;
    }}

    /* SpinBoxes */
    QSpinBox, QDoubleSpinBox {{
        background-color: #0d131d;
        border: 1.5px solid #253347;
        border-radius: 8px;
        padding: 6px 10px;
        color: #f8fafc;
    }}

    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1.5px solid {theme["primary"]};
    }}

    /* Buttons */
    QPushButton {{
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 16px;
        color: #f8fafc;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: #273549;
        border-color: #475569;
        color: #ffffff;
    }}

    QPushButton:pressed {{
        background-color: #16202e;
        transform: translateY(1px);
    }}

    QPushButton:disabled {{
        background-color: #131923;
        color: #475569;
        border-color: #1e293b;
    }}

    /* Primary Accent Action Button */
    QPushButton#btnPrimary {{
        background: {theme["primary_gradient"]};
        border: 1px solid {theme["primary"]};
        color: #ffffff;
        font-weight: 700;
        font-size: 14px;
        border-radius: 10px;
        padding: 10px 22px;
    }}

    QPushButton#btnPrimary:hover {{
        background: {theme["primary_gradient_hover"]};
        border: 1px solid #7dd3fc;
    }}

    QPushButton#btnPrimary:pressed {{
        background-color: #0284c7;
    }}

    /* Success Button */
    QPushButton#btnSuccess {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
        border: 1px solid #10b981;
        color: #ffffff;
        font-weight: 700;
        font-size: 13px;
        border-radius: 8px;
        padding: 8px 16px;
    }}

    QPushButton#btnSuccess:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
    }}

    /* Danger / Cancel Button */
    QPushButton#btnDanger {{
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #f87171;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
    }}

    QPushButton#btnDanger:hover {{
        background-color: rgba(239, 68, 68, 0.3);
        border-color: #ef4444;
        color: #ffffff;
    }}

    /* Secondary Action Button */
    QPushButton#btnSecondary {{
        background-color: #172030;
        border: 1px solid #2c3e55;
        color: #94a3b8;
        border-radius: 8px;
        padding: 8px 14px;
    }}

    QPushButton#btnSecondary:hover {{
        background-color: #202b3d;
        color: #f8fafc;
        border-color: #3b82f6;
    }}

    /* Checkboxes & Radio Buttons */
    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: #cbd5e1;
        font-weight: 500;
    }}

    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        background-color: #0d131d;
        border: 1.5px solid #334155;
        border-radius: 5px;
    }}

    QRadioButton::indicator {{
        border-radius: 9px;
    }}

    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border-color: {theme["primary"]};
    }}

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {theme["primary"]};
        border-color: {theme["primary"]};
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: #0d131d;
        border: 1px solid #233044;
        border-radius: 8px;
        height: 16px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
        font-size: 11px;
    }}

    QProgressBar::chunk {{
        background: {theme["primary_gradient"]};
        border-radius: 7px;
    }}

    /* Status Badges */
    QLabel#badgePill {{
        background-color: {theme["tag_bg"]};
        border: 1px solid {theme["tag_border"]};
        color: {theme["primary"]};
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }}

    QLabel#badgeSuccess {{
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }}

    QLabel#badgeWarning {{
        background-color: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* Table Widgets */
    QTableWidget {{
        background-color: #0d131d;
        border: 1px solid #233044;
        border-radius: 10px;
        gridline-color: #1a2332;
        color: #e2e8f0;
        selection-background-color: #1e293b;
        selection-color: {theme["primary"]};
    }}

    QHeaderView::section {{
        background-color: #151e2c;
        color: #94a3b8;
        padding: 8px 12px;
        font-weight: 600;
        border: none;
        border-bottom: 2px solid #233044;
    }}

    /* Labels & Headers */
    QLabel#headingTitle {{
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
    }}

    QLabel#subHeading {{
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
    }}

    QLabel#sectionHeader {{
        font-size: 14px;
        font-weight: 700;
        color: {theme["primary"]};
    }}

    /* Group Box */
    QGroupBox {{
        background-color: #121924;
        border: 1px solid #233044;
        border-radius: 10px;
        margin-top: 14px;
        padding-top: 14px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 6px;
        color: {theme["primary"]};
        font-weight: 700;
    }}

    /* Tooltips */
    QToolTip {{
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid {theme["primary"]};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}
    """
