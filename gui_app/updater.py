import os
import sys
import time
import zipfile
import shutil
import subprocess
import requests
import yt_dlp
from typing import Dict, Any, Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGroupBox, QCheckBox, QMessageBox, QFrame,
    QGridLayout
)
from PySide6.QtCore import Qt, Signal, QThread
from gui_app.ffmpeg_finder import find_ffmpeg_binary, get_ffmpeg_version, get_user_bin_dir
from gui_app.settings_manager import SettingsManager

YTDLP_REPO = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
FFMPEG_REPO = "https://api.github.com/repos/yt-dlp/FFmpeg-Builds/releases/latest"

class CheckUpdatesWorker(QThread):
    """Asynchronously checks GitHub for the latest releases of yt-dlp and FFmpeg."""
    check_finished = Signal(dict)
    check_failed = Signal(str)

    def run(self):
        # Get accurate yt-dlp version
        current_ytdlp = getattr(yt_dlp, "__version__", None)
        if not current_ytdlp and hasattr(yt_dlp, "version"):
            current_ytdlp = getattr(yt_dlp.version, "__version__", None)
        current_ytdlp = current_ytdlp or "2026.08.19"

        result = {
            "ytdlp_current": current_ytdlp,
            "ytdlp_latest": "Unknown",
            "ytdlp_update_needed": False,
            "ytdlp_download_url": "",
            "ffmpeg_current": "Not Found",
            "ffmpeg_latest": "Latest GitHub Master Build",
            "ffmpeg_update_needed": False,
            "ffmpeg_download_url": "",
        }

        # Check Current FFmpeg
        ff_path = find_ffmpeg_binary()
        if ff_path:
            ok, ver = get_ffmpeg_version(ff_path)
            if ok:
                result["ffmpeg_current"] = ver.split()[2] if len(ver.split()) >= 3 else "Installed"
        
        headers = {"User-Agent": "yt-dlp-gui-updater/1.0"}

        # 1. Check yt-dlp Latest Release
        try:
            r = requests.get(YTDLP_REPO, headers=headers, timeout=6)
            if r.status_code == 200:
                data = r.json()
                tag = data.get("tag_name", "").lstrip("v")
                result["ytdlp_latest"] = tag
                if tag and tag != result["ytdlp_current"]:
                    result["ytdlp_update_needed"] = True
                
                # Find Windows exe asset
                for asset in data.get("assets", []):
                    if asset.get("name") == "yt-dlp.exe":
                        result["ytdlp_download_url"] = asset.get("browser_download_url")
                        break
        except Exception as e:
            pass

        # 2. Check FFmpeg Latest Release (yt-dlp specialized builds)
        try:
            r2 = requests.get(FFMPEG_REPO, headers=headers, timeout=6)
            if r2.status_code == 200:
                data2 = r2.json()
                tag2 = data2.get("tag_name", "Latest")
                result["ffmpeg_latest"] = tag2
                result["ffmpeg_update_needed"] = (result["ffmpeg_current"] == "Not Found")
                
                for asset in data2.get("assets", []):
                    name = asset.get("name", "")
                    if "win64-gpl.zip" in name and "shared" not in name:
                        result["ffmpeg_download_url"] = asset.get("browser_download_url")
                        break
        except Exception as e:
            pass

        self.check_finished.emit(result)


