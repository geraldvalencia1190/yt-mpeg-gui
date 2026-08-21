import os
import sys
import subprocess
import datetime
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon

from gui_app.settings_manager import SettingsManager
from gui_app.assets_manager import get_icon

class HistoryTab(QWidget):
    def __init__(self, settings_mgr: SettingsManager):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.history_items: List[Dict[str, Any]] = []

        self.init_ui()
        self.load_history_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top search & stats bar
        top_frame = QFrame()
        top_frame.setObjectName("cardFrame")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(10)

        self.lbl_history_count = QLabel("Download History (0 items)")
        self.lbl_history_count.setObjectName("sectionHeader")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search downloads by title, channel or URL...")
        self.search_input.textChanged.connect(self.filter_history)

        self.btn_clear_history = QPushButton("Clear History")
        self.btn_clear_history.setIcon(get_icon("trash", "#cbd5e1"))
        self.btn_clear_history.setObjectName("btnDanger")
        self.btn_clear_history.clicked.connect(self.clear_all_history)

        top_layout.addWidget(self.lbl_history_count)
        top_layout.addSpacing(16)
        top_layout.addWidget(self.search_input, 1)
        top_layout.addWidget(self.btn_clear_history)
        layout.addWidget(top_frame)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date/Time", "Title", "Format", "Size", "File Path", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 170)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        layout.addWidget(self.table, 1)

    def load_history_data(self):
        self.history_items = self.settings_mgr.load_history()
        self.populate_table(self.history_items)

    def populate_table(self, items: List[Dict[str, Any]]):
        self.table.setRowCount(len(items))
        self.lbl_history_count.setText(f"Download History ({len(items)} items)")

        for row, item in enumerate(items):
            # 0. Date/Time
            ts = item.get("timestamp", 0)
            date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "—"
            item_date = QTableWidgetItem(date_str)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_date)

            # 1. Title
            title = item.get("title") or item.get("url") or "Unknown"
            item_title = QTableWidgetItem(title)
            self.table.setItem(row, 1, item_title)

            # 2. Format
            fmt = item.get("format", "video")
            item_fmt = QTableWidgetItem(fmt)
            item_fmt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_fmt)

            # 3. Size
            sz = item.get("file_size", 0)
            sz_str = f"{sz / (1024*1024):.1f} MB" if sz > 0 else "—"
            item_sz = QTableWidgetItem(sz_str)
            item_sz.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_sz)

            # 4. File Path
            path = item.get("file_path", "")
            item_path = QTableWidgetItem(path)
            self.table.setItem(row, 4, item_path)

            # 5. Actions Widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(6)

            btn_play = QPushButton("Play")
            btn_play.setIcon(get_icon("play", "#38bdf8"))
            btn_play.setToolTip("Play / Open File")
            btn_play.setFixedWidth(54)
            btn_play.setObjectName("btnSecondary")
            btn_play.clicked.connect(lambda ch, p=path: self.play_file(p))

            btn_folder = QPushButton("Folder")
            btn_folder.setIcon(get_icon("folder", "#cbd5e1"))
            btn_folder.setToolTip("Show in Folder")
            btn_folder.setFixedWidth(64)
            btn_folder.setObjectName("btnSecondary")
            btn_folder.clicked.connect(lambda ch, p=path: self.show_in_folder(p))

            btn_del = QPushButton()
            btn_del.setIcon(get_icon("cancel", "#f87171"))
            btn_del.setToolTip("Remove from History")
            btn_del.setFixedWidth(30)
            btn_del.setObjectName("btnDanger")
            entry_id = item.get("id", "")
            btn_del.clicked.connect(lambda ch, eid=entry_id: self.delete_entry(eid))

            actions_layout.addWidget(btn_play)
            actions_layout.addWidget(btn_folder)
            actions_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 5, actions_widget)

    def filter_history(self, text: str):
        text = text.lower().strip()
        if not text:
            self.populate_table(self.history_items)
            return

        filtered = [
            item for item in self.history_items
            if text in item.get("title", "").lower() or text in item.get("channel", "").lower() or text in item.get("url", "").lower()
        ]
        self.populate_table(filtered)

    def play_file(self, filepath: str):
        if filepath and os.path.isfile(filepath):
            if sys.platform == "win32":
                os.startfile(filepath)
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", filepath])
        else:
            QMessageBox.warning(self, "File Not Found", f"The media file was moved or deleted:\n{filepath}")

    def show_in_folder(self, filepath: str):
        if filepath and os.path.exists(filepath):
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{os.path.abspath(filepath)}"')
            else:
                folder = os.path.dirname(filepath)
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder])
        else:
            folder = os.path.dirname(filepath) if filepath else ""
            if folder and os.path.isdir(folder):
                if sys.platform == "win32":
                    os.startfile(folder)
            else:
                QMessageBox.warning(self, "Folder Not Found", "Destination folder not found.")

    def delete_entry(self, entry_id: str):
        self.settings_mgr.remove_history_entry(entry_id)
        self.load_history_data()

    def clear_all_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all download history records?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_mgr.clear_history()
            self.load_history_data()

    def on_cell_double_clicked(self, row: int, col: int):
        path_item = self.table.item(row, 4)
        if path_item:
            self.play_file(path_item.text())
