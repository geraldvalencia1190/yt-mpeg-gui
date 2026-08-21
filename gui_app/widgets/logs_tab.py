import os
import time
from typing import List, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QComboBox, QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QTextCursor, QColor

class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_logs: List[Tuple[str, str, str]] = []  # (timestamp, level, message)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top bar
        top_frame = QFrame()
        top_frame.setObjectName("cardFrame")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(10)

        lbl_logs = QLabel("📜 Diagnostic & Execution Logs")
        lbl_logs.setObjectName("sectionHeader")

        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["All Levels", "INFO & Errors", "WARNING & Errors", "ERROR Only"])
        self.combo_filter.currentIndexChanged.connect(self.rebuild_log_view)

        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Filter logs by text...")
        self.edit_search.textChanged.connect(self.rebuild_log_view)

        self.btn_copy = QPushButton("📋 Copy Logs")
        self.btn_copy.setObjectName("btnSecondary")
        self.btn_copy.clicked.connect(self.copy_logs)

        self.btn_save = QPushButton("💾 Export...")
        self.btn_save.setObjectName("btnSecondary")
        self.btn_save.clicked.connect(self.export_logs)

        self.btn_clear = QPushButton("🧹 Clear")
        self.btn_clear.setObjectName("btnDanger")
        self.btn_clear.clicked.connect(self.clear_logs)

        top_layout.addWidget(lbl_logs)
        top_layout.addSpacing(10)
        top_layout.addWidget(QLabel("Filter:"))
        top_layout.addWidget(self.combo_filter)
        top_layout.addWidget(self.edit_search, 1)
        top_layout.addWidget(self.btn_copy)
        top_layout.addWidget(self.btn_save)
        top_layout.addWidget(self.btn_clear)
        layout.addWidget(top_frame)

        # Log Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #080c14;
                color: #e2e8f0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #1f293d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.console, 1)

    def append_log(self, level: str, message: str):
        ts = time.strftime("%H:%M:%S")
        self.raw_logs.append((ts, level, message))
        if len(self.raw_logs) > 3000:
            self.raw_logs = self.raw_logs[-3000:]

        if self.should_display(level, message):
            html = self.format_html_line(ts, level, message)
            self.console.append(html)
            self.console.moveCursor(QTextCursor.MoveOperation.End)

    def should_display(self, level: str, message: str) -> bool:
        filter_idx = self.combo_filter.currentIndex()
        if filter_idx == 1 and level == "DEBUG":
            return False
        elif filter_idx == 2 and level in ("DEBUG", "INFO"):
            return False
        elif filter_idx == 3 and level != "ERROR":
            return False

        search = self.edit_search.text().strip().lower()
        if search and search not in message.lower():
            return False

        return True

    def format_html_line(self, ts: str, level: str, msg: str) -> str:
        color_map = {
            "INFO": "#38bdf8",     # cyan
            "WARNING": "#fbbf24",  # amber
            "ERROR": "#f87171",    # red
            "SUCCESS": "#34d399",  # green
            "DEBUG": "#64748b",    # slate
        }
        color = color_map.get(level, "#94a3b8")
        escaped_msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<span style="color: #64748b;">[{ts}]</span> <b style="color: {color};">[{level}]</b> <span style="color: #cbd5e1;">{escaped_msg}</span>'

    def rebuild_log_view(self):
        self.console.clear()
        html_lines = []
        for ts, level, msg in self.raw_logs:
            if self.should_display(level, msg):
                html_lines.append(self.format_html_line(ts, level, msg))
        if html_lines:
            self.console.setHtml("<br>".join(html_lines))
            self.console.moveCursor(QTextCursor.MoveOperation.End)

    def copy_logs(self):
        text = "\n".join([f"[{ts}] [{level}] {msg}" for ts, level, msg in self.raw_logs])
        QGuiApplication.clipboard().setText(text)
        QMessageBox.information(self, "Logs Copied", "All logs copied to clipboard.")

    def export_logs(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Log File", "yt-dlp-gui.log", "Log Files (*.log);;Text Files (*.txt)")
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    for ts, level, msg in self.raw_logs:
                        f.write(f"[{ts}] [{level}] {msg}\n")
                QMessageBox.information(self, "Export Successful", f"Logs exported to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save log file:\n{e}")

    def clear_logs(self):
        self.raw_logs.clear()
        self.console.clear()
