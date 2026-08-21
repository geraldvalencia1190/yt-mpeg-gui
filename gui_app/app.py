import os
import sys
import subprocess
import yt_dlp
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QStatusBar, QFrame, QPushButton, QMenuBar,
    QMenu, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap

from gui_app.settings_manager import SettingsManager
from gui_app.styles import get_app_stylesheet
from gui_app.ffmpeg_finder import find_ffmpeg_binary, get_ffmpeg_version
from gui_app.updater import UpdateDialog, CheckUpdatesWorker
from gui_app.assets_manager import get_app_icon, get_icon, get_logo_pixmap
from gui_app.widgets.downloader_tab import DownloaderTab
from gui_app.widgets.queue_tab import QueueTab
from gui_app.widgets.settings_tab import SettingsTab
from gui_app.widgets.history_tab import HistoryTab
from gui_app.widgets.logs_tab import LogsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_mgr = SettingsManager()
        self.setWindowTitle("YT-DLP & FFmpeg GUI Studio")
        self.setWindowIcon(get_app_icon())
        self.setMinimumSize(980, 680)
        self.resize(1100, 740)

        self.init_menu_bar()
        self.init_ui()
        self.apply_theme()
        self.log_startup_info()
        self.check_startup_updates()

    def init_menu_bar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        act_open_folder = QAction(get_icon("folder", "#94a3b8"), "Open Download Folder", self)
        act_open_folder.triggered.connect(self.open_download_folder)
        file_menu.addAction(act_open_folder)

        act_clear_hist = QAction(get_icon("trash", "#94a3b8"), "Clear History", self)
        act_clear_hist.triggered.connect(self.clear_history)
        file_menu.addAction(act_clear_hist)

        file_menu.addSeparator()
        act_exit = QAction(get_icon("cancel", "#94a3b8"), "Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        act_update_engines = QAction(get_icon("refresh", "#38bdf8"), "Update yt-dlp & FFmpeg Engines...", self)
        act_update_engines.triggered.connect(self.open_updater_dialog)
        tools_menu.addAction(act_update_engines)

        act_batch = QAction(get_icon("queue", "#94a3b8"), "Open Batch Queue", self)
        act_batch.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        tools_menu.addAction(act_batch)

        act_settings = QAction(get_icon("settings", "#94a3b8"), "Application Preferences", self)
        act_settings.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        tools_menu.addAction(act_settings)

        # View Menu
        view_menu = menubar.addMenu("View")
        act_v_down = QAction(get_icon("download", "#94a3b8"), "Downloader", self)
        act_v_down.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(act_v_down)

        act_v_queue = QAction(get_icon("queue", "#94a3b8"), "Batch Queue", self)
        act_v_queue.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(act_v_queue)

        act_v_hist = QAction(get_icon("history", "#94a3b8"), "History", self)
        act_v_hist.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(act_v_hist)

        act_v_logs = QAction(get_icon("logs", "#94a3b8"), "Logs & Diagnostics", self)
        act_v_logs.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        view_menu.addAction(act_v_logs)

        # Help Menu
        help_menu = menubar.addMenu("Help")
        act_check_up = QAction(get_icon("refresh", "#94a3b8"), "Check for Engine Updates...", self)
        act_check_up.triggered.connect(self.open_updater_dialog)
        help_menu.addAction(act_check_up)

        help_menu.addSeparator()
        act_about = QAction("About YT-DLP & FFmpeg GUI Studio", self)
        act_about.triggered.connect(self.show_about_dialog)
        help_menu.addAction(act_about)

        # Right-aligned badges in menu bar
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 10, 0)
        corner_layout.setSpacing(10)

        ytdlp_ver = getattr(yt_dlp, "__version__", None) or getattr(getattr(yt_dlp, "version", None), "__version__", "2026.08.19")
        self.badge_ytdlp = QLabel(f"yt-dlp v{ytdlp_ver}")
        self.badge_ytdlp.setObjectName("badgeVersion")
        self.badge_ytdlp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.badge_ytdlp.mousePressEvent = lambda e: self.open_updater_dialog()

        self.badge_ffmpeg = QLabel("FFmpeg: Checking...")
        self.badge_ffmpeg.setObjectName("badgeFfmpegReady")
        self.badge_ffmpeg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.badge_ffmpeg.mousePressEvent = lambda e: self.open_updater_dialog()

        corner_layout.addWidget(self.badge_ytdlp)
        corner_layout.addWidget(self.badge_ffmpeg)
        menubar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

        self.update_ffmpeg_badge()

    def init_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setIconSize(QSize(18, 18))

        # Instantiate Tabs
        self.tab_downloader = DownloaderTab(self.settings_mgr)
        self.tab_queue = QueueTab(self.settings_mgr)
        self.tab_history = HistoryTab(self.settings_mgr)
        self.tab_settings = SettingsTab(self.settings_mgr)
        self.tab_logs = LogsTab()

        # Add Tabs with Crisp Vector Assets
        self.tabs.addTab(self.tab_downloader, get_icon("download", "#38bdf8"), "Downloader")
        self.tabs.addTab(self.tab_queue, get_icon("queue", "#a78bfa"), "Batch Queue")
        self.tabs.addTab(self.tab_history, get_icon("history", "#34d399"), "History")
        self.tabs.addTab(self.tab_settings, get_icon("settings", "#94a3b8"), "Settings")
        self.tabs.addTab(self.tab_logs, get_icon("logs", "#fbbf24"), "Logs / Diagnostics")

        # Inter-tab Connections
        self.tab_downloader.add_to_queue_signal.connect(self.on_item_queued)
        self.tab_downloader.log_signal.connect(self.tab_logs.append_log)
        self.tab_downloader.download_finished_signal.connect(self.on_download_completed)
        self.tab_downloader.open_settings_signal.connect(lambda: self.tabs.setCurrentIndex(3))

        self.tab_queue.log_signal.connect(self.tab_logs.append_log)
        self.tab_queue.download_finished_signal.connect(self.on_download_completed)

        self.tab_settings.theme_changed_signal.connect(self.apply_theme)
        self.tab_settings.settings_saved_signal.connect(self.update_ffmpeg_badge)

        main_layout.addWidget(self.tabs, 1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_text = QLabel("Ready.")
        self.status_bar.addWidget(self.lbl_status_text, 1)

        # Total Progress widget in status bar
        total_prog_widget = QWidget()
        total_layout = QHBoxLayout(total_prog_widget)
        total_layout.setContentsMargins(0, 0, 8, 0)
        total_layout.setSpacing(6)

        lbl_total = QLabel("Total Progress:")
        lbl_total.setStyleSheet("color: #888888; font-size: 11px;")
        
        self.status_prog_bar = QProgressBar()
        self.status_prog_bar.setRange(0, 100)
        self.status_prog_bar.setValue(0)
        self.status_prog_bar.setFixedSize(100, 12)
        self.status_prog_bar.setTextVisible(False)

        self.lbl_total_percent = QLabel("0.0%")
        self.lbl_total_percent.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: 600;")

        total_layout.addWidget(lbl_total)
        total_layout.addWidget(self.status_prog_bar)
        total_layout.addWidget(self.lbl_total_percent)

        self.status_bar.addPermanentWidget(total_prog_widget)

    def on_item_queued(self, task: dict):
        self.tab_queue.add_task(task)
        self.tabs.setCurrentIndex(1)

    def update_ffmpeg_badge(self):
        custom = self.settings_mgr.get("custom_ffmpeg_path", "")
        path = find_ffmpeg_binary(custom)
        if path:
            self.badge_ffmpeg.setText("FFmpeg: Ready (Integrated)")
            self.badge_ffmpeg.setObjectName("badgeFfmpegReady")
        else:
            self.badge_ffmpeg.setText("FFmpeg: Not Found")
            self.badge_ffmpeg.setObjectName("badgeFfmpegMissing")
        self.badge_ffmpeg.style().unpolish(self.badge_ffmpeg)
        self.badge_ffmpeg.style().polish(self.badge_ffmpeg)

    def open_updater_dialog(self):
        dialog = UpdateDialog(self.settings_mgr, self)
        dialog.engines_updated.connect(self.on_engines_updated)
        dialog.exec()

    def on_engines_updated(self):
        self.update_ffmpeg_badge()
        self.tab_settings.check_ffmpeg_status()
        self.tab_logs.append_log("SUCCESS", "Engines updated successfully from GitHub.")

    def check_startup_updates(self):
        if self.settings_mgr.get("check_updates_startup", True):
            self.startup_check_worker = CheckUpdatesWorker()
            self.startup_check_worker.check_finished.connect(self.on_startup_check_finished)
            self.startup_check_worker.start()

    def on_startup_check_finished(self, info: dict):
        if info.get("ytdlp_update_needed"):
            self.tab_logs.append_log("INFO", f"Newer yt-dlp available: v{info.get('ytdlp_latest')}")
            self.badge_ytdlp.setText(f"yt-dlp v{info.get('ytdlp_current')} (Update Available)")
            self.badge_ytdlp.setStyleSheet("background-color: #1e3a5f; color: #38bdf8; font-weight: 700; border: 1px solid #0284c7; padding: 3px 8px; border-radius: 3px;")

    def apply_theme(self, theme_name: str = None):
        stylesheet = get_app_stylesheet("cyan")
        self.setStyleSheet(stylesheet)

    def open_download_folder(self):
        folder = self.settings_mgr.get("download_dir")
        if folder and os.path.isdir(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder])

    def clear_history(self):
        self.settings_mgr.clear_history()
        self.tab_history.load_history_data()

    def show_about_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About YT-DLP & FFmpeg GUI Studio")
        msg.setIconPixmap(get_logo_pixmap(64, 64))
        msg.setText("<h3>YT-DLP & FFmpeg GUI Studio</h3>")
        msg.setInformativeText(
            "A fast, modern universal desktop media downloader and processor.<br>"
            "Built with Python 3, PySide6, yt-dlp, and FFmpeg.<br><br>"
            "<b>GitHub:</b> <a href='https://github.com/hazynyx/yt-mpeg-gui'>https://github.com/hazynyx/yt-mpeg-gui</a>"
        )
        msg.exec()

    def on_download_completed(self, result: dict):
        self.tab_history.load_history_data()
        self.tab_logs.append_log("SUCCESS", f"Download finished: {result.get('title')}")
        self.lbl_status_text.setText(f"Completed: {result.get('title', 'Media')}")
        self.status_prog_bar.setValue(100)
        self.lbl_total_percent.setText("100.0%")

    def log_startup_info(self):
        self.tab_logs.append_log("INFO", "Starting YT-DLP & FFmpeg GUI Studio...")
        ytdlp_ver = getattr(yt_dlp, "__version__", None) or getattr(getattr(yt_dlp, "version", None), "__version__", "unknown")
        self.tab_logs.append_log("INFO", f"yt-dlp version: {ytdlp_ver}")
        ffmpeg_p = find_ffmpeg_binary(self.settings_mgr.get("custom_ffmpeg_path"))
        if ffmpeg_p:
            ok, ver = get_ffmpeg_version(ffmpeg_p)
            self.tab_logs.append_log("INFO", f"FFmpeg located: {ffmpeg_p}")
            self.tab_logs.append_log("INFO", f"FFmpeg version info: {ver}")
        else:
            self.tab_logs.append_log("WARNING", "FFmpeg not detected!")

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setWindowIcon(get_app_icon())
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
