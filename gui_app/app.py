import os
import sys
import yt_dlp
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QStatusBar, QFrame, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from gui_app.settings_manager import SettingsManager
from gui_app.styles import get_app_stylesheet
from gui_app.ffmpeg_finder import find_ffmpeg_binary, get_ffmpeg_version
from gui_app.widgets.downloader_tab import DownloaderTab
from gui_app.widgets.queue_tab import QueueTab
from gui_app.widgets.settings_tab import SettingsTab
from gui_app.widgets.history_tab import HistoryTab
from gui_app.widgets.logs_tab import LogsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_mgr = SettingsManager()
        self.setWindowTitle("yt-dlp & FFmpeg GUI Studio")
        self.setMinimumSize(960, 680)
        self.resize(1080, 750)

        self.init_ui()
        self.apply_theme()
        self.log_startup_info()

    def init_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header Banner
        header = QFrame()
        header.setObjectName("glassHeader")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(14)

        # Logo / Title
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        app_title = QLabel("⚡ YT-DLP & FFMPEG STUDIO")
        app_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;")
        
        app_sub = QLabel("Universal High-Speed Media Downloader & Media Processor")
        app_sub.setStyleSheet("font-size: 11px; color: #94a3b8;")
        title_box.addWidget(app_title)
        title_box.addWidget(app_sub)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Engine Badges
        ytdlp_ver = getattr(yt_dlp, "__version__", "2024.x")
        self.badge_ytdlp = QLabel(f"yt-dlp v{ytdlp_ver}")
        self.badge_ytdlp.setObjectName("badgePill")

        # FFmpeg Status
        self.badge_ffmpeg = QLabel("FFmpeg: Checking...")
        self.badge_ffmpeg.setObjectName("badgeSuccess")
        self.update_ffmpeg_badge()

        header_layout.addWidget(self.badge_ytdlp)
        header_layout.addWidget(self.badge_ffmpeg)

        main_layout.addWidget(header)

        # 2. Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Instantiate Tabs
        self.tab_downloader = DownloaderTab(self.settings_mgr)
        self.tab_queue = QueueTab(self.settings_mgr)
        self.tab_history = HistoryTab(self.settings_mgr)
        self.tab_settings = SettingsTab(self.settings_mgr)
        self.tab_logs = LogsTab()

        # Add Tabs
        self.tabs.addTab(self.tab_downloader, "🚀 Downloader")
        self.tabs.addTab(self.tab_queue, "📋 Batch Queue")
        self.tabs.addTab(self.tab_history, "📁 History")
        self.tabs.addTab(self.tab_settings, "⚙️ Settings")
        self.tabs.addTab(self.tab_logs, "📜 Logs & Diagnostics")

        # Connect inter-tab signals
        self.tab_downloader.add_to_queue_signal.connect(self.tab_queue.add_task)
        self.tab_downloader.log_signal.connect(self.tab_logs.append_log)
        self.tab_downloader.download_finished_signal.connect(self.on_download_completed)

        self.tab_queue.log_signal.connect(self.tab_logs.append_log)
        self.tab_queue.download_finished_signal.connect(self.on_download_completed)

        self.tab_settings.theme_changed_signal.connect(self.apply_theme)
        self.tab_settings.settings_saved_signal.connect(self.update_ffmpeg_badge)

        main_layout.addWidget(self.tabs, 1)

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #0d131d; color: #94a3b8; border-top: 1px solid #1e293b; padding: 4px;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Paste a link or batch queue to start.")

    def update_ffmpeg_badge(self):
        custom = self.settings_mgr.get("custom_ffmpeg_path", "")
        path = find_ffmpeg_binary(custom)
        if path:
            self.badge_ffmpeg.setText("FFmpeg: Ready (Integrated)")
            self.badge_ffmpeg.setObjectName("badgeSuccess")
        else:
            self.badge_ffmpeg.setText("FFmpeg: Not Found")
            self.badge_ffmpeg.setObjectName("badgeWarning")
        self.badge_ffmpeg.style().unpolish(self.badge_ffmpeg)
        self.badge_ffmpeg.style().polish(self.badge_ffmpeg)

    def apply_theme(self, theme_name: str = None):
        if not theme_name:
            theme_name = self.settings_mgr.get("theme", "dark_cyan")
        
        accent = "cyan"
        if "purple" in theme_name:
            accent = "purple"
        elif "emerald" in theme_name:
            accent = "emerald"

        stylesheet = get_app_stylesheet(accent)
        self.setStyleSheet(stylesheet)

    def on_download_completed(self, result: dict):
        self.tab_history.load_history_data()
        self.tab_logs.append_log("SUCCESS", f"Download finished: {result.get('title')}")
        self.status_bar.showMessage(f"Downloaded: {result.get('title', 'Media')} -> {result.get('file_path')}", 8000)

    def log_startup_info(self):
        self.tab_logs.append_log("INFO", "Starting yt-dlp & FFmpeg Studio...")
        self.tab_logs.append_log("INFO", f"yt-dlp version: {getattr(yt_dlp, '__version__', 'unknown')}")
        ffmpeg_p = find_ffmpeg_binary(self.settings_mgr.get("custom_ffmpeg_path"))
        if ffmpeg_p:
            ok, ver = get_ffmpeg_version(ffmpeg_p)
            self.tab_logs.append_log("INFO", f"FFmpeg located: {ffmpeg_p}")
            self.tab_logs.append_log("INFO", f"FFmpeg version info: {ver}")
        else:
            self.tab_logs.append_log("WARNING", "FFmpeg not detected! Video and audio merge operations may require FFmpeg.")

def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