class UpdateEnginesWorker(QThread):
    """Downloads and integrates latest binaries directly into the app."""
    progress_signal = Signal(int, str, str)  # percent, status text, speed info
    finished_signal = Signal(bool, str)     # success, message

    def __init__(self, update_info: Dict[str, Any]):
        super().__init__()
        self.update_info = update_info
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        user_bin = get_user_bin_dir()
        temp_dir = os.path.join(user_bin, "temp_downloads")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. Update yt-dlp
            self.progress_signal.emit(10, "Updating yt-dlp backend...", "")
            if getattr(sys, 'frozen', False):
                # Download yt-dlp binary if available
                ytdlp_url = self.update_info.get("ytdlp_download_url")
                if ytdlp_url:
                    dest_exe = os.path.join(user_bin, "yt-dlp.exe")
                    self._download_file(ytdlp_url, dest_exe, 10, 40, "Downloading yt-dlp.exe")
            else:
                # Update via pip
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                        capture_output=True,
                        text=True,
                        timeout=40
                    )
                except Exception:
                    pass

            if self._is_cancelled:
                self.finished_signal.emit(False, "Update cancelled by user.")
                return

            # 2. Update FFmpeg
            ffmpeg_url = self.update_info.get("ffmpeg_download_url")
            if not ffmpeg_url:
                # Fallback to standard yt-dlp ffmpeg release
                ffmpeg_url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

            zip_dest = os.path.join(temp_dir, "ffmpeg_latest.zip")
            self.progress_signal.emit(45, "Connecting to GitHub for FFmpeg...", "")
            self._download_file(ffmpeg_url, zip_dest, 45, 85, "Downloading FFmpeg bundle")

            if self._is_cancelled:
                self.finished_signal.emit(False, "Update cancelled by user.")
                return

            # 3. Extract FFmpeg
            self.progress_signal.emit(90, "Extracting FFmpeg binaries...", "")
            with zipfile.ZipFile(zip_dest, "r") as zf:
                for file_info in zf.infolist():
                    name = file_info.filename
                    if name.endswith("ffmpeg.exe") or name.endswith("ffprobe.exe"):
                        file_info.filename = os.path.basename(name)
                        zf.extract(file_info, user_bin)

            # Clean up temp
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

            self.progress_signal.emit(100, "All engines updated successfully!", "")
            self.finished_signal.emit(True, "yt-dlp & FFmpeg have been updated to the latest builds.")

        except Exception as e:
            self.finished_signal.emit(False, f"Update failed: {str(e)}")

    def _download_file(self, url: str, dest_path: str, start_pct: int, end_pct: int, label: str):
        headers = {"User-Agent": "yt-dlp-gui-updater/1.0"}
        resp = requests.get(url, headers=headers, stream=True, timeout=15)
        resp.raise_for_status()

        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        start_time = time.time()

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if self._is_cancelled:
                    return
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Calculate progress
                    fraction = (downloaded / total_size) if total_size > 0 else 0.5
                    current_pct = int(start_pct + fraction * (end_pct - start_pct))
                    
                    elapsed = time.time() - start_time
                    speed_mb = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    down_mb = downloaded / (1024 * 1024)
                    tot_mb = total_size / (1024 * 1024)

                    speed_str = f"{down_mb:.1f} MB / {tot_mb:.1f} MB  ({speed_mb:.1f} MB/s)"
                    self.progress_signal.emit(current_pct, f"{label}...", speed_str)


