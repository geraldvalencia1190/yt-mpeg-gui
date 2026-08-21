import os
import sys
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QComboBox, QCheckBox, QSpinBox, QFileDialog, QMessageBox,
    QScrollArea, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
import yt_dlp

from gui_app.settings_manager import SettingsManager
from gui_app.ffmpeg_finder import find_ffmpeg_binary, find_ffprobe_binary, get_ffmpeg_version
from gui_app.updater import UpdateDialog
from gui_app.assets_manager import get_icon

class SettingsTab(QWidget):
    settings_saved_signal = Signal()
    theme_changed_signal = Signal(str)

    def __init__(self, settings_mgr: SettingsManager):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Scroll Area to comfortably fit all rich settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        # 0. Engine & Backend Updater Card
        grp_updates = QGroupBox("Engine & Backend Updater (yt-dlp & FFmpeg)")
        grid_up = QGridLayout(grp_updates)
        grid_up.setSpacing(10)

        ytdlp_ver = getattr(yt_dlp, "__version__", None) or getattr(getattr(yt_dlp, "version", None), "__version__", "2026.08.19")
        lbl_yt = QLabel(f"Core yt-dlp Engine:  <b>v{ytdlp_ver}</b>")
        lbl_yt.setStyleSheet("color: #38bdf8;")

        self.lbl_ff_info = QLabel("FFmpeg Processor: Checking...")
        self.lbl_ff_info.setStyleSheet("color: #22c55e;")

        self.btn_open_updater = QPushButton("Check & Update Engines from GitHub...")
        self.btn_open_updater.setIcon(get_icon("refresh", "#ffffff"))
        self.btn_open_updater.setObjectName("btnStartDownload")
        self.btn_open_updater.setFixedHeight(34)
        self.btn_open_updater.clicked.connect(self.open_update_dialog)

        self.chk_auto_update = QCheckBox("Check for engine updates on application launch")
        self.chk_auto_update.setChecked(self.settings_mgr.get("check_updates_startup", True))

        grid_up.addWidget(lbl_yt, 0, 0)
        grid_up.addWidget(self.lbl_ff_info, 0, 1)
        grid_up.addWidget(self.btn_open_updater, 1, 0)
        grid_up.addWidget(self.chk_auto_update, 1, 1)

        layout.addWidget(grp_updates)

        # 1. Output & File Naming
        grp_output = QGroupBox("Download & File Naming Settings")
        grid_out = QGridLayout(grp_output)
        grid_out.setSpacing(10)

        grid_out.addWidget(QLabel("Default Download Directory:"), 0, 0)
        self.edit_dir = QLineEdit(self.settings_mgr.get("download_dir"))
        btn_dir = QPushButton("Browse...")
        btn_dir.setIcon(get_icon("folder", "#cbd5e1"))
        btn_dir.setObjectName("btnSecondary")
        btn_dir.clicked.connect(self.browse_download_dir)
        dir_box = QHBoxLayout()
        dir_box.addWidget(self.edit_dir, 1)
        dir_box.addWidget(btn_dir)
        grid_out.addLayout(dir_box, 0, 1)

        grid_out.addWidget(QLabel("Filename Template:"), 1, 0)
        self.edit_template = QLineEdit(self.settings_mgr.get("filename_template"))
        grid_out.addWidget(self.edit_template, 1, 1)

        hint_template = QLabel("Tags: %(title)s, %(uploader)s, %(resolution)s, %(id)s, %(ext)s, %(playlist_index)s")
        hint_template.setStyleSheet("color: #64748b; font-size: 11px;")
        grid_out.addWidget(hint_template, 2, 1)

        layout.addWidget(grp_output)

        # 2. FFmpeg & Media Processing
        grp_ffmpeg = QGroupBox("FFmpeg & Post-Processing Settings")
        grid_ff = QGridLayout(grp_ffmpeg)
        grid_ff.setSpacing(10)

        # Status
        grid_ff.addWidget(QLabel("FFmpeg Detection:"), 0, 0)
        self.lbl_ffmpeg_status = QLabel()
        self.check_ffmpeg_status()
        grid_ff.addWidget(self.lbl_ffmpeg_status, 0, 1)

        grid_ff.addWidget(QLabel("Custom FFmpeg Path:"), 1, 0)
        self.edit_ffmpeg_path = QLineEdit(self.settings_mgr.get("custom_ffmpeg_path"))
        self.edit_ffmpeg_path.setPlaceholderText("Leave blank to use integrated ffmpeg.exe")
        btn_ff_browse = QPushButton("Browse...")
        btn_ff_browse.setIcon(get_icon("folder", "#cbd5e1"))
        btn_ff_browse.setObjectName("btnSecondary")
        btn_ff_browse.clicked.connect(self.browse_ffmpeg_binary)
        ff_box = QHBoxLayout()
        ff_box.addWidget(self.edit_ffmpeg_path, 1)
        ff_box.addWidget(btn_ff_browse)
        grid_ff.addLayout(ff_box, 1, 1)

        # Checkboxes for embed
        self.chk_thumb = QCheckBox("Embed Video Thumbnail directly into media file")
        self.chk_thumb.setChecked(self.settings_mgr.get("embed_thumbnail", True))
        grid_ff.addWidget(self.chk_thumb, 2, 0, 1, 2)

        self.chk_meta = QCheckBox("Embed Video Metadata and Description tags")
        self.chk_meta.setChecked(self.settings_mgr.get("embed_metadata", True))
        grid_ff.addWidget(self.chk_meta, 3, 0, 1, 2)

        self.chk_chapters = QCheckBox("Embed Video Chapters markers")
        self.chk_chapters.setChecked(self.settings_mgr.get("embed_chapters", True))
        grid_ff.addWidget(self.chk_chapters, 4, 0, 1, 2)

        layout.addWidget(grp_ffmpeg)

        # 3. Subtitles & SponsorBlock
        grp_subs = QGroupBox("Subtitles & SponsorBlock")
        grid_sub = QGridLayout(grp_subs)
        grid_sub.setSpacing(10)

        self.chk_embed_sub = QCheckBox("Embed Subtitles into video container")
        self.chk_embed_sub.setChecked(self.settings_mgr.get("embed_subtitles", False))
        grid_sub.addWidget(self.chk_embed_sub, 0, 0)

        self.chk_write_sub = QCheckBox("Write separate external subtitle file (.srt / .vtt)")
        self.chk_write_sub.setChecked(self.settings_mgr.get("write_subtitles", False))
        grid_sub.addWidget(self.chk_write_sub, 0, 1)

        self.chk_auto_sub = QCheckBox("Include Auto-Generated subtitles if manual subs not available")
        self.chk_auto_sub.setChecked(self.settings_mgr.get("auto_subtitles", False))
        grid_sub.addWidget(self.chk_auto_sub, 1, 0, 1, 2)

        grid_sub.addWidget(QLabel("Subtitle Languages (comma-separated, e.g. en, es, fr, all):"), 2, 0)
        self.edit_sub_langs = QLineEdit(self.settings_mgr.get("subtitles_languages", "en"))
        grid_sub.addWidget(self.edit_sub_langs, 2, 1)

        # Sponsorblock
        self.chk_sponsor = QCheckBox("Enable SponsorBlock (Auto-remove sponsor segments)")
        self.chk_sponsor.setChecked(self.settings_mgr.get("sponsorblock_enabled", False))
        grid_sub.addWidget(self.chk_sponsor, 3, 0, 1, 2)

        layout.addWidget(grp_subs)

        # 4. Network, Cookies & Performance
        grp_net = QGroupBox("Network, Authentication & Performance")
        grid_net = QGridLayout(grp_net)
        grid_net.setSpacing(10)

        grid_net.addWidget(QLabel("Browser Cookies Extraction:"), 0, 0)
        self.combo_browser = QComboBox()
        self.combo_browser.addItems(["none", "chrome", "firefox", "edge", "brave", "opera", "vivaldi", "custom_file"])
        cur_browser = self.settings_mgr.get("browser_cookies", "none")
        idx = self.combo_browser.findText(cur_browser)
        if idx >= 0:
            self.combo_browser.setCurrentIndex(idx)
        grid_net.addWidget(self.combo_browser, 0, 1)

        grid_net.addWidget(QLabel("Custom Cookies File:"), 1, 0)
        self.edit_cookie_file = QLineEdit(self.settings_mgr.get("custom_cookies_file", ""))
        self.edit_cookie_file.setPlaceholderText("Path to cookies.txt")
        btn_cookie = QPushButton("Browse...")
        btn_cookie.setIcon(get_icon("folder", "#cbd5e1"))
        btn_cookie.setObjectName("btnSecondary")
        btn_cookie.clicked.connect(self.browse_cookie_file)
        cookie_box = QHBoxLayout()
        cookie_box.addWidget(self.edit_cookie_file, 1)
        cookie_box.addWidget(btn_cookie)
        grid_net.addLayout(cookie_box, 1, 1)

        grid_net.addWidget(QLabel("Download Rate Limit (e.g., 5M or empty):"), 2, 0)
        self.edit_rate_limit = QLineEdit(self.settings_mgr.get("rate_limit", ""))
        grid_net.addWidget(self.edit_rate_limit, 2, 1)

        grid_net.addWidget(QLabel("Concurrent Fragment Downloads:"), 3, 0)
        self.spin_fragments = QSpinBox()
        self.spin_fragments.setRange(1, 16)
        self.spin_fragments.setValue(self.settings_mgr.get("concurrent_fragments", 4))
        grid_net.addWidget(self.spin_fragments, 3, 1)

        grid_net.addWidget(QLabel("Proxy URL (e.g., socks5://127.0.0.1:1080):"), 4, 0)
        self.edit_proxy = QLineEdit(self.settings_mgr.get("proxy", ""))
        grid_net.addWidget(self.edit_proxy, 4, 1)

        layout.addWidget(grp_net)

        # 5. UI Theme & Extra Args
        grp_adv = QGroupBox("Appearance & Custom Options")
        grid_adv = QGridLayout(grp_adv)
        grid_adv.setSpacing(10)

        grid_adv.addWidget(QLabel("Theme Accent:"), 0, 0)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark_cyan", "dark_purple", "dark_emerald"])
        cur_theme = self.settings_mgr.get("theme", "dark_cyan")
        idx_t = self.combo_theme.findText(cur_theme)
        if idx_t >= 0:
            self.combo_theme.setCurrentIndex(idx_t)
        grid_adv.addWidget(self.combo_theme, 0, 1)

        grid_adv.addWidget(QLabel("Extra yt-dlp Arguments:"), 1, 0)
        self.edit_extra_args = QLineEdit(self.settings_mgr.get("custom_args", ""))
        self.edit_extra_args.setPlaceholderText("e.g., --geo-bypass --no-check-certificates")
        grid_adv.addWidget(self.edit_extra_args, 1, 1)

        layout.addWidget(grp_adv)

        # Bottom Buttons
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Save All Settings")
        self.btn_save.setIcon(get_icon("check", "#ffffff"))
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.setFixedHeight(40)
        self.btn_save.clicked.connect(self.save_all)

        self.btn_reset = QPushButton("Reset Defaults")
        self.btn_reset.setIcon(get_icon("refresh", "#cbd5e1"))
        self.btn_reset.setObjectName("btnSecondary")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.clicked.connect(self.reset_defaults)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_reset)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def check_ffmpeg_status(self):
        custom = self.edit_ffmpeg_path.text().strip() if hasattr(self, "edit_ffmpeg_path") else ""
        path = find_ffmpeg_binary(custom)
        if path:
            ok, ver = get_ffmpeg_version(path)
            self.lbl_ffmpeg_status.setText(f"Detected ({path})")
            self.lbl_ffmpeg_status.setStyleSheet("color: #34d399; font-weight: 600;")
            if hasattr(self, "lbl_ff_info"):
                self.lbl_ff_info.setText(f"FFmpeg Processor:  <b>Ready</b> ({os.path.basename(path)})")
        else:
            self.lbl_ffmpeg_status.setText("Not Found")
            self.lbl_ffmpeg_status.setStyleSheet("color: #f87171; font-weight: 600;")
            if hasattr(self, "lbl_ff_info"):
                self.lbl_ff_info.setText("FFmpeg Processor:  <b>Not Found</b>")

    def open_update_dialog(self):
        dialog = UpdateDialog(self.settings_mgr, self)
        dialog.engines_updated.connect(self.on_engines_updated)
        dialog.exec()

    def on_engines_updated(self):
        self.check_ffmpeg_status()
        self.settings_saved_signal.emit()

    def browse_download_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.edit_dir.text())
        if folder:
            self.edit_dir.setText(folder)

    def browse_ffmpeg_binary(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select FFmpeg Binary", "", "Executable (*.exe);;All Files (*)")
        if file:
            self.edit_ffmpeg_path.setText(file)
            self.check_ffmpeg_status()

    def browse_cookie_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Cookies File", "", "Text Files (*.txt);;All Files (*)")
        if file:
            self.edit_cookie_file.setText(file)

    def save_all(self):
        theme = self.combo_theme.currentText()
        settings = {
            "download_dir": self.edit_dir.text().strip(),
            "filename_template": self.edit_template.text().strip(),
            "custom_ffmpeg_path": self.edit_ffmpeg_path.text().strip(),
            "embed_thumbnail": self.chk_thumb.isChecked(),
            "embed_metadata": self.chk_meta.isChecked(),
            "embed_chapters": self.chk_chapters.isChecked(),
            "embed_subtitles": self.chk_embed_sub.isChecked(),
            "write_subtitles": self.chk_write_sub.isChecked(),
            "auto_subtitles": self.chk_auto_sub.isChecked(),
            "subtitles_languages": self.edit_sub_langs.text().strip(),
            "sponsorblock_enabled": self.chk_sponsor.isChecked(),
            "browser_cookies": self.combo_browser.currentText(),
            "custom_cookies_file": self.edit_cookie_file.text().strip(),
            "rate_limit": self.edit_rate_limit.text().strip(),
            "concurrent_fragments": self.spin_fragments.value(),
            "proxy": self.edit_proxy.text().strip(),
            "theme": theme,
            "custom_args": self.edit_extra_args.text().strip(),
            "check_updates_startup": self.chk_auto_update.isChecked(),
        }
        self.settings_mgr.save_settings(settings)
        self.check_ffmpeg_status()
        self.settings_saved_signal.emit()
        self.theme_changed_signal.emit(theme)
        QMessageBox.information(self, "Settings Saved", "Preferences and configurations saved successfully!")

    def reset_defaults(self):
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_mgr.settings = dict(self.settings_mgr.DEFAULT_CONFIG)
            self.settings_mgr.save_settings()
            self.edit_dir.setText(self.settings_mgr.get("download_dir"))
            self.edit_template.setText(self.settings_mgr.get("filename_template"))
            self.edit_ffmpeg_path.setText("")
            self.chk_thumb.setChecked(True)
            self.chk_meta.setChecked(True)
            self.chk_chapters.setChecked(True)
            self.chk_embed_sub.setChecked(False)
            self.chk_write_sub.setChecked(False)
            self.chk_auto_sub.setChecked(False)
            self.edit_sub_langs.setText("en")
            self.chk_sponsor.setChecked(False)
            self.combo_browser.setCurrentIndex(0)
            self.edit_cookie_file.setText("")
            self.edit_rate_limit.setText("")
            self.spin_fragments.setValue(4)
            self.edit_proxy.setText("")
            self.edit_extra_args.setText("")
            self.chk_auto_update.setChecked(True)
            self.check_ffmpeg_status()
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
