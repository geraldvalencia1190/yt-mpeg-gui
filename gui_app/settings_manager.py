import os
import json
import time
from typing import Dict, Any, List
from pathlib import Path

class SettingsManager:
    DEFAULT_CONFIG = {
        "download_dir": str(Path.home() / "Downloads"),
        "default_mode": "video",
        "video_quality": "best",
        "video_format": "mp4",
        "audio_format": "mp3",
        "audio_bitrate": "320k",
        "embed_thumbnail": True,
        "embed_metadata": True,
        "embed_chapters": True,
        "embed_subtitles": False,
        "write_subtitles": False,
        "subtitles_languages": "en",
        "auto_subtitles": False,
        "sponsorblock_enabled": False,
        "sponsorblock_categories": ["sponsor", "selfpromo", "interaction"],
        "browser_cookies": "none",
        "custom_cookies_file": "",
        "rate_limit": "",
        "concurrent_fragments": 4,
        "proxy": "",
        "filename_template": "%(title)s [%(resolution)s].%(ext)s",
        "custom_args": "",
        "custom_ffmpeg_path": "",
        "theme": "dark_cyan"
    }

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".yt-mpeg-gui")
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.history_file = os.path.join(self.config_dir, "history.json")
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from json file with defaults fallback."""
        settings = dict(self.DEFAULT_CONFIG)
        if os.path.isfile(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    settings.update(data)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return settings

    def save_settings(self, new_settings: Dict[str, Any] = None):
        """Save settings to config file."""
        if new_settings:
            self.settings.update(new_settings)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()

    def load_history(self) -> List[Dict[str, Any]]:
        """Load list of downloaded items."""
        if os.path.isfile(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        return []

    def add_history_entry(self, entry: Dict[str, Any]):
        """Add a new history entry and save."""
        history = self.load_history()
        entry["timestamp"] = entry.get("timestamp", int(time.time()))
        # Insert at beginning
        history.insert(0, entry)
        # Keep latest 200 items
        history = history[:200]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def clear_history(self):
        """Clear all history entries."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        except Exception as e:
            print(f"Error clearing history: {e}")

    def remove_history_entry(self, entry_id: str):
        """Remove a specific entry from history."""
        history = self.load_history()
        history = [item for item in history if item.get("id") != entry_id]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error updating history: {e}")
