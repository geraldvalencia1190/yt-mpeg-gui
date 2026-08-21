import os
import sys
import shutil
import subprocess
from typing import Optional, Tuple

def get_base_dir() -> str:
    """Get the base directory whether running from source or frozen PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_user_bin_dir() -> str:
    """Get the persistent user bin directory for auto-updated binaries."""
    bin_dir = os.path.join(os.path.expanduser("~"), ".yt-mpeg-gui", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    return bin_dir

def find_ffmpeg_binary(custom_path: Optional[str] = None) -> Optional[str]:
    """Find ffmpeg.exe path across updated user bin, bundled locations, custom settings, or system PATH."""
    # 1. Custom user path
    if custom_path and os.path.isfile(custom_path):
        return os.path.abspath(custom_path)
    if custom_path and os.path.isdir(custom_path):
        candidate = os.path.join(custom_path, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    # 2. Updated User Bin Directory (~/.yt-mpeg-gui/bin/)
    user_bin = get_user_bin_dir()
    user_ffmpeg = os.path.join(user_bin, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if os.path.isfile(user_ffmpeg):
        return os.path.abspath(user_ffmpeg)

    # 3. Frozen PyInstaller MEIPASS
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        meipass_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.isfile(meipass_ffmpeg):
            return os.path.abspath(meipass_ffmpeg)

    # 4. Next to executable or inside _internal
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        exe_ffmpeg = os.path.join(exe_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.isfile(exe_ffmpeg):
            return os.path.abspath(exe_ffmpeg)
        internal_ffmpeg = os.path.join(exe_dir, "_internal", "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.isfile(internal_ffmpeg):
            return os.path.abspath(internal_ffmpeg)

    # 5. Project root directory
    base_dir = get_base_dir()
    project_ffmpeg = os.path.join(base_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if os.path.isfile(project_ffmpeg):
        return os.path.abspath(project_ffmpeg)

    # 6. System PATH
    system_path = shutil.which("ffmpeg")
    if system_path:
        return os.path.abspath(system_path)

    return None

def find_ffprobe_binary(custom_path: Optional[str] = None) -> Optional[str]:
    """Find ffprobe.exe path across updated user bin, bundled locations, custom settings, or system PATH."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.abspath(custom_path)
    if custom_path and os.path.isdir(custom_path):
        candidate = os.path.join(custom_path, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    user_bin = get_user_bin_dir()
    user_ffprobe = os.path.join(user_bin, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    if os.path.isfile(user_ffprobe):
        return os.path.abspath(user_ffprobe)

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        meipass_ffprobe = os.path.join(sys._MEIPASS, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(meipass_ffprobe):
            return os.path.abspath(meipass_ffprobe)

    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        exe_ffprobe = os.path.join(exe_dir, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(exe_ffprobe):
            return os.path.abspath(exe_ffprobe)
        internal_ffprobe = os.path.join(exe_dir, "_internal", "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(internal_ffprobe):
            return os.path.abspath(internal_ffprobe)

    base_dir = get_base_dir()
    project_ffprobe = os.path.join(base_dir, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    if os.path.isfile(project_ffprobe):
        return os.path.abspath(project_ffprobe)

    system_path = shutil.which("ffprobe")
    if system_path:
        return os.path.abspath(system_path)

    return None

def get_ffmpeg_version(ffmpeg_path: Optional[str] = None) -> Tuple[bool, str]:
    """Retrieve the version string of FFmpeg binary."""
    path = ffmpeg_path or find_ffmpeg_binary()
    if not path or not os.path.isfile(path):
        return False, "Not Found"
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        proc = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            startupinfo=startupinfo,
            encoding="utf-8",
            errors="ignore"
        )
        if proc.returncode == 0 and proc.stdout:
            first_line = proc.stdout.splitlines()[0]
            return True, first_line
        return False, "Failed to execute"
    except Exception as e:
        return False, str(e)
