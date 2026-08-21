import os
import sys
import subprocess
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QComboBox, QCheckBox, QProgressBar, QFileDialog, QMessageBox,
    QGridLayout, QGroupBox, QRadioButton, QButtonGroup, QSizePolicy,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QImage, QGuiApplication, QFont
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
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Smooth Scroll Area to prevent any vertical collapsing
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # ----------------------------------------------------
        # 1. Enter Media URL
        # ----------------------------------------------------
        grp_url = QGroupBox("1. Enter Media URL")
        grp_url.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        url_layout = QHBoxLayout(grp_url)
        url_layout.setContentsMargins(12, 14, 12, 12)
        url_layout.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=... or any supported video/audio link")
        self.url_input.setFixedHeight(30)
        self.url_input.returnPressed.connect(self.start_analyze)

        self.btn_paste = QPushButton("📋 Paste")
        self.btn_paste.setFixedHeight(30)
        self.btn_paste.setMinimumWidth(80)
        self.btn_paste.clicked.connect(self.paste_from_clipboard)

        self.btn_analyze = QPushButton("🔍 Analyze Link")
        self.btn_analyze.setFixedHeight(30)
        self.btn_analyze.setMinimumWidth(125)
        self.btn_analyze.clicked.connect(self.start_analyze)

        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.btn_paste)
        url_layout.addWidget(self.btn_analyze)
        layout.addWidget(grp_url)

        # ----------------------------------------------------
        # 2. Link Information (Explicit Row Heights & Clean Spacing)
        # ----------------------------------------------------
        grp_info = QGroupBox("2. Link Information")
        grp_info.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        info_main_layout = QHBoxLayout(grp_info)
        info_main_layout.setContentsMargins(12, 14, 12, 12)
        info_main_layout.setSpacing(16)

        # Thumbnail Box
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(180, 115)
        self.thumb_label.setStyleSheet("background-color: #101010; border: 1px solid #282828; border-radius: 4px; color: #555555;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setText("No Thumbnail")
        info_main_layout.addWidget(self.thumb_label)

        # 2-Column Grid with fixed row heights
        grid_info = QGridLayout()
        grid_info.setHorizontalSpacing(14)
        grid_info.setVerticalSpacing(4)

        for r in range(6):
            grid_info.setRowMinimumHeight(r, 20)

        # Col 0 & 1 (Left info)
        lbl_title_k = QLabel("Title")
        lbl_title_k.setObjectName("infoKey")
        self.val_title = QLabel("--")
        self.val_title.setObjectName("infoVal")
        self.val_title.setWordWrap(True)

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

        # Col 2 & 3 (Right info)
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

        grid_info.setColumnStretch(0, 0)
        grid_info.setColumnStretch(1, 3)
        grid_info.setColumnStretch(2, 0)
        grid_info.setColumnStretch(3, 2)

        info_main_layout.addLayout(grid_info, 1)
        layout.addWidget(grp_info)

        # ----------------------------------------------------
        # 3. Download Options (Separate Video vs Audio Options)
        # ----------------------------------------------------
        grp_opts = QGroupBox("3. Download Options")
        grp_opts.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        opts_layout = QVBoxLayout(grp_opts)
        opts_layout.setContentsMargins(12, 14, 12, 12)
        opts_layout.setSpacing(10)

        # Row 1: Mode Selection Radio Group
        mode_select_layout = QHBoxLayout()
        mode_select_layout.setSpacing(16)
        
        lbl_target = QLabel("Download Type:")
        lbl_target.setStyleSheet("font-weight: 700; color: #38bdf8;")
        
        self.radio_mode_group = QButtonGroup(self)
        self.radio_video = QRadioButton("🎥 Video Download (with Audio)")
        self.radio_audio = QRadioButton("🎵 Audio Extraction (MP3 / FLAC / WAV / M4A)")
        self.radio_video.setChecked(True)
        self.radio_mode_group.addButton(self.radio_video)
        self.radio_mode_group.addButton(self.radio_audio)
        self.radio_video.toggled.connect(self.on_mode_toggled)

        mode_select_layout.addWidget(lbl_target)
        mode_select_layout.addWidget(self.radio_video)
        mode_select_layout.addWidget(self.radio_audio)
        mode_select_layout.addStretch()
        opts_layout.addLayout(mode_select_layout)

        # Row 2: VIDEO Options Widget (Visible in Video Mode)
        self.widget_video_opts = QWidget()
        v_opts_layout = QHBoxLayout(self.widget_video_opts)
        v_opts_layout.setContentsMargins(0, 0, 0, 0)
        v_opts_layout.setSpacing(12)

        lbl_v_res = QLabel("Video Resolution:")
        lbl_v_res.setFixedWidth(110)
        self.combo_v_res = QComboBox()
        self.combo_v_res.setFixedHeight(28)
        self.combo_v_res.addItems([
            "Best Quality (Auto-merged)",
            "4K Ultra HD (2160p)",
            "2K Quad HD (1440p)",
            "1080p Full HD",
            "720p HD",
            "480p SD",
            "360p Low",
        ])

        lbl_v_fmt = QLabel("Video Container:")
        lbl_v_fmt.setFixedWidth(110)
        self.combo_v_fmt = QComboBox()
        self.combo_v_fmt.setFixedHeight(28)
        self.combo_v_fmt.addItems(["MP4 (Universal)", "MKV (Matroska)", "WEBM", "AVI", "MOV (QuickTime)"])

        v_opts_layout.addWidget(lbl_v_res)
        v_opts_layout.addWidget(self.combo_v_res, 1)
        v_opts_layout.addWidget(lbl_v_fmt)
        v_opts_layout.addWidget(self.combo_v_fmt, 1)
        opts_layout.addWidget(self.widget_video_opts)

        # Row 2: AUDIO Options Widget (Visible in Audio Mode)
        self.widget_audio_opts = QWidget()
        a_opts_layout = QHBoxLayout(self.widget_audio_opts)
        a_opts_layout.setContentsMargins(0, 0, 0, 0)
        a_opts_layout.setSpacing(12)

        lbl_a_fmt = QLabel("Audio Format / Codec:")
        lbl_a_fmt.setFixedWidth(130)
        self.combo_a_fmt = QComboBox()
        self.combo_a_fmt.setFixedHeight(28)
        self.combo_a_fmt.addItems(["MP3", "M4A (AAC)", "FLAC (Lossless)", "WAV (Lossless)", "OPUS", "AAC"])

        lbl_a_bitrate = QLabel("Audio Quality / Bitrate:")
        lbl_a_bitrate.setFixedWidth(130)
        self.combo_a_bitrate = QComboBox()
        self.combo_a_bitrate.setFixedHeight(28)
        self.combo_a_bitrate.addItems(["320 kbps (High Quality)", "256 kbps", "192 kbps (Standard)", "128 kbps (Compact)"])

        a_opts_layout.addWidget(lbl_a_fmt)
        a_opts_layout.addWidget(self.combo_a_fmt, 1)
        a_opts_layout.addWidget(lbl_a_bitrate)
        a_opts_layout.addWidget(self.combo_a_bitrate, 1)
        self.widget_audio_opts.hide()
        opts_layout.addWidget(self.widget_audio_opts)

        # Row 3: Output Folder & File Name Template
        widget_folder_row = QWidget()
        folder_row_layout = QHBoxLayout(widget_folder_row)
        folder_row_layout.setContentsMargins(0, 0, 0, 0)
        folder_row_layout.setSpacing(12)

        lbl_folder = QLabel("Output Folder:")
        lbl_folder.setFixedWidth(110)
        self.folder_input = QLineEdit(self.settings_mgr.get("download_dir"))
        self.folder_input.setFixedHeight(28)
        
        self.btn_browse = QPushButton("...")
        self.btn_browse.setFixedSize(30, 28)
        self.btn_browse.clicked.connect(self.browse_folder)

        folder_box = QHBoxLayout()
        folder_box.setContentsMargins(0, 0, 0, 0)
        folder_box.setSpacing(4)
        folder_box.addWidget(self.folder_input, 1)
        folder_box.addWidget(self.btn_browse)

        lbl_tmpl = QLabel("File Name Template:")
        lbl_tmpl.setFixedWidth(120)
        self.template_input = QLineEdit(self.settings_mgr.get("filename_template", "%(title)s.%(ext)s"))
        self.template_input.setFixedHeight(28)

        folder_row_layout.addWidget(lbl_folder)
        folder_row_layout.addLayout(folder_box, 1)
        folder_row_layout.addWidget(lbl_tmpl)
        folder_row_layout.addWidget(self.template_input, 1)
        opts_layout.addWidget(widget_folder_row)

        # Row 4: Checkboxes & Advanced Options
        chk_row = QHBoxLayout()
        chk_row.setContentsMargins(0, 0, 0, 0)
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

        self.btn_adv_opts = QPushButton("⚙️ Advanced Options...")
        self.btn_adv_opts.setFixedHeight(28)
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
        # Action Buttons Bar (Download, Pause/Resume, Add to Queue, Cancel)
        # ----------------------------------------------------
        act_layout = QHBoxLayout()
        act_layout.setSpacing(10)

        self.btn_download = QPushButton("⬇  Start Download Now")
        self.btn_download.setObjectName("btnStartDownload")
        self.btn_download.setFixedHeight(38)
        self.btn_download.clicked.connect(self.start_download)

        self.btn_pause = QPushButton("⏸  Pause")
        self.btn_pause.setObjectName("btnPauseAction")
        self.btn_pause.setFixedHeight(38)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_add_queue = QPushButton(":=  Add to Queue")
        self.btn_add_queue.setObjectName("btnQueueAction")
        self.btn_add_queue.setFixedHeight(38)
        self.btn_add_queue.clicked.connect(self.add_to_queue)

        self.btn_cancel = QPushButton("✕  Cancel")
        self.btn_cancel.setObjectName("btnCancelAction")
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_download)

        act_layout.addWidget(self.btn_download, 3)
        act_layout.addWidget(self.btn_pause, 2)
        act_layout.addWidget(self.btn_add_queue, 2)
        act_layout.addWidget(self.btn_cancel, 2)
        layout.addLayout(act_layout)

        # ----------------------------------------------------
        # 4. Progress
        # ----------------------------------------------------
        grp_prog = QGroupBox("4. Progress")
        grp_prog.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        prog_layout = QVBoxLayout(grp_prog)
        prog_layout.setContentsMargins(12, 14, 12, 12)
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
        layout.addStretch(1)

        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)

    def on_mode_toggled(self):
        is_video = self.radio_video.isChecked()
        self.widget_video_opts.setVisible(is_video)
        self.widget_audio_opts.setVisible(not is_video)
        self.chk_subs.setEnabled(is_video)

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

        # Fill in Section 2
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
        is_video = self.radio_video.isChecked()

        # Video quality
        res_text = self.combo_v_res.currentText()
        video_q = "best"
        if "4K" in res_text or "2160p" in res_text:
            video_q = "2160p"
        elif "2K" in res_text or "1440p" in res_text:
            video_q = "1440p"
        elif "1080p" in res_text:
            video_q = "1080p"
        elif "720p" in res_text:
            video_q = "720p"
        elif "480p" in res_text:
            video_q = "480p"
        elif "360p" in res_text:
            video_q = "360p"

        # Video Container Format
        video_fmt = self.combo_v_fmt.currentText().split()[0].lower()

        # Audio Codec & Bitrate
        audio_fmt = self.combo_a_fmt.currentText().split()[0].lower()
        audio_bitrate = self.combo_a_bitrate.currentText().split()[0]

        return {
            "url": url,
            "title": self.current_info.get("title", url) if self.current_info else url,
            "channel": self.current_info.get("uploader", "Unknown") if self.current_info else "Unknown",
            "thumbnail": self.current_info.get("thumbnail", "") if self.current_info else "",
            "mode": "video" if is_video else "audio",
            "video_quality": video_q,
            "video_format": video_fmt,
            "audio_format": audio_fmt,
            "audio_bitrate": audio_bitrate,
            "embed_thumbnail": self.chk_thumb.isChecked(),
            "embed_metadata": self.chk_meta.isChecked(),
            "embed_chapters": self.chk_chapters.isChecked(),
            "embed_subtitles": self.chk_subs.isChecked() if is_video else False,
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
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText("⏸  Pause")
        self.btn_pause.setObjectName("btnPauseAction")
        self.btn_pause.style().unpolish(self.btn_pause)
        self.btn_pause.style().polish(self.btn_pause)
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

    def toggle_pause(self):
        if self.download_worker:
            is_paused = self.download_worker.toggle_pause()
            if is_paused:
                self.btn_pause.setText("▶  Resume")
                self.btn_pause.setObjectName("btnResumeAction")
                self.lbl_prog_status.setText("Status: Paused ⏸ (Click Resume to continue)")
                self.lbl_speed.setText("Speed: 0.0 KB/s")
            else:
                self.btn_pause.setText("⏸  Pause")
                self.btn_pause.setObjectName("btnPauseAction")
                self.lbl_prog_status.setText("Status: Resuming download...")
            self.btn_pause.style().unpolish(self.btn_pause)
            self.btn_pause.style().polish(self.btn_pause)

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
            self.btn_pause.setEnabled(False)
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
        if status == "paused":
            self.lbl_speed.setText("Speed: 0.0 KB/s")
            self.lbl_eta.setText("ETA: Paused")
            self.lbl_prog_status.setText("Status: Paused ⏸ (Click Resume to continue)")
            return

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
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸  Pause")
        self.btn_pause.setObjectName("btnPauseAction")
        self.settings_mgr.add_history_entry(result)
        self.download_finished_signal.emit(result)

    def on_task_failed(self, url: str, err: str):
        self.lbl_prog_status.setText("Status: Download Failed ❌")
        self.btn_pause.setEnabled(False)
        QMessageBox.critical(self, "Download Error", f"Failed to download:\n{url}\n\n{err}")

    def on_all_finished(self):
        self.btn_download.setEnabled(True)
        self.btn_analyze.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸  Pause")
        self.btn_pause.setObjectName("btnPauseAction")
        self.btn_pause.style().unpolish(self.btn_pause)
        self.btn_pause.style().polish(self.btn_pause)
        self.btn_cancel.setEnabled(False)
