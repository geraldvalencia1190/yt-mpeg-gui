# ⚡ yt-dlp & FFmpeg GUI Studio (`yt-mpeg-gui`)

A modern, high-performance, dark-themed Desktop GUI for Windows combining the power of **yt-dlp** and **FFmpeg** into a unified, standalone application.

---

## 🌟 Key Features

- 🎥 **Universal Media Downloader**: Supports YouTube, TikTok, Instagram, Twitter/X, Reddit, Twitch, Vimeo, and 1000+ websites.
- ⚡ **Embedded FFmpeg Engine**: Bundles full `ffmpeg.exe` for high-speed audio-video merging, stream remuxing, subtitle embedding, and metadata processing.
- 🔍 **Instant Media Inspection**: Live thumbnail preview, channel details, duration, view count, and available resolution options before downloading.
- ⏸️ **Live Pause & Resume**: Pause and resume downloads on the fly without socket timeouts or losing downloaded bytes.
- 🔄 **1-Click Engine Updater**: In-app automated backend updater that fetches and integrates latest releases of yt-dlp and FFmpeg directly from GitHub.
- 📦 **Rich Format & Quality Controls**:
  - **Video + Audio**: Best Quality (auto-merged), 4K Ultra HD (2160p), 2K Quad HD (1440p), 1080p FHD, 720p HD, 480p, 360p.
  - **Containers**: MP4, MKV, WEBM, AVI, MOV.
  - **Audio Extraction**: Lossless FLAC, WAV, MP3 (320kbps / 256kbps / 192kbps / 128kbps), M4A (AAC), OPUS.
- 📋 **Batch Queue Manager**: Import multiple URLs simultaneously with individual progress tracking, pause, resume, and bulk actions.
- 💬 **Subtitles & Metadata**: Embed subtitles or export `.srt`/`.vtt` files, embed video thumbnails into audio/video tags, and embed chapter markers.
- 🛡️ **SponsorBlock Integration**: Automatically remove sponsor segments, intros, outros, and self-promos.
- 🍪 **Cookie & Authentication**: Extract cookies directly from installed browsers (Chrome, Edge, Firefox, Brave, Opera, Vivaldi) or custom `cookies.txt` files for private / member-only / age-restricted content.
- 🌐 **Network & Speed**: Download rate limiting, concurrent fragment multi-threading, and custom proxy support (HTTP/HTTPS/SOCKS5).
- 📁 **Download History**: Integrated history browser with quick "Play File" and "Show in Folder" shortcuts.
- 📜 **Live Diagnostics Console**: Real-time colored yt-dlp & FFmpeg log viewer.

---

## 🚀 Quick Start (Running from Source)

### Requirements
- Python 3.10+
- PySide6, yt-dlp, Pillow, requests

### Installation

```bash
# 1. Clone repository
git clone https://github.com/hazynyx/yt-mpeg-gui.git
cd yt-mpeg-gui

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application
python main.py
```

---

## 🔨 Building Standalone Executable (.exe)

To compile a standalone Windows executable that packages the Python app, PySide6, `yt-dlp`, and `ffmpeg.exe`:

```bash
# 1. Build executable
python build_exe.py

# 2. (Optional) Create ready-to-upload ZIP for GitHub Releases
python package_release.py
```

The compiled application is generated in `dist/yt-dlp-gui/`, and the zip archive is saved to `dist/yt-dlp-gui-windows-x64.zip`.

---

## 📁 Project Structure

```
yt-mpeg-gui/
├── gui_app/
│   ├── __init__.py
│   ├── app.py                # Main window & application lifecycle
│   ├── assets/               # High-res logos & icons (.png, .ico)
│   ├── assets_manager.py     # Vector icon & UI asset provider
│   ├── engine.py             # Asynchronous yt-dlp & FFmpeg download worker
│   ├── ffmpeg_finder.py      # Binary locator for bundled & user FFmpeg
│   ├── settings_manager.py   # Persistent JSON config & history storage
│   ├── styles.py             # Modern Glassmorphic Dark stylesheet
│   ├── updater.py            # Automated GitHub engine updater & modal
│   └── widgets/
│       ├── __init__.py
│       ├── downloader_tab.py # Single URL analyzer & downloader
│       ├── queue_tab.py      # Batch URL downloader
│       ├── history_tab.py    # Download history manager
│       ├── settings_tab.py   # Comprehensive configuration panel
│       └── logs_tab.py       # Live diagnostics console
├── build_exe.py              # PyInstaller build automation script
├── package_release.py        # Release zip packager for GitHub Releases
├── main.py                   # Root entry launcher
├── requirements.txt          # Python dependencies
├── LICENSE                   # GNU GPL-3.0 License
└── .gitignore                # Git exclusions
```

---

## 📄 License & Legal Notice

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [LICENSE](LICENSE) file for complete details.

### Third-Party Software & Attributions
- **FFmpeg**: Licensed under the GNU General Public License (GPL) v2+/v3+. FFmpeg is a trademark of Fabrice Bellard, originator of the FFmpeg project. ([ffmpeg.org](https://ffmpeg.org))
- **yt-dlp**: Licensed under The Unlicense (Public Domain). ([github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp))
- **PySide6 / Qt6**: Licensed under LGPLv3. ([qt.io](https://www.qt.io))
