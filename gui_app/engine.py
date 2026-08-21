import os
import sys
import time
import traceback
from typing import Dict, Any, Optional, List
from PySide6.QtCore import QThread, Signal, QObject
import yt_dlp

from gui_app.ffmpeg_finder import find_ffmpeg_binary, find_ffprobe_binary

class CustomYTDLPLogger:
    def __init__(self, callback):
        self.callback = callback

    def debug(self, msg):
        # yt-dlp sends info as debug sometimes
        if msg.startswith("[debug] "):
            self.callback("DEBUG", msg[8:])
        elif msg.startswith("[download] "):
            self.callback("INFO", msg)
        else:
            self.callback("INFO", msg)

    def info(self, msg):
        self.callback("INFO", msg)

    def warning(self, msg):
        self.callback("WARNING", msg)

    def error(self, msg):
        self.callback("ERROR", msg)


class InfoWorker(QThread):
    """Worker thread to extract video metadata without downloading."""
    info_ready = Signal(dict)
    info_error = Signal(str)
    log_signal = Signal(str, str)

    def __init__(self, url: str, settings: Dict[str, Any]):
        super().__init__()
        self.url = url.strip()
        self.settings = settings

    def run(self):
        try:
            ffmpeg_path = find_ffmpeg_binary(self.settings.get("custom_ffmpeg_path"))
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
                'skip_download': True,
                'logger': CustomYTDLPLogger(lambda lvl, msg: self.log_signal.emit(lvl, msg)),
            }

            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path

            # Proxy
            proxy = self.settings.get("proxy", "").strip()
            if proxy:
                ydl_opts['proxy'] = proxy

            # Cookies
            browser = self.settings.get("browser_cookies", "none")
            if browser and browser not in ("none", "custom_file"):
                ydl_opts['cookiesfrombrowser'] = (browser,)
            elif browser == "custom_file":
                cookie_file = self.settings.get("custom_cookies_file", "")
                if cookie_file and os.path.isfile(cookie_file):
                    ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                if not info:
                    self.info_error.emit("Could not extract media info.")
                    return

                # Process formats
                formats_summary = []
                if "formats" in info:
                    seen_res = set()
                    for f in info.get("formats", []):
                        height = f.get("height")
                        ext = f.get("ext")
                        fps = f.get("fps")
                        vcodec = f.get("vcodec")
                        acodec = f.get("acodec")
                        
                        if height and vcodec != 'none':
                            res_str = f"{height}p"
                            if fps and fps > 30:
                                res_str += f"{fps}"
                            if res_str not in seen_res:
                                seen_res.add(res_str)
                                formats_summary.append({
                                    "format_id": f.get("format_id"),
                                    "resolution": res_str,
                                    "height": height,
                                    "ext": ext,
                                    "filesize": f.get("filesize") or f.get("filesize_approx") or 0,
                                    "vcodec": vcodec,
                                    "acodec": acodec,
                                })
                    # Sort formats descending by height
                    formats_summary.sort(key=lambda x: x.get("height", 0), reverse=True)

                is_playlist = info.get("_type") == "playlist" or "entries" in info
                entry_count = len(list(info.get("entries", []))) if is_playlist else 1

                result = {
                    "url": self.url,
                    "id": info.get("id", ""),
                    "title": info.get("title", "Unknown Title"),
                    "uploader": info.get("uploader") or info.get("channel") or "Unknown Channel",
                    "duration": info.get("duration", 0),
                    "duration_string": info.get("duration_string", ""),
                    "thumbnail": info.get("thumbnail", ""),
                    "description": info.get("description", ""),
                    "view_count": info.get("view_count", 0),
                    "is_playlist": is_playlist,
                    "entry_count": entry_count,
                    "formats": formats_summary,
                    "webpage_url": info.get("webpage_url", self.url),
                }
                self.info_ready.emit(result)

        except Exception as e:
            err = traceback.format_exc()
            self.info_error.emit(str(e))
            self.log_signal.emit("ERROR", f"Extraction error: {err}")


