# ╔══════════════════════════════════════════════════════╗
# ║   🎬  MediaGrab Pro — Configuration                  ║
# ║   Developed by ProofyGamerz                          ║
# ╚══════════════════════════════════════════════════════╝

import os

# ─── Helpers ─────────────────────────────────────────
def _parse_admin_ids(value: str | None) -> list[int]:
    if not value:
        return []
    parts = [p.strip() for p in value.replace(";", ",").replace(" ", ",").split(",")]
    ids = []
    for p in parts:
        if not p:
            continue
        try:
            ids.append(int(p))
        except ValueError:
            pass
    return ids


# ─── Bot Token ───────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# ─── Admin Settings ──────────────────────────────────
ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS"))

# ─── Download Settings ───────────────────────────────
DOWNLOAD_DIR = "downloads"
MAX_FILE_SIZE = 50 * 1024 * 1024   # 50 MB (Telegram limit)
MAX_DOWNLOADS_PER_MINUTE = 5
MAX_CONCURRENT_DOWNLOADS = 3
MAX_DOWNLOAD_FOLDER_MB = 500
AUTO_CLEANUP_SECONDS = 300
MAX_FILE_AGE_SECONDS = 120
MAX_UPLOAD_RETRIES = 3

# ─── Database ────────────────────────────────────────
DATABASE_FILE = os.getenv("DATABASE_FILE", "mediagrab_pro.db")

# ─── Cookies (optional) ──────────────────────────────
# Path to a Netscape-format cookies.txt for Instagram/Pinterest access.
COOKIES_FILE = os.getenv("COOKIES_FILE", "")

# ─── Cobalt API (Free YouTube fallback) ──────────────
# Cobalt is a free, open-source video downloader that handles
# YouTube bot verification on their end. This is used as a
# fallback when yt-dlp is blocked by YouTube.
# Public:  https://api.cobalt.tools  (may need API key)
# Self-hosted: deploy your own at https://github.com/imputnet/cobalt
COBALT_API_URL = os.getenv("COBALT_API_URL", "https://api.cobalt.tools")
COBALT_API_KEY = os.getenv("COBALT_API_KEY", "")  # Optional API key

# ─── YouTube Proxy (optional) ────────────────────────
# Residential proxy for YouTube requests (if yt-dlp + Cobalt both fail)
# Format: http://user:pass@host:port  or  socks5://user:pass@host:port
YOUTUBE_PROXY = os.getenv("YOUTUBE_PROXY", "")

# ─── Bot Branding ────────────────────────────────────
BOT_NAME = "MediaGrab Pro"
BOT_VERSION = "3.0.0"
BOT_USERNAME = ""

# ─── Credits ─────────────────────────────────────────
DEVELOPER_NAME = "ProofyGamerz"
DEVELOPER_CHANNEL = "https://www.youtube.com/@ProofyGamerz"
DEVELOPER_TELEGRAM = ""

# ─── Messages ────────────────────────────────────────
SUPPORT_LINK = "https://www.youtube.com/@ProofyGamerz"

# ─── Quality Presets (yt-dlp format strings) ─────────
# Uses bestvideo+bestaudio for 720p+ to get separate HD video + audio
# streams merged by FFmpeg. Falls back to muxed "best" if FFmpeg missing.
QUALITY_OPTIONS = {
    "best":  "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio/best",
}

# Cobalt quality mapping (string values for Cobalt API)
COBALT_QUALITY_MAP = {
    "best": "1080",
    "1080p": "1080",
    "720p": "720",
    "360p": "360",
    "audio": "320",
}

# ─── Supported Languages ────────────────────────────
SUPPORTED_LANGUAGES = ["en", "hi"]
DEFAULT_LANGUAGE = "en"