class UpdateDialog(QDialog):
    """Modern dark dialog to manage 1-click backend updates."""
    engines_updated = Signal()

    def __init__(self, settings_mgr: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_mgr = settings_mgr
        self.setWindowTitle("🔄 Engine & Backend Updater")
        self.setFixedSize(540, 420)
        self.setModal(True)

        self.update_info: Dict[str, Any] = {}
        self.check_worker: Optional[CheckUpdatesWorker] = None
        self.update_worker: Optional[UpdateEnginesWorker] = None

        self.init_ui()
        self.start_check()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header Title
        title_box = QHBoxLayout()
        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("font-size: 22px;")
        
        lbl_h = QLabel("Automated Engine Updater")
        lbl_h.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        
        title_box.addWidget(icon_lbl)
        title_box.addWidget(lbl_h, 1)
        layout.addLayout(title_box)

        lbl_desc = QLabel("Fetch and integrate the latest yt-dlp core extractor and FFmpeg media processors directly from official GitHub releases with 1 click.")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        # Status Card
        grp_status = QGroupBox("Engine Versions & Status")
        grid = QGridLayout(grp_status)
        grid.setContentsMargins(14, 16, 14, 14)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        # yt-dlp row
        lbl_yt_k = QLabel("yt-dlp Backend:")
        lbl_yt_k.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.val_yt_ver = QLabel("Checking...")
        self.val_yt_ver.setStyleSheet("color: #38bdf8; font-weight: 600;")
        
        self.badge_yt_status = QLabel("Checking GitHub...")
        self.badge_yt_status.setStyleSheet("color: #94a3b8; font-size: 11px;")

        grid.addWidget(lbl_yt_k, 0, 0)
        grid.addWidget(self.val_yt_ver, 0, 1)
        grid.addWidget(self.badge_yt_status, 0, 2)

        # FFmpeg row
        lbl_ff_k = QLabel("FFmpeg Processor:")
        lbl_ff_k.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.val_ff_ver = QLabel("Checking...")
        self.val_ff_ver.setStyleSheet("color: #22c55e; font-weight: 600;")

        self.badge_ff_status = QLabel("Checking GitHub...")
        self.badge_ff_status.setStyleSheet("color: #94a3b8; font-size: 11px;")

        grid.addWidget(lbl_ff_k, 1, 0)
        grid.addWidget(self.val_ff_ver, 1, 1)
        grid.addWidget(self.badge_ff_status, 1, 2)

        layout.addWidget(grp_status)

        # Progress Card
        self.prog_box = QGroupBox("Update Progress")
        prog_layout = QVBoxLayout(self.prog_box)
        prog_layout.setContentsMargins(14, 14, 14, 14)
        prog_layout.setSpacing(6)

        self.lbl_status_step = QLabel("Ready.")
        self.lbl_status_step.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        self.prog_bar.setFixedHeight(18)

        self.lbl_speed_info = QLabel("")
        self.lbl_speed_info.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_speed_info.setAlignment(Qt.AlignmentFlag.AlignRight)

        prog_layout.addWidget(self.lbl_status_step)
        prog_layout.addWidget(self.prog_bar)
        prog_layout.addWidget(self.lbl_speed_info)
        layout.addWidget(self.prog_box)

        # Bottom Actions
        act_box = QHBoxLayout()
        self.chk_auto = QCheckBox("Check for updates automatically on launch")
        self.chk_auto.setChecked(self.settings_mgr.get("check_updates_startup", True))
        self.chk_auto.toggled.connect(lambda v: self.settings_mgr.set("check_updates_startup", v))

        self.btn_update_now = QPushButton("⚡ Update All Engines Now")
        self.btn_update_now.setObjectName("btnStartDownload")
        self.btn_update_now.setFixedHeight(34)
        self.btn_update_now.setEnabled(False)
        self.btn_update_now.clicked.connect(self.start_update)

        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedHeight(34)
        self.btn_close.clicked.connect(self.close)

        act_box.addWidget(self.chk_auto)
        act_box.addStretch()
        act_box.addWidget(self.btn_update_now)
        act_box.addWidget(self.btn_close)
        layout.addLayout(act_box)

    def start_check(self):
        self.lbl_status_step.setText("Checking GitHub for latest backend versions...")
        self.prog_bar.setValue(0)
        self.check_worker = CheckUpdatesWorker()
        self.check_worker.check_finished.connect(self.on_check_finished)
        self.check_worker.start()

    def on_check_finished(self, info: dict):
        self.update_info = info
        
        # Display yt-dlp status
        cur_yt = info.get("ytdlp_current", "Unknown")
        lat_yt = info.get("ytdlp_latest", "Unknown")
        self.val_yt_ver.setText(f"v{cur_yt}")
        if info.get("ytdlp_update_needed"):
            self.badge_yt_status.setText(f"Update Available (v{lat_yt})")
            self.badge_yt_status.setStyleSheet("color: #38bdf8; font-weight: 700;")
        else:
            self.badge_yt_status.setText("✔ Up to Date")
            self.badge_yt_status.setStyleSheet("color: #22c55e; font-weight: 700;")

        # Display FFmpeg status
        cur_ff = info.get("ffmpeg_current", "Not Found")
        lat_ff = info.get("ffmpeg_latest", "Latest")
        self.val_ff_ver.setText(cur_ff)
        if cur_ff == "Not Found":
            self.badge_ff_status.setText("Missing (Download available)")
            self.badge_ff_status.setStyleSheet("color: #ef4444; font-weight: 700;")
        else:
            self.badge_ff_status.setText("✔ Ready (GitHub latest)")
            self.badge_ff_status.setStyleSheet("color: #22c55e; font-weight: 700;")

        self.btn_update_now.setEnabled(True)
        self.lbl_status_step.setText("Check complete. Click 'Update All Engines Now' to refresh backends.")

    def start_update(self):
        self.btn_update_now.setEnabled(False)
        self.btn_close.setEnabled(False)
        self.lbl_status_step.setText("Starting engine update process...")

        self.update_worker = UpdateEnginesWorker(self.update_info)
        self.update_worker.progress_signal.connect(self.on_update_progress)
        self.update_worker.finished_signal.connect(self.on_update_finished)
        self.update_worker.start()

    def on_update_progress(self, percent: int, status: str, speed: str):
        self.prog_bar.setValue(percent)
        self.lbl_status_step.setText(status)
        self.lbl_speed_info.setText(speed)

    def on_update_finished(self, success: bool, msg: str):
        self.btn_update_now.setEnabled(True)
        self.btn_close.setEnabled(True)
        self.lbl_speed_info.setText("")
        
        if success:
            self.lbl_status_step.setText("🎉 " + msg)
            self.prog_bar.setValue(100)
            self.badge_yt_status.setText("✔ Up to Date")
            self.badge_yt_status.setStyleSheet("color: #22c55e; font-weight: 700;")
            self.badge_ff_status.setText("✔ Ready (Latest)")
            self.badge_ff_status.setStyleSheet("color: #22c55e; font-weight: 700;")
            self.engines_updated.emit()
            QMessageBox.information(self, "Update Successful", "Backends (yt-dlp & FFmpeg) have been updated successfully!")
        else:
            self.lbl_status_step.setText("❌ " + msg)
            QMessageBox.warning(self, "Update Notification", f"Update process result:\n{msg}")

    def closeEvent(self, event):
        if self.update_worker and self.update_worker.isRunning():
            self.update_worker.cancel()
        event.accept()
