import os
import sys
import subprocess
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QComboBox, QCheckBox, QProgressBar,
    QFileDialog, QMessageBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QImage, QClipboard, QGuiApplication
import requests
from io import BytesIO
from PIL import Image

from gui_app.engine import InfoWorker, DownloadWorker
from gui_app.settings_manager import SettingsManager

class ThumbnailLoader(QThread):
    loaded = Signal(QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        if not self.url:
            return
        try:
            resp = requests.get(self.url, timeout=6)
            if resp.status_code == 200:
                image = Image.open(BytesIO(resp.content))
                image.thumbnail((260, 150), Image.Resampling.LANCZOS)
                
                # Convert PIL to QPixmap
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                data = image.tobytes("raw", "RGBA")
                qim = QImage(data, image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qim)
                self.loaded.emit(pixmap)
        except Exception:
            pass


class DownloaderTab(QWidget):
    add_to_queue_signal = Signal(dict)
    log_signal = Signal(str, str)
    download_finished_signal = Signal(dict)

    def __init__(self, settings_mgr: SettingsManager):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.info_worker: Optional[InfoWorker] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.current_info: Optional[Dict[str, Any]] = None
        self.thumb_loader: Optional[ThumbnailLoader] = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # 1. URL Input Bar
        url_frame = QFrame()
        url_frame.setObjectName("cardFrame")
        url_layout = QHBoxLayout(url_frame)
        url_layout.setContentsMargins(12, 10, 12, 10)
        url_layout.setSpacing(10)

        url_label = QLabel("🔗 Media URL:")
        url_label.setStyleSheet("font-weight: 700; color: #38bdf8;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube, Instagram, Twitter/X, TikTok, Reddit, Vimeo or any supported link...")
        self.url_input.returnPressed.connect(self.start_analyze)

        self.btn_paste = QPushButton("📋 Paste")
        self.btn_paste.setObjectName("btnSecondary")
        self.btn_paste.clicked.connect(self.paste_from_clipboard)

        self.btn_analyze = QPushButton("🔍 Analyze Link")
        self.btn_analyze.setObjectName("btnPrimary")
        self.btn_analyze.clicked.connect(self.start_analyze)

        self.btn_clear = QPushButton("✕")
        self.btn_clear.setObjectName("btnSecondary")
        self.btn_clear.setFixedWidth(36)
        self.btn_clear.clicked.connect(self.clear_input)

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.btn_paste)
        url_layout.addWidget(self.btn_analyze)
        url_layout.addWidget(self.btn_clear)
        layout.addWidget(url_frame)

        # 2. Media Preview Card
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("previewCard")
        self.preview_frame.setFixedHeight(160)
        preview_layout = QHBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(14, 12, 14, 12)
        preview_layout.setSpacing(16)

        # Thumbnail Label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(220, 130)
        self.thumb_label.setStyleSheet("background-color: #0b0f17; border-radius: 8px; border: 1px solid #1e293b;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setText("No Preview")
        preview_layout.addWidget(self.thumb_label)

        # Info Details
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        self.title_label = QLabel("Enter a URL and click 'Analyze Link' to inspect media details")
        self.title_label.setObjectName("headingTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")

        self.channel_label = QLabel("Channel: —")
        self.channel_label.setObjectName("subHeading")

        # Badges row
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(8)

        self.duration_badge = QLabel("⏱️ Duration: —")
        self.duration_badge.setObjectName("badgePill")

        self.quality_badge = QLabel("📺 Max Quality: —")
        self.quality_badge.setObjectName("badgePill")

        self.type_badge = QLabel("🎬 Single Video")
        self.type_badge.setObjectName("badgeSuccess")

        badges_layout.addWidget(self.duration_badge)
        badges_layout.addWidget(self.quality_badge)
        badges_layout.addWidget(self.type_badge)
        badges_layout.addStretch()

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.channel_label)
        info_layout.addLayout(badges_layout)
        info_layout.addStretch()

        preview_layout.addLayout(info_layout, 1)
        layout.addWidget(self.preview_frame)

        # 3. Format & Download Settings Card
        settings_frame = QFrame()
        settings_frame.setObjectName("cardFrame")
        settings_grid = QGridLayout(settings_frame)
        settings_grid.setContentsMargins(16, 14, 16, 14)
        settings_grid.setHorizontalSpacing(16)
        settings_grid.setVerticalSpacing(12)

        # Row 0: Mode selection
        mode_label = QLabel("🎯 Download Mode:")
        mode_label.setStyleSheet("font-weight: 700;")
        
        mode_btn_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.radio_video = QRadioButton("🎥 Video + Audio")
        self.radio_audio = QRadioButton("🎵 Audio Only (MP3 / FLAC / WAV)")
        self.radio_video.setChecked(True)
        self.mode_group.addButton(self.radio_video)
        self.mode_group.addButton(self.radio_audio)
        self.radio_video.toggled.connect(self.toggle_mode)
        mode_btn_layout.addWidget(self.radio_video)
        mode_btn_layout.addWidget(self.radio_audio)
        mode_btn_layout.addStretch()

        settings_grid.addWidget(mode_label, 0, 0)
        settings_grid.addLayout(mode_btn_layout, 0, 1, 1, 3)

        # Row 1: Video/Audio Quality & Container Selection
        self.lbl_quality = QLabel("✨ Quality Preset:")
        self.combo_quality = QComboBox()
        self.combo_quality.addItems([
            "Best Quality (Merged)",
            "4K Ultra HD (2160p)",
            "2K Quad HD (1440p)",
            "1080p Full HD",
            "720p HD",
            "480p SD",
            "360p Low",
        ])

        self.lbl_format = QLabel("📦 Container Format:")
        self.combo_format = QComboBox()
        self.combo_format.addItems(["MP4", "MKV", "WEBM", "AVI", "MOV"])

        # Audio specific dropdowns (hidden by default unless audio mode)
        self.lbl_audio_codec = QLabel("🎵 Audio Codec:")
        self.combo_audio_codec = QComboBox()
        self.combo_audio_codec.addItems(["MP3", "M4A (AAC)", "FLAC (Lossless)", "WAV (Lossless)", "OPUS", "AAC"])
        
        self.lbl_audio_bitrate = QLabel("⚡ Audio Bitrate:")
        self.combo_audio_bitrate = QComboBox()
        self.combo_audio_bitrate.addItems(["320 kbps (High Quality)", "256 kbps", "192 kbps (Standard)", "128 kbps (Compact)"])

        settings_grid.addWidget(self.lbl_quality, 1, 0)
        settings_grid.addWidget(self.combo_quality, 1, 1)
        settings_grid.addWidget(self.lbl_format, 1, 2)
        settings_grid.addWidget(self.combo_format, 1, 3)

        settings_grid.addWidget(self.lbl_audio_codec, 1, 0)
        settings_grid.addWidget(self.combo_audio_codec, 1, 1)
        settings_grid.addWidget(self.lbl_audio_bitrate, 1, 2)
        settings_grid.addWidget(self.combo_audio_bitrate, 1, 3)

        # Hide audio dropdowns initially
        self.lbl_audio_codec.hide()
        self.combo_audio_codec.hide()
        self.lbl_audio_bitrate.hide()
        self.combo_audio_bitrate.hide()

        # Row 2: Toggles
        toggles_layout = QHBoxLayout()
        toggles_layout.setSpacing(18)
        self.chk_thumb = QCheckBox("Embed Thumbnail")
        self.chk_thumb.setChecked(True)
        self.chk_meta = QCheckBox("Embed Metadata & Chapters")
        self.chk_meta.setChecked(True)
        self.chk_subs = QCheckBox("Embed Subtitles")
        self.chk_subs.setChecked(False)

        toggles_layout.addWidget(self.chk_thumb)
        toggles_layout.addWidget(self.chk_meta)
        toggles_layout.addWidget(self.chk_subs)
        toggles_layout.addStretch()

        settings_grid.addWidget(QLabel("⚙️ Quick Options:"), 2, 0)
        settings_grid.addLayout(toggles_layout, 2, 1, 1, 3)

        # Row 3: Output Folder
        folder_label = QLabel("📂 Output Folder:")
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

        self.folder_input = QLineEdit()
        self.folder_input.setText(self.settings_mgr.get("download_dir"))
        
        self.btn_browse = QPushButton("📁 Browse...")
        self.btn_browse.setObjectName("btnSecondary")
        self.btn_browse.clicked.connect(self.browse_folder)

        self.btn_open_folder = QPushButton("↗️ Open")
        self.btn_open_folder.setObjectName("btnSecondary")
        self.btn_open_folder.clicked.connect(self.open_current_folder)

        folder_layout.addWidget(self.folder_input, 1)
        folder_layout.addWidget(self.btn_browse)
        folder_layout.addWidget(self.btn_open_folder)

        settings_grid.addWidget(folder_label, 3, 0)
        settings_grid.addLayout(folder_layout, 3, 1, 1, 3)

        layout.addWidget(settings_frame)

        # 4. Action Buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        self.btn_download = QPushButton("⚡ Start Download Now")
        self.btn_download.setObjectName("btnPrimary")
        self.btn_download.setFixedHeight(44)
        self.btn_download.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.btn_download.clicked.connect(self.start_download)

        self.btn_add_queue = QPushButton("➕ Add to Queue")
        self.btn_add_queue.setObjectName("btnSecondary")
        self.btn_add_queue.setFixedHeight(44)
        self.btn_add_queue.clicked.connect(self.add_to_queue)

        self.btn_cancel = QPushButton("⏹️ Cancel")
        self.btn_cancel.setObjectName("btnDanger")
        self.btn_cancel.setFixedHeight(44)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_download)

        actions_layout.addWidget(self.btn_download, 2)
        actions_layout.addWidget(self.btn_add_queue, 1)
        actions_layout.addWidget(self.btn_cancel, 1)
        layout.addLayout(actions_layout)

        # 5. Live Progress Card
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progressCard")
        prog_layout = QVBoxLayout(self.progress_frame)
        prog_layout.setContentsMargins(14, 12, 14, 12)
        prog_layout.setSpacing(8)

        # Status text & filename
        status_row = QHBoxLayout()
        self.status_title = QLabel("Status: Idle")
        self.status_title.setStyleSheet("font-weight: 700; color: #38bdf8;")
        self.filename_label = QLabel("No active download")
        self.filename_label.setStyleSheet("color: #94a3b8;")
        status_row.addWidget(self.status_title)
        status_row.addSpacing(10)
        status_row.addWidget(self.filename_label, 1)
        prog_layout.addLayout(status_row)

        # Progress Bar
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        self.prog_bar.setFixedHeight(18)
        prog_layout.addWidget(self.prog_bar)

        # Progress Stats Row
        stats_row = QHBoxLayout()
        self.speed_label = QLabel("🚀 Speed: 0 KB/s")
        self.eta_label = QLabel("⏱️ ETA: --:--")
        self.size_label = QLabel("💾 Size: 0 MB / 0 MB")
        self.percent_label = QLabel("0.0%")
        self.percent_label.setStyleSheet("font-weight: 700; color: #00d2ff;")

        stats_row.addWidget(self.speed_label)
        stats_row.addSpacing(16)
        stats_row.addWidget(self.eta_label)
        stats_row.addSpacing(16)
        stats_row.addWidget(self.size_label)
        stats_row.addStretch()
        stats_row.addWidget(self.percent_label)
        prog_layout.addLayout(stats_row)

        layout.addWidget(self.progress_frame)
        layout.addStretch()

    def toggle_mode(self):
        is_video = self.radio_video.isChecked()
        self.lbl_quality.setVisible(is_video)
        self.combo_quality.setVisible(is_video)
        self.lbl_format.setVisible(is_video)
        self.combo_format.setVisible(is_video)

        self.lbl_audio_codec.setVisible(not is_video)
        self.combo_audio_codec.setVisible(not is_video)
        self.lbl_audio_bitrate.setVisible(not is_video)
        self.combo_audio_bitrate.setVisible(not is_video)

    def paste_from_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self.start_analyze()

    def clear_input(self):
        self.url_input.clear()
        self.current_info = None
        self.title_label.setText("Enter a URL and click 'Analyze Link' to inspect media details")
        self.channel_label.setText("Channel: —")
        self.duration_badge.setText("⏱️ Duration: —")
        self.quality_badge.setText("📺 Max Quality: —")
        self.type_badge.setText("🎬 Single Video")
        self.thumb_label.setPixmap(QPixmap())
        self.thumb_label.setText("No Preview")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)
            self.settings_mgr.set("download_dir", folder)

    def open_current_folder(self):
        folder = self.folder_input.text().strip()
        if os.path.isdir(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder])
        else:
            QMessageBox.warning(self, "Folder Not Found", "The specified download folder does not exist.")

    def start_analyze(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Empty URL", "Please enter a valid media link.")
            return

        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Analyzing...")
        self.title_label.setText("Fetching media information from server...")
        self.log_signal.emit("INFO", f"Analyzing link: {url}")

        settings = self.settings_mgr.load_settings()
        self.info_worker = InfoWorker(url, settings)
        self.info_worker.info_ready.connect(self.on_info_ready)
        self.info_worker.info_error.connect(self.on_info_error)
        self.info_worker.log_signal.connect(self.log_signal.emit)
        self.info_worker.start()

    def on_info_ready(self, info: Dict[str, Any]):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍 Analyze Link")
        self.current_info = info

        # Update info fields
        self.title_label.setText(info.get("title", "No Title"))
        self.channel_label.setText(f"Channel / Uploader: {info.get('uploader', 'Unknown')}")
        
        # Duration
        dur_sec = info.get("duration", 0)
        dur_str = info.get("duration_string")
        if not dur_str:
            mins, secs = divmod(dur_sec, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                dur_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            else:
                dur_str = f"{mins:02d}:{secs:02d}"
        self.duration_badge.setText(f"⏱️ Duration: {dur_str}")

        # Playlist vs Single
        if info.get("is_playlist"):
            self.type_badge.setText(f"📑 Playlist ({info.get('entry_count', 0)} videos)")
            self.type_badge.setObjectName("badgeWarning")
        else:
            self.type_badge.setText("🎬 Single Video")
            self.type_badge.setObjectName("badgeSuccess")
        self.type_badge.style().unpolish(self.type_badge)
        self.type_badge.style().polish(self.type_badge)

        # Formats list
        formats = info.get("formats", [])
        if formats:
            best_res = formats[0].get("resolution", "HD")
            self.quality_badge.setText(f"📺 Max Quality: {best_res}")
        else:
            self.quality_badge.setText("📺 Max Quality: Auto")

        # Load Thumbnail
        thumb_url = info.get("thumbnail")
        if thumb_url:
            self.thumb_label.setText("Loading...")
            self.thumb_loader = ThumbnailLoader(thumb_url)
            self.thumb_loader.loaded.connect(self.set_thumbnail)
            self.thumb_loader.start()
        else:
            self.thumb_label.setText("No Thumbnail")

    def set_thumbnail(self, pixmap: QPixmap):
        self.thumb_label.setPixmap(pixmap)

    def on_info_error(self, err_msg: str):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍 Analyze Link")
        self.title_label.setText("Failed to analyze URL.")
        QMessageBox.critical(self, "Analysis Failed", f"Could not retrieve video information:\n\n{err_msg}")

    def get_current_task_options(self) -> Dict[str, Any]:
        url = self.url_input.text().strip()
        is_video = self.radio_video.isChecked()

        # Map quality
        q_idx = self.combo_quality.currentIndex()
        quality_map = {0: "best", 1: "2160p", 2: "1440p", 3: "1080p", 4: "720p", 5: "480p", 6: "360p"}
        video_quality = quality_map.get(q_idx, "best")

        # Map audio format
        audio_codec_map = {0: "mp3", 1: "m4a", 2: "flac", 3: "wav", 4: "opus", 5: "aac"}
        audio_format = audio_codec_map.get(self.combo_audio_codec.currentIndex(), "mp3")

        # Map audio bitrate
        bitrate_map = {0: "320k", 1: "256k", 2: "192k", 3: "128k"}
        audio_bitrate = bitrate_map.get(self.combo_audio_bitrate.currentIndex(), "320k")

        task = {
            "url": url,
            "title": self.current_info.get("title", url) if self.current_info else url,
            "channel": self.current_info.get("uploader", "Unknown") if self.current_info else "Unknown",
            "thumbnail": self.current_info.get("thumbnail", "") if self.current_info else "",
            "mode": "video" if is_video else "audio",
            "video_quality": video_quality,
            "video_format": self.combo_format.currentText().lower(),
            "audio_format": audio_format,
            "audio_bitrate": audio_bitrate,
            "embed_thumbnail": self.chk_thumb.isChecked(),
            "embed_metadata": self.chk_meta.isChecked(),
            "embed_subtitles": self.chk_subs.isChecked(),
            "download_dir": self.folder_input.text().strip() or self.settings_mgr.get("download_dir"),
        }
        return task

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Empty URL", "Please enter a valid media link first.")
            return

        task = self.get_current_task_options()
        settings = self.settings_mgr.load_settings()

        self.btn_download.setEnabled(False)
        self.btn_analyze.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.status_title.setText("Status: Downloading")
        self.filename_label.setText("Preparing download...")
        self.prog_bar.setValue(0)

        self.download_worker = DownloadWorker([task], settings)
        self.download_worker.progress_signal.connect(self.on_progress_update)
        self.download_worker.log_signal.connect(self.log_signal.emit)
        self.download_worker.task_finished.connect(self.on_task_finished)
        self.download_worker.task_failed.connect(self.on_task_failed)
        self.download_worker.all_finished.connect(self.on_all_finished)
        self.download_worker.start()

    def add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Empty URL", "Please enter a valid media link first.")
            return
        task = self.get_current_task_options()
        self.add_to_queue_signal.emit(task)
        QMessageBox.information(self, "Added to Queue", f"Added to batch queue:\n{task.get('title', url)}")

    def cancel_download(self):
        if self.download_worker:
            self.download_worker.cancel()
            self.btn_cancel.setEnabled(False)
            self.status_title.setText("Status: Cancelling...")

    def on_progress_update(self, data: Dict[str, Any]):
        status = data.get("status")
        percent = data.get("percent", 0.0)
        speed = data.get("speed", 0)
        eta = data.get("eta", 0)
        downloaded = data.get("downloaded_bytes", 0)
        total = data.get("total_bytes", 0)
        filename = data.get("filename", "")

        self.prog_bar.setValue(int(percent))
        self.percent_label.setText(f"{percent:.1f}%")

        if filename:
            self.filename_label.setText(filename)

        # Format Speed
        if speed > 1024 * 1024:
            self.speed_label.setText(f"🚀 Speed: {speed / (1024*1024):.2f} MB/s")
        elif speed > 1024:
            self.speed_label.setText(f"🚀 Speed: {speed / 1024:.1f} KB/s")
        else:
            self.speed_label.setText("🚀 Speed: --")

        # Format ETA
        if eta > 0:
            m, s = divmod(int(eta), 60)
            h, m = divmod(m, 60)
            if h > 0:
                self.eta_label.setText(f"⏱️ ETA: {h:02d}:{m:02d}:{s:02d}")
            else:
                self.eta_label.setText(f"⏱️ ETA: {m:02d}:{s:02d}")
        else:
            self.eta_label.setText("⏱️ ETA: --:--")

        # Format Size
        d_mb = downloaded / (1024 * 1024)
        t_mb = total / (1024 * 1024)
        if total > 0:
            self.size_label.setText(f"💾 Size: {d_mb:.1f} MB / {t_mb:.1f} MB")
        elif downloaded > 0:
            self.size_label.setText(f"💾 Downloaded: {d_mb:.1f} MB")

        if status == "processing":
            self.status_title.setText("Status: Processing / Merging (FFmpeg)...")
        elif status == "downloading":
            self.status_title.setText("Status: Downloading...")

    def on_task_finished(self, result: Dict[str, Any]):
        self.status_title.setText("Status: Download Completed! 🎉")
        self.prog_bar.setValue(100)
        self.percent_label.setText("100.0%")
        self.settings_mgr.add_history_entry(result)
        self.download_finished_signal.emit(result)

    def on_task_failed(self, url: str, err: str):
        self.status_title.setText("Status: Download Failed ❌")
        QMessageBox.critical(self, "Download Error", f"Failed to download:\n{url}\n\nError:\n{err}")

    def on_all_finished(self):
        self.btn_download.setEnabled(True)
        self.btn_analyze.setEnabled(True)
        self.btn_cancel.setEnabled(False)
