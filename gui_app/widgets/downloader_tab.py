import os
import sys
import subprocess
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QComboBox, QCheckBox, QProgressBar, QFileDialog, QMessageBox,
    QGridLayout, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QImage, QGuiApplication
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
                image.thumbnail((220, 130), Image.Resampling.LANCZOS)
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
    open_settings_signal = Signal()

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
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # ----------------------------------------------------
        # 1. Enter Media URL
        # ----------------------------------------------------
        grp_url = QGroupBox("1. Enter Media URL")
        url_layout = QHBoxLayout(grp_url)
        url_layout.setContentsMargins(10, 12, 10, 10)
        url_layout.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=... or any supported URL")
        self.url_input.returnPressed.connect(self.start_analyze)

        self.btn_paste = QPushButton("Paste")
        self.btn_paste.setFixedWidth(70)
        self.btn_paste.clicked.connect(self.paste_from_clipboard)

        self.btn_analyze = QPushButton("🔍 Analyze Link")
        self.btn_analyze.setFixedWidth(110)
        self.btn_analyze.clicked.connect(self.start_analyze)

        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.btn_paste)
        url_layout.addWidget(self.btn_analyze)
        layout.addWidget(grp_url)

        # ----------------------------------------------------
        # 2. Link Information
        # ----------------------------------------------------
        grp_info = QGroupBox("2. Link Information")
        info_main_layout = QHBoxLayout(grp_info)
        info_main_layout.setContentsMargins(10, 12, 10, 10)
        info_main_layout.setSpacing(14)

        # Thumbnail Box
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(180, 115)
        self.thumb_label.setStyleSheet("background-color: #121212; border: 1px solid #2e2e2e; border-radius: 3px; color: #666666;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setText("No Thumbnail")
        info_main_layout.addWidget(self.thumb_label)

        # Grid for info fields (2 columns)
        grid_info = QGridLayout()
        grid_info.setHorizontalSpacing(16)
        grid_info.setVerticalSpacing(4)

        # Col 1: Left Key-Values
        lbl_title_k = QLabel("Title")
        lbl_title_k.setObjectName("infoKey")
        self.val_title = QLabel("--")
        self.val_title.setObjectName("infoVal")
        self.val_title.setWordWrap(True)
        self.val_title.setMaximumHeight(36)

        lbl_uploader_k = QLabel("Uploader / Channel")
        lbl_uploader_k.setObjectName("infoKey")
        self.val_uploader = QLabel("--")
        self.val_uploader.setObjectName("infoVal")

        lbl_type_k = QLabel("Type")
        lbl_type_k.setObjectName("infoKey")
        self.val_type = QLabel("Single Video")
        self.val_type.setObjectName("infoVal")

        lbl_entries_k = QLabel("Entries")
        lbl_entries_k.setObjectName("infoKey")
        self.val_entries = QLabel("1 video")
        self.val_entries.setObjectName("infoVal")

        lbl_dur_k = QLabel("Duration")
        lbl_dur_k.setObjectName("infoKey")
        self.val_dur = QLabel("--:--")
        self.val_dur.setObjectName("infoVal")

        lbl_qual_k = QLabel("Max Quality")
        lbl_qual_k.setObjectName("infoKey")
        self.val_qual = QLabel("Auto")
        self.val_qual.setObjectName("infoVal")

        grid_info.addWidget(lbl_title_k, 0, 0)
        grid_info.addWidget(self.val_title, 0, 1)
        grid_info.addWidget(lbl_uploader_k, 1, 0)
        grid_info.addWidget(self.val_uploader, 1, 1)
        grid_info.addWidget(lbl_type_k, 2, 0)
        grid_info.addWidget(self.val_type, 2, 1)
        grid_info.addWidget(lbl_entries_k, 3, 0)
        grid_info.addWidget(self.val_entries, 3, 1)
        grid_info.addWidget(lbl_dur_k, 4, 0)
        grid_info.addWidget(self.val_dur, 4, 1)
        grid_info.addWidget(lbl_qual_k, 5, 0)
        grid_info.addWidget(self.val_qual, 5, 1)

        # Col 2: Right Key-Values
        lbl_avail_k = QLabel("Availability")
        lbl_avail_k.setObjectName("infoKey")
        self.val_avail = QLabel("✔ Available")
        self.val_avail.setObjectName("infoAvailable")

        lbl_fmt_k = QLabel("Formats")
        lbl_fmt_k.setObjectName("infoKey")
        self.val_fmts = QLabel("Audio + Video")
        self.val_fmts.setObjectName("infoVal")

        lbl_ext_k = QLabel("Extractors")
        lbl_ext_k.setObjectName("infoKey")
        self.val_extractors = QLabel("generic")
        self.val_extractors.setObjectName("infoVal")

        lbl_date_k = QLabel("Upload Date")
        lbl_date_k.setObjectName("infoKey")
        self.val_date = QLabel("--")
        self.val_date.setObjectName("infoVal")

        lbl_desc_k = QLabel("Description")
        lbl_desc_k.setObjectName("infoKey")
        self.val_desc = QLabel("--")
        self.val_desc.setObjectName("infoVal")

        grid_info.addWidget(lbl_avail_k, 0, 2)
        grid_info.addWidget(self.val_avail, 0, 3)
        grid_info.addWidget(lbl_fmt_k, 1, 2)
        grid_info.addWidget(self.val_fmts, 1, 3)
        grid_info.addWidget(lbl_ext_k, 2, 2)
        grid_info.addWidget(self.val_extractors, 2, 3)
        grid_info.addWidget(lbl_date_k, 3, 2)
        grid_info.addWidget(self.val_date, 3, 3)
        grid_info.addWidget(lbl_desc_k, 4, 2)
        grid_info.addWidget(self.val_desc, 4, 3)

        info_main_layout.addLayout(grid_info, 1)
        layout.addWidget(grp_info)

        # ----------------------------------------------------
        # 3. Download Options
        # ----------------------------------------------------
        grp_opts = QGroupBox("3. Download Options")
        opts_layout = QVBoxLayout(grp_opts)
        opts_layout.setContentsMargins(10, 12, 10, 10)
        opts_layout.setSpacing(8)

        grid_opts = QGridLayout()
        grid_opts.setHorizontalSpacing(12)
        grid_opts.setVerticalSpacing(6)

        # Col 0: Mode & Codec
        lbl_mode = QLabel("Download Mode:")
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            "Audio Only (MP3)",
            "Audio Only (FLAC Lossless)",
            "Audio Only (M4A)",
            "Audio Only (WAV)",
            "Video + Audio (MP4)",
            "Video + Audio (Best Quality)",
            "Video (1080p FHD)",
            "Video (720p HD)",
            "Video (4K UHD)",
        ])
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)

        self.lbl_codec = QLabel("Audio Codec:")
        self.combo_codec = QComboBox()
        self.combo_codec.addItems(["MP3", "M4A (AAC)", "FLAC", "WAV", "OPUS", "AAC"])

        grid_opts.addWidget(lbl_mode, 0, 0)
        grid_opts.addWidget(self.combo_mode, 0, 1)
        grid_opts.addWidget(self.lbl_codec, 1, 0)
        grid_opts.addWidget(self.combo_codec, 1, 1)

        # Col 1: Quality / Bitrate
        self.lbl_bitrate = QLabel("Audio Quality / Bitrate:")
        self.combo_bitrate = QComboBox()
        self.combo_bitrate.addItems(["320 kbps (High Quality)", "256 kbps", "192 kbps (Standard)", "128 kbps (Compact)"])

        grid_opts.addWidget(self.lbl_bitrate, 0, 2)
        grid_opts.addWidget(self.combo_bitrate, 0, 3)

        # Col 2: Output Folder & Template
        lbl_folder = QLabel("Output Folder:")
        self.folder_input = QLineEdit(self.settings_mgr.get("download_dir"))
        self.btn_browse = QPushButton("...")
        self.btn_browse.setFixedWidth(30)
        self.btn_browse.clicked.connect(self.browse_folder)

        folder_box = QHBoxLayout()
        folder_box.setSpacing(4)
        folder_box.addWidget(self.folder_input, 1)
        folder_box.addWidget(self.btn_browse)

        lbl_tmpl = QLabel("File Name Template:")
        self.template_input = QLineEdit(self.settings_mgr.get("filename_template", "%(title)s.%(ext)s"))

        grid_opts.addWidget(lbl_folder, 0, 4)
        grid_opts.addLayout(folder_box, 0, 5)
        grid_opts.addWidget(lbl_tmpl, 1, 4)
        grid_opts.addWidget(self.template_input, 1, 5)

        opts_layout.addLayout(grid_opts)

        # Checkboxes row & Advanced button
        chk_row = QHBoxLayout()
        chk_row.setSpacing(14)

        self.chk_thumb = QCheckBox("Embed Thumbnail")
        self.chk_thumb.setChecked(True)

        self.chk_meta = QCheckBox("Embed Metadata")
        self.chk_meta.setChecked(True)

        self.chk_chapters = QCheckBox("Chapters")
        self.chk_chapters.setChecked(True)

        self.chk_subs = QCheckBox("Embed Subtitles")
        self.chk_subs.setChecked(False)

        self.chk_queue_error = QCheckBox("Add to Queue if errors")
        self.chk_queue_error.setChecked(False)

        self.btn_adv_opts = QPushButton("Advanced Options...")
        self.btn_adv_opts.clicked.connect(self.open_settings_signal.emit)

        chk_row.addWidget(self.chk_thumb)
        chk_row.addWidget(self.chk_meta)
        chk_row.addWidget(self.chk_chapters)
        chk_row.addWidget(self.chk_subs)
        chk_row.addWidget(self.chk_queue_error)
        chk_row.addStretch()
        chk_row.addWidget(self.btn_adv_opts)

        opts_layout.addLayout(chk_row)
        layout.addWidget(grp_opts)

        # ----------------------------------------------------
        # Action Buttons
        # ----------------------------------------------------
        act_layout = QHBoxLayout()
        act_layout.setSpacing(10)

        self.btn_download = QPushButton("⬇  Start Download Now")
        self.btn_download.setObjectName("btnStartDownload")
        self.btn_download.setFixedHeight(38)
        self.btn_download.clicked.connect(self.start_download)

        self.btn_add_queue = QPushButton(":=  Add to Queue")
        self.btn_add_queue.setObjectName("btnQueueAction")
        self.btn_add_queue.setFixedHeight(38)
        self.btn_add_queue.clicked.connect(self.add_to_queue)

        self.btn_cancel = QPushButton("✕  Cancel")
        self.btn_cancel.setObjectName("btnCancelAction")
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_download)

        act_layout.addWidget(self.btn_download, 2)
        act_layout.addWidget(self.btn_add_queue, 1)
        act_layout.addWidget(self.btn_cancel, 1)
        layout.addLayout(act_layout)

        # ----------------------------------------------------
        # 4. Progress
        # ----------------------------------------------------
        grp_prog = QGroupBox("4. Progress")
        prog_layout = QVBoxLayout(grp_prog)
        prog_layout.setContentsMargins(10, 12, 10, 10)
        prog_layout.setSpacing(6)

        # Top line: Status (left) & Item (right)
        stat_top_row = QHBoxLayout()
        self.lbl_prog_status = QLabel("Status: Idle")
        self.lbl_prog_status.setStyleSheet("color: #38bdf8; font-weight: 700;")
        
        self.lbl_item_counter = QLabel("Item: 0 / 0")
        self.lbl_item_counter.setStyleSheet("color: #cbd5e1; font-weight: 600;")

        stat_top_row.addWidget(self.lbl_prog_status, 1)
        stat_top_row.addWidget(self.lbl_item_counter)
        prog_layout.addLayout(stat_top_row)

        # Progress Bar
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        self.prog_bar.setFixedHeight(18)
        prog_layout.addWidget(self.prog_bar)

        # Bottom stats row
        stat_bot_row = QHBoxLayout()
        self.lbl_speed = QLabel("Speed: -- MB/s")
        self.lbl_eta = QLabel("ETA: --:--")
        self.lbl_size = QLabel("Size: 0 MB / 0 MB")
        self.lbl_downloaded = QLabel("Downloaded: 0 MB")

        stat_bot_row.addWidget(self.lbl_speed)
        stat_bot_row.addSpacing(20)
        stat_bot_row.addWidget(self.lbl_eta)
        stat_bot_row.addSpacing(20)
        stat_bot_row.addWidget(self.lbl_size)
        stat_bot_row.addStretch()
        stat_bot_row.addWidget(self.lbl_downloaded)
        prog_layout.addLayout(stat_bot_row)

        layout.addWidget(grp_prog)
        layout.addStretch()

    def on_mode_changed(self):
        mode_text = self.combo_mode.currentText()
        is_audio = "Audio" in mode_text

        if is_audio:
            self.lbl_codec.setText("Audio Codec:")
            self.combo_codec.clear()
            self.combo_codec.addItems(["MP3", "M4A (AAC)", "FLAC", "WAV", "OPUS", "AAC"])
            self.lbl_bitrate.setText("Audio Quality / Bitrate:")
            self.combo_bitrate.clear()
            self.combo_bitrate.addItems(["320 kbps (High Quality)", "256 kbps", "192 kbps (Standard)", "128 kbps (Compact)"])
        else:
            self.lbl_codec.setText("Video Container:")
            self.combo_codec.clear()
            self.combo_codec.addItems(["MP4", "MKV", "WEBM", "AVI", "MOV"])
            self.lbl_bitrate.setText("Video Resolution:")
            self.combo_bitrate.clear()
            self.combo_bitrate.addItems(["Best Quality", "4K UHD (2160p)", "2K QHD (1440p)", "1080p FHD", "720p HD", "480p SD", "360p Low"])

    def paste_from_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self.start_analyze()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)
            self.settings_mgr.set("download_dir", folder)

    def start_analyze(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Empty URL", "Please enter a valid media link.")
            return

        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Analyzing...")
        self.val_title.setText("Fetching media information...")
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

        # Fill in Section 2 Grid
        self.val_title.setText(info.get("title", "No Title"))
        self.val_uploader.setText(info.get("uploader", "Unknown"))
        
        is_pl = info.get("is_playlist", False)
        ent_count = info.get("entry_count", 1)
        self.val_type.setText("Playlist / Collection" if is_pl else "Single Video")
        self.val_entries.setText(f"{ent_count} video{'s' if ent_count != 1 else ''}")

        dur_sec = info.get("duration", 0)
        dur_str = info.get("duration_string")
        if not dur_str:
            mins, secs = divmod(dur_sec, 60)
            hours, mins = divmod(mins, 60)
            dur_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins:02d}:{secs:02d}"
        self.val_dur.setText(dur_str)

        formats = info.get("formats", [])
        best_res = formats[0].get("resolution", "Auto") if formats else "Auto"
        self.val_qual.setText(best_res)

        self.val_avail.setText("✔ Available")
        self.val_avail.setStyleSheet("color: #22c55e; font-weight: 700;")
        self.val_fmts.setText("Audio + Video")
        
        # Extractor name from URL
        url = info.get("url", "")
        extractor = "generic"
        if "youtube.com" in url or "youtu.be" in url:
            extractor = "youtube" if not is_pl else "youtube:playlist"
        elif "instagram.com" in url:
            extractor = "instagram"
        elif "tiktok.com" in url:
            extractor = "tiktok"
        elif "twitter.com" in url or "x.com" in url:
            extractor = "twitter"
        self.val_extractors.setText(extractor)

        self.lbl_item_counter.setText(f"Item: 1 / {ent_count}")

        # Load Thumbnail
        thumb_url = info.get("thumbnail")
        if thumb_url:
            self.thumb_label.setText("Loading...")
            self.thumb_loader = ThumbnailLoader(thumb_url)
            self.thumb_loader.loaded.connect(self.thumb_label.setPixmap)
            self.thumb_loader.start()
        else:
            self.thumb_label.setText("No Thumbnail")

    def on_info_error(self, err_msg: str):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍 Analyze Link")
        self.val_title.setText("Failed to analyze link.")
        self.val_avail.setText("❌ Unavailable / Error")
        self.val_avail.setStyleSheet("color: #ef4444; font-weight: 700;")
        QMessageBox.critical(self, "Analysis Failed", f"Could not retrieve media info:\n{err_msg}")

    def get_current_task_options(self) -> Dict[str, Any]:
        url = self.url_input.text().strip()
        mode_text = self.combo_mode.currentText()
        is_audio = "Audio" in mode_text

        # Audio Codec & Bitrate
        audio_fmt = self.combo_codec.currentText().lower().split()[0]
        audio_bitrate = self.combo_bitrate.currentText().split()[0]

        # Video quality
        video_q = "best"
        if "4K" in mode_text or "2160p" in self.combo_bitrate.currentText():
            video_q = "2160p"
        elif "2K" in mode_text or "1440p" in self.combo_bitrate.currentText():
            video_q = "1440p"
        elif "1080p" in mode_text or "1080p" in self.combo_bitrate.currentText():
            video_q = "1080p"
        elif "720p" in mode_text or "720p" in self.combo_bitrate.currentText():
            video_q = "720p"

        video_fmt = self.combo_codec.currentText().lower() if not is_audio else "mp4"

        return {
            "url": url,
            "title": self.current_info.get("title", url) if self.current_info else url,
            "channel": self.current_info.get("uploader", "Unknown") if self.current_info else "Unknown",
            "thumbnail": self.current_info.get("thumbnail", "") if self.current_info else "",
            "mode": "audio" if is_audio else "video",
            "video_quality": video_q,
            "video_format": video_fmt,
            "audio_format": audio_fmt,
            "audio_bitrate": audio_bitrate,
            "embed_thumbnail": self.chk_thumb.isChecked(),
            "embed_metadata": self.chk_meta.isChecked(),
            "embed_chapters": self.chk_chapters.isChecked(),
            "embed_subtitles": self.chk_subs.isChecked(),
            "download_dir": self.folder_input.text().strip() or self.settings_mgr.get("download_dir"),
            "filename_template": self.template_input.text().strip() or "%(title)s.%(ext)s"
        }

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
        self.lbl_prog_status.setText(f"Status: Downloading...  {task.get('title', url)}")
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
            self.lbl_prog_status.setText("Status: Cancelling...")

    def on_progress_update(self, data: Dict[str, Any]):
        status = data.get("status")
        percent = data.get("percent", 0.0)
        speed = data.get("speed", 0)
        eta = data.get("eta", 0)
        downloaded = data.get("downloaded_bytes", 0)
        total = data.get("total_bytes", 0)
        filename = data.get("filename", "")

        self.prog_bar.setValue(int(percent))

        # Speed
        if speed > 1024 * 1024:
            self.lbl_speed.setText(f"Speed: {speed / (1024*1024):.1f} MB/s")
        elif speed > 1024:
            self.lbl_speed.setText(f"Speed: {speed / 1024:.1f} KB/s")
        else:
            self.lbl_speed.setText("Speed: -- MB/s")

        # ETA
        if eta > 0:
            m, s = divmod(int(eta), 60)
            h, m = divmod(m, 60)
            self.lbl_eta.setText(f"ETA: {h:02d}:{m:02d}:{s:02d}" if h > 0 else f"ETA: {m:02d}:{s:02d}")
        else:
            self.lbl_eta.setText("ETA: --:--")

        # Size
        d_mb = downloaded / (1024 * 1024)
        t_mb = total / (1024 * 1024)
        if total > 0:
            self.lbl_size.setText(f"Size: {d_mb:.1f} MB / {t_mb:.1f} MB")
        elif downloaded > 0:
            self.lbl_size.setText(f"Size: {d_mb:.1f} MB")
        self.lbl_downloaded.setText(f"Downloaded: {d_mb:.1f} MB")

        if status == "processing":
            self.lbl_prog_status.setText(f"Status: Processing / Merging (FFmpeg)... {filename}")
        elif status == "downloading":
            self.lbl_prog_status.setText(f"Status: Downloading... {filename}")

    def on_task_finished(self, result: Dict[str, Any]):
        self.lbl_prog_status.setText("Status: Download Completed Successfully! 🎉")
        self.prog_bar.setValue(100)
        self.settings_mgr.add_history_entry(result)
        self.download_finished_signal.emit(result)

    def on_task_failed(self, url: str, err: str):
        self.lbl_prog_status.setText("Status: Download Failed ❌")
        QMessageBox.critical(self, "Download Error", f"Failed to download:\n{url}\n\n{err}")

    def on_all_finished(self):
        self.btn_download.setEnabled(True)
        self.btn_analyze.setEnabled(True)
        self.btn_cancel.setEnabled(False)
