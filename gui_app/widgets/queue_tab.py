import os
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox,
    QProgressBar, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from gui_app.engine import DownloadWorker
from gui_app.settings_manager import SettingsManager

class QueueTab(QWidget):
    log_signal = Signal(str, str)
    download_finished_signal = Signal(dict)

    def __init__(self, settings_mgr: SettingsManager):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.queue_items: List[Dict[str, Any]] = []
        self.download_worker: Optional[DownloadWorker] = None
        self.current_running_index = -1

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # 1. Top Add Links Frame
        add_frame = QFrame()
        add_frame.setObjectName("cardFrame")
        add_layout = QVBoxLayout(add_frame)
        add_layout.setContentsMargins(14, 12, 14, 12)
        add_layout.setSpacing(8)

        add_header_row = QHBoxLayout()
        lbl_batch = QLabel("📋 Bulk URL Importer (one URL per line):")
        lbl_batch.setObjectName("sectionHeader")
        add_header_row.addWidget(lbl_batch)
        add_header_row.addStretch()

        self.text_bulk_urls = QPlainTextEdit()
        self.text_bulk_urls.setPlaceholderText("https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...\nhttps://instagram.com/p/...")
        self.text_bulk_urls.setFixedHeight(80)

        btn_row = QHBoxLayout()
        self.combo_batch_mode = QComboBox()
        self.combo_batch_mode.addItems(["Video: Best Quality (MP4)", "Video: 1080p FHD (MP4)", "Video: 720p HD (MP4)", "Audio: MP3 (320 kbps)", "Audio: M4A", "Audio: FLAC Lossless"])
        
        self.btn_add_bulk = QPushButton("➕ Add URLs to Queue")
        self.btn_add_bulk.setObjectName("btnPrimary")
        self.btn_add_bulk.clicked.connect(self.add_bulk_urls)

        self.btn_clear_input = QPushButton("Clear Input")
        self.btn_clear_input.setObjectName("btnSecondary")
        self.btn_clear_input.clicked.connect(self.text_bulk_urls.clear)

        btn_row.addWidget(QLabel("Default Format for Batch:"))
        btn_row.addWidget(self.combo_batch_mode)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear_input)
        btn_row.addWidget(self.btn_add_bulk)

        add_layout.addLayout(add_header_row)
        add_layout.addWidget(self.text_bulk_urls)
        add_layout.addLayout(btn_row)
        layout.addWidget(add_frame)

        # 2. Queue Controls & Table Frame
        table_frame = QFrame()
        table_frame.setObjectName("cardFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(14, 12, 14, 12)
        table_layout.setSpacing(10)

        ctrl_row = QHBoxLayout()
        self.queue_count_label = QLabel("Batch Queue (0 items)")
        self.queue_count_label.setObjectName("sectionHeader")

        self.btn_start_queue = QPushButton("⚡ Start Batch Download")
        self.btn_start_queue.setObjectName("btnStartDownload")
        self.btn_start_queue.setFixedHeight(34)
        self.btn_start_queue.clicked.connect(self.start_queue_download)

        self.btn_pause_queue = QPushButton("⏸  Pause Queue")
        self.btn_pause_queue.setObjectName("btnPauseAction")
        self.btn_pause_queue.setFixedHeight(34)
        self.btn_pause_queue.setEnabled(False)
        self.btn_pause_queue.clicked.connect(self.toggle_queue_pause)

        self.btn_stop_queue = QPushButton("✕ Stop / Cancel")
        self.btn_stop_queue.setObjectName("btnCancelAction")
        self.btn_stop_queue.setFixedHeight(34)
        self.btn_stop_queue.setEnabled(False)
        self.btn_stop_queue.clicked.connect(self.stop_queue_download)

        self.btn_clear_completed = QPushButton("🧹 Clear Done")
        self.btn_clear_completed.setFixedHeight(34)
        self.btn_clear_completed.clicked.connect(self.clear_completed)

        self.btn_clear_all = QPushButton("🗑️ Clear All")
        self.btn_clear_all.setFixedHeight(34)
        self.btn_clear_all.clicked.connect(self.clear_all)

        ctrl_row.addWidget(self.queue_count_label)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self.btn_clear_completed)
        ctrl_row.addWidget(self.btn_clear_all)
        ctrl_row.addWidget(self.btn_pause_queue)
        ctrl_row.addWidget(self.btn_stop_queue)
        ctrl_row.addWidget(self.btn_start_queue)
        table_layout.addLayout(ctrl_row)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["#", "Title / URL", "Format", "Status", "Progress"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 180)
        self.table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.table)

        layout.addWidget(table_frame, 1)

    def add_task(self, task: Dict[str, Any]):
        """Add a single task to queue."""
        task["status"] = "Pending"
        task["progress"] = 0
        self.queue_items.append(task)
        self.refresh_table()

    def add_bulk_urls(self):
        text = self.text_bulk_urls.toPlainText().strip()
        if not text:
            return

        lines = [line.strip() for line in text.splitlines() if line.strip() and (line.startswith("http://") or line.startswith("https://"))]
        if not lines:
            QMessageBox.warning(self, "Invalid Links", "No valid http:// or https:// URLs found.")
            return

        mode_text = self.combo_batch_mode.currentText()
        is_audio = "Audio" in mode_text
        
        audio_fmt = "mp3"
        if "M4A" in mode_text:
            audio_fmt = "m4a"
        elif "FLAC" in mode_text:
            audio_fmt = "flac"

        video_q = "best"
        if "1080p" in mode_text:
            video_q = "1080p"
        elif "720p" in mode_text:
            video_q = "720p"

        for url in lines:
            task = {
                "url": url,
                "title": url,
                "channel": "Pending",
                "thumbnail": "",
                "mode": "audio" if is_audio else "video",
                "video_quality": video_q,
                "video_format": "mp4",
                "audio_format": audio_fmt,
                "audio_bitrate": "320k",
                "embed_thumbnail": True,
                "embed_metadata": True,
                "embed_subtitles": False,
                "download_dir": self.settings_mgr.get("download_dir"),
                "status": "Pending",
                "progress": 0
            }
            self.queue_items.append(task)

        self.text_bulk_urls.clear()
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.queue_items))
        self.queue_count_label.setText(f"Batch Queue ({len(self.queue_items)} items)")

        for row, item in enumerate(self.queue_items):
            # 0. Index
            item_idx = QTableWidgetItem(str(row + 1))
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_idx)

            # 1. Title / URL
            title_text = item.get("title") or item.get("url")
            item_title = QTableWidgetItem(title_text)
            self.table.setItem(row, 1, item_title)

            # 2. Format
            fmt_text = item.get("mode", "video").upper()
            if item.get("mode") == "video":
                fmt_text += f" ({item.get('video_quality', 'best')})"
            else:
                fmt_text += f" ({item.get('audio_format', 'mp3').upper()})"
            item_fmt = QTableWidgetItem(fmt_text)
            item_fmt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_fmt)

            # 3. Status
            status = item.get("status", "Pending")
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if status == "Completed":
                item_status.setForeground(QColor("#34d399"))
            elif status == "Downloading":
                item_status.setForeground(QColor("#38bdf8"))
            elif status == "Paused":
                item_status.setForeground(QColor("#f59e0b"))
            elif status == "Failed":
                item_status.setForeground(QColor("#f87171"))
            self.table.setItem(row, 3, item_status)

            # 4. Progress bar widget
            p_bar = QProgressBar()
            p_bar.setRange(0, 100)
            p_bar.setValue(int(item.get("progress", 0)))
            p_bar.setFixedHeight(14)
            p_bar.setTextVisible(True)
            self.table.setCellWidget(row, 4, p_bar)

    def start_queue_download(self):
        pending_tasks = [task for task in self.queue_items if task.get("status") in ("Pending", "Failed", "Paused")]
        if not pending_tasks:
            QMessageBox.information(self, "No Tasks", "There are no pending items in the queue.")
            return

        self.btn_start_queue.setEnabled(False)
        self.btn_pause_queue.setEnabled(True)
        self.btn_pause_queue.setText("⏸  Pause Queue")
        self.btn_pause_queue.setObjectName("btnPauseAction")
        self.btn_pause_queue.style().unpolish(self.btn_pause_queue)
        self.btn_pause_queue.style().polish(self.btn_pause_queue)
        self.btn_stop_queue.setEnabled(True)

        for task in pending_tasks:
            if task.get("status") != "Completed":
                task["status"] = "Downloading"
                break
        self.refresh_table()

        settings = self.settings_mgr.load_settings()
        self.download_worker = DownloadWorker(pending_tasks, settings)
        self.download_worker.progress_signal.connect(self.on_queue_progress)
        self.download_worker.log_signal.connect(self.log_signal.emit)
        self.download_worker.task_finished.connect(self.on_queue_task_finished)
        self.download_worker.task_failed.connect(self.on_queue_task_failed)
        self.download_worker.all_finished.connect(self.on_queue_all_finished)
        self.download_worker.start()

    def toggle_queue_pause(self):
        if self.download_worker:
            is_paused = self.download_worker.toggle_pause()
            if is_paused:
                self.btn_pause_queue.setText("▶  Resume Queue")
                self.btn_pause_queue.setObjectName("btnResumeAction")
                for task in self.queue_items:
                    if task.get("status") == "Downloading":
                        task["status"] = "Paused"
                        break
            else:
                self.btn_pause_queue.setText("⏸  Pause Queue")
                self.btn_pause_queue.setObjectName("btnPauseAction")
                for task in self.queue_items:
                    if task.get("status") == "Paused":
                        task["status"] = "Downloading"
                        break
            self.btn_pause_queue.style().unpolish(self.btn_pause_queue)
            self.btn_pause_queue.style().polish(self.btn_pause_queue)
            self.refresh_table()

    def stop_queue_download(self):
        if self.download_worker:
            self.download_worker.cancel()
            self.btn_pause_queue.setEnabled(False)
            self.btn_stop_queue.setEnabled(False)

    def on_queue_progress(self, data: Dict[str, Any]):
        percent = data.get("percent", 0.0)
        status = data.get("status")
        for row, task in enumerate(self.queue_items):
            if task.get("status") in ("Downloading", "Paused"):
                task["progress"] = percent
                if status == "paused":
                    task["status"] = "Paused"
                widget = self.table.cellWidget(row, 4)
                if isinstance(widget, QProgressBar):
                    widget.setValue(int(percent))
                break

    def on_queue_task_finished(self, result: Dict[str, Any]):
        url = result.get("url")
        for row, task in enumerate(self.queue_items):
            if task.get("url") == url:
                task["status"] = "Completed"
                task["progress"] = 100
                task["title"] = result.get("title", task.get("title"))
                self.settings_mgr.add_history_entry(result)
                self.download_finished_signal.emit(result)
                break
        
        # Mark next pending task as Downloading
        for task in self.queue_items:
            if task.get("status") == "Pending":
                task["status"] = "Downloading"
                break

        self.refresh_table()

    def on_queue_task_failed(self, url: str, err: str):
        for row, task in enumerate(self.queue_items):
            if task.get("url") == url:
                task["status"] = "Failed"
                break
        
        for task in self.queue_items:
            if task.get("status") == "Pending":
                task["status"] = "Downloading"
                break

        self.refresh_table()

    def on_queue_all_finished(self):
        self.btn_start_queue.setEnabled(True)
        self.btn_pause_queue.setEnabled(False)
        self.btn_pause_queue.setText("⏸  Pause Queue")
        self.btn_pause_queue.setObjectName("btnPauseAction")
        self.btn_pause_queue.style().unpolish(self.btn_pause_queue)
        self.btn_pause_queue.style().polish(self.btn_pause_queue)
        self.btn_stop_queue.setEnabled(False)
        self.refresh_table()

    def clear_completed(self):
        self.queue_items = [task for task in self.queue_items if task.get("status") != "Completed"]
        self.refresh_table()

    def clear_all(self):
        self.queue_items.clear()
        self.refresh_table()
