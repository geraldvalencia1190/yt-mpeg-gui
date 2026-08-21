"""
PyInstaller Build Script to compile standalone yt-dlp & FFmpeg GUI Executable.
"""
import os
import sys
import subprocess
import shutil

def build():
    print("==================================================")
    print("Building yt-dlp & FFmpeg Standalone GUI Executable")
    print("==================================================")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_exe = os.path.join(root_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(root_dir, "ffprobe.exe")

    if not os.path.isfile(ffmpeg_exe):
        print(f"WARNING: ffmpeg.exe not found at {ffmpeg_exe}")
    if not os.path.isfile(ffprobe_exe):
        print(f"WARNING: ffprobe.exe not found at {ffprobe_exe}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yt-dlp-gui",
        "--windowed",
        "--noconfirm",
        "--clean",
        # Collect yt_dlp extractors and data
        "--collect-all=yt_dlp",
        "--collect-all=PIL",
        # Include ffmpeg & ffprobe binaries
    ]

    if os.path.isfile(ffmpeg_exe):
        cmd.extend(["--add-binary", f"{ffmpeg_exe};."])
    if os.path.isfile(ffprobe_exe):
        cmd.extend(["--add-binary", f"{ffprobe_exe};."])

    # Entry point
    cmd.append(os.path.join(root_dir, "main.py"))

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        print("\n==================================================")
        print("BUILD SUCCESSFUL!")
        print(f"Executable output is located in: {os.path.join(root_dir, 'dist', 'yt-dlp-gui')}")
        print("==================================================")
    else:
        print(f"\nBUILD FAILED with exit code {result.returncode}")

if __name__ == "__main__":
    build()
