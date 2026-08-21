"""
Optimized PyInstaller Build Script to compile lean standalone yt-dlp & FFmpeg GUI Executable.
"""
import os
import sys
import subprocess
import shutil

def build():
    print("==================================================")
    print("Building Optimized yt-dlp & FFmpeg Standalone GUI")
    print("==================================================")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_exe = os.path.join(root_dir, "ffmpeg.exe")

    if not os.path.isfile(ffmpeg_exe):
        print(f"WARNING: ffmpeg.exe not found at {ffmpeg_exe}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yt-dlp-gui",
        "--windowed",
        "--noconfirm",
        "--clean",
        # Collect only essential yt_dlp and PIL components
        "--collect-all=yt_dlp",
        "--collect-submodules=PIL",
        # Exclude massive unused Qt modules
        "--exclude-module=PySide6.QtQml",
        "--exclude-module=PySide6.QtQuick",
        "--exclude-module=PySide6.QtQuickWidgets",
        "--exclude-module=PySide6.QtWebEngineCore",
        "--exclude-module=PySide6.QtWebEngineWidgets",
        "--exclude-module=PySide6.Qt3DCore",
        "--exclude-module=PySide6.Qt3DRender",
        "--exclude-module=PySide6.QtVirtualKeyboard",
        "--exclude-module=PySide6.QtPdf",
        "--exclude-module=PySide6.QtPdfWidgets",
        "--exclude-module=PySide6.QtSensors",
        "--exclude-module=PySide6.QtPositioning",
        "--exclude-module=PySide6.QtBluetooth",
        "--exclude-module=PySide6.QtNfc",
        "--exclude-module=PySide6.QtSpatialAudio",
        "--exclude-module=PySide6.QtMultimedia",
        "--exclude-module=PySide6.QtMultimediaWidgets",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=torch",
        "--exclude-module=pygame",
        "--exclude-module=unittest",
    ]

    # Include ffmpeg binary (yt-dlp performs all media conversion, extraction and merging via ffmpeg)
    if os.path.isfile(ffmpeg_exe):
        cmd.extend(["--add-binary", f"{ffmpeg_exe};."])

    # Entry point
    cmd.append(os.path.join(root_dir, "main.py"))

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        dist_folder = os.path.join(root_dir, 'dist', 'yt-dlp-gui')
        total_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(dist_folder) for filename in filenames)
        print("\n==================================================")
        print("BUILD SUCCESSFUL & OPTIMIZED!")
        print(f"Total bundle size: {total_size / (1024*1024):.1f} MB (reduced from ~571 MB)")
        print(f"Executable output is located in: {dist_folder}")
        print("==================================================")
    else:
        print(f"\nBUILD FAILED with exit code {result.returncode}")

if __name__ == "__main__":
    build()