class DownloadWorker(QThread):
    """Worker thread that processes downloads asynchronously with progress hooks."""
    progress_signal = Signal(dict)
    log_signal = Signal(str, str)
    task_finished = Signal(dict)
    task_failed = Signal(str, str)
    all_finished = Signal()

    def __init__(self, tasks: List[Dict[str, Any]], global_settings: Dict[str, Any]):
        super().__init__()
        self.tasks = tasks
        self.settings = global_settings
        self._is_cancelled = False
        self._current_ydl = None

    def cancel(self):
        """Cancel ongoing downloads."""
        self._is_cancelled = True
        self.log_signal.emit("WARNING", "Cancelling download operations...")

    def _progress_hook(self, d: Dict[str, Any]):
        if self._is_cancelled:
            raise Exception("Download cancelled by user.")

        status = d.get("status")
        
        # Calculate nice numbers
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        speed = d.get("speed", 0)
        eta = d.get("eta", 0)
        
        percent = 0.0
        if total > 0:
            percent = (downloaded / total) * 100.0
        elif "_percent_str" in d:
            try:
                p_str = d["_percent_str"].replace("%", "").strip()
                percent = float(p_str)
            except Exception:
                percent = 0.0

        filename = os.path.basename(d.get("filename", ""))

        payload = {
            "status": status,
            "filename": filename,
            "downloaded_bytes": downloaded,
            "total_bytes": total,
            "percent": percent,
            "speed": speed or 0,
            "eta": eta or 0,
            "elapsed": d.get("elapsed", 0),
        }
        self.progress_signal.emit(payload)

    def _postprocessor_hook(self, d: Dict[str, Any]):
        if self._is_cancelled:
            raise Exception("Download cancelled by user.")
        
        status = d.get("status")
        postprocessor = d.get("postprocessor")
        if status == "started":
            self.log_signal.emit("INFO", f"Post-processing with {postprocessor}...")
            self.progress_signal.emit({
                "status": "processing",
                "percent": 99.0,
                "filename": f"Processing: {postprocessor}"
            })
        elif status == "finished":
            self.log_signal.emit("INFO", f"Post-processing finished: {postprocessor}")

    def build_ydl_opts(self, task_options: Dict[str, Any]) -> Dict[str, Any]:
        """Construct yt-dlp options dictionary combining task & global settings."""
        # Merge settings with task override
        opts = dict(self.settings)
        opts.update(task_options)

        download_dir = opts.get("download_dir", os.path.expanduser("~/Downloads"))
        os.makedirs(download_dir, exist_ok=True)

        template = opts.get("filename_template", "%(title)s.%(ext)s")
        outtmpl = os.path.join(download_dir, template)

        ffmpeg_path = find_ffmpeg_binary(opts.get("custom_ffmpeg_path"))

        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'logger': CustomYTDLPLogger(lambda lvl, msg: self.log_signal.emit(lvl, msg)),
            'progress_hooks': [self._progress_hook],
            'postprocessor_hooks': [self._postprocessor_hook],
            'noplaylist': opts.get("noplaylist", True),
            'ignoreerrors': True,
        }

        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
            self.log_signal.emit("INFO", f"Using FFmpeg at: {ffmpeg_path}")
        else:
            self.log_signal.emit("WARNING", "FFmpeg binary not detected! Some merges/conversions may fail.")

        # Mode: Video or Audio
        mode = opts.get("mode", "video")
        
        if mode == "audio":
            audio_format = opts.get("audio_format", "mp3")
            audio_bitrate = opts.get("audio_bitrate", "320k").replace("k", "")
            
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_bitrate,
            }]
        else:
            # Video mode
            quality = opts.get("video_quality", "best")
            video_format = opts.get("video_format", "mp4")

            if quality == "best":
                ydl_opts['format'] = f"bestvideo+bestaudio/best"
            else:
                # e.g., '1080p', '720p', '2160p'
                h = quality.replace("p", "").strip()
                ydl_opts['format'] = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"

            if video_format and video_format != "auto":
                ydl_opts['merge_output_format'] = video_format

        # Post-processing options
        postprocessors = ydl_opts.get('postprocessors', [])

        # Embed Thumbnail
        if opts.get("embed_thumbnail", True):
            ydl_opts['writethumbnail'] = True
            postprocessors.append({'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'})
            postprocessors.append({'key': 'EmbedThumbnail', 'already_have_thumbnail': False})

        # Embed Metadata / Tags
        if opts.get("embed_metadata", True):
            postprocessors.append({'key': 'FFmpegMetadata', 'add_chapters': opts.get("embed_chapters", True)})

        # Subtitles
        if opts.get("embed_subtitles", False) or opts.get("write_subtitles", False):
            ydl_opts['writesubtitles'] = True
            if opts.get("auto_subtitles", False):
                ydl_opts['writeautomaticsub'] = True
            
            sub_langs = opts.get("subtitles_languages", "en")
            if isinstance(sub_langs, str):
                ydl_opts['subtitleslangs'] = [lang.strip() for lang in sub_langs.split(",") if lang.strip()]
            elif isinstance(sub_langs, list):
                ydl_opts['subtitleslangs'] = sub_langs

            if opts.get("embed_subtitles", False):
                postprocessors.append({'key': 'FFmpegEmbedSubtitle'})

        # SponsorBlock
        if opts.get("sponsorblock_enabled", False):
            cats = opts.get("sponsorblock_categories", ["sponsor"])
            if cats:
                postprocessors.append({
                    'key': 'SponsorBlock',
                    'categories': set(cats),
                    'when': 'after_filter'
                })
                postprocessors.append({
                    'key': 'ModifyChapters',
                    'remove_sponsor_segments': set(cats)
                })

        ydl_opts['postprocessors'] = postprocessors

        # Rate Limit
        rate_limit = opts.get("rate_limit", "").strip()
        if rate_limit:
            # Parse e.g. 5M, 500K
            mult = 1
            if rate_limit.upper().endswith("K"):
                mult = 1024
                rate_limit = rate_limit[:-1]
            elif rate_limit.upper().endswith("M"):
                mult = 1024 * 1024
                rate_limit = rate_limit[:-1]
            try:
                ydl_opts['ratelimit'] = int(float(rate_limit) * mult)
            except Exception:
                pass

        # Concurrent fragments
        conc = opts.get("concurrent_fragments", 4)
        if conc and conc > 1:
            ydl_opts['concurrent_fragment_downloads'] = int(conc)

        # Proxy
        proxy = opts.get("proxy", "").strip()
        if proxy:
            ydl_opts['proxy'] = proxy

        # Cookies
        browser = opts.get("browser_cookies", "none")
        if browser and browser not in ("none", "custom_file"):
            ydl_opts['cookiesfrombrowser'] = (browser,)
        elif browser == "custom_file":
            cookie_file = opts.get("custom_cookies_file", "")
            if cookie_file and os.path.isfile(cookie_file):
                ydl_opts['cookiefile'] = cookie_file

        return ydl_opts

    def run(self):
        for task in self.tasks:
            if self._is_cancelled:
                self.log_signal.emit("WARNING", "Download sequence cancelled.")
                break

            url = task.get("url")
            if not url:
                continue

            self.log_signal.emit("INFO", f"Starting download for: {url}")
            ydl_opts = self.build_ydl_opts(task)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self._current_ydl = ydl
                    info = ydl.extract_info(url, download=True)
                    
                    if info:
                        # Determine target file
                        filepath = ydl.prepare_filename(info)
                        if task.get("mode") == "audio":
                            audio_format = task.get("audio_format", "mp3")
                            base_no_ext, _ = os.path.splitext(filepath)
                            filepath = f"{base_no_ext}.{audio_format}"

                        file_size = 0
                        if os.path.isfile(filepath):
                            file_size = os.path.getsize(filepath)

                        result = {
                            "id": info.get("id", str(time.time())),
                            "url": url,
                            "title": info.get("title", task.get("title", "Completed Video")),
                            "channel": info.get("uploader") or info.get("channel", "Unknown"),
                            "duration": info.get("duration", 0),
                            "format": task.get("mode", "video") + (" (" + task.get("video_format", "mp4") + ")" if task.get("mode") == "video" else " (" + task.get("audio_format", "mp3") + ")"),
                            "file_path": filepath,
                            "file_size": file_size,
                            "thumbnail_url": info.get("thumbnail", task.get("thumbnail", "")),
                            "timestamp": int(time.time()),
                            "status": "Completed"
                        }
                        self.task_finished.emit(result)
                        self.log_signal.emit("INFO", f"Successfully downloaded: {info.get('title', url)}")

            except Exception as e:
                if self._is_cancelled:
                    self.log_signal.emit("WARNING", "Task stopped due to cancellation.")
                else:
                    err_msg = str(e)
                    self.log_signal.emit("ERROR", f"Download failed for {url}: {err_msg}")
                    self.task_failed.emit(url, err_msg)

        self.all_finished.emit()
