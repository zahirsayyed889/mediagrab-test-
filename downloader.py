"""
╔══════════════════════════════════════════════════════╗
║   📥  MediaGrab Pro — Multi-Platform Download Engine  ║
║   Instagram • YouTube • Pinterest via yt-dlp          ║
║   + Cobalt API fallback (async aiohttp)               ║
║   v3.1 — Async Cobalt, storage mgmt, unique IDs      ║
╚══════════════════════════════════════════════════════╝
"""

import os
import re
import glob
import json
import time
import shutil
import asyncio
import logging
from pathlib import Path

import aiohttp
import yt_dlp

from config import (
    DOWNLOAD_DIR, MAX_FILE_SIZE,
    MAX_DOWNLOAD_FOLDER_MB, MAX_FILE_AGE_SECONDS,
    QUALITY_OPTIONS, COOKIES_FILE,
    COBALT_API_URL, COBALT_API_KEY, COBALT_QUALITY_MAP,
    YOUTUBE_PROXY,
)

logger = logging.getLogger(__name__)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_HAS_FFMPEG = bool(shutil.which("ffmpeg"))
_HAS_FFPROBE = bool(shutil.which("ffprobe"))


# ═════════════════════════════════════════════════════
#  STORAGE MANAGEMENT
# ═════════════════════════════════════════════════════

def get_folder_size_mb() -> float:
    total = 0
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try:
            total += os.path.getsize(f)
        except OSError:
            pass
    return total / (1024 * 1024)


def is_storage_safe() -> bool:
    return get_folder_size_mb() < MAX_DOWNLOAD_FOLDER_MB


def cleanup_old_files() -> int:
    """Remove files older than MAX_FILE_AGE_SECONDS. Returns count removed."""
    now = time.time()
    removed = 0
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try:
            if now - os.path.getmtime(f) > MAX_FILE_AGE_SECONDS:
                os.remove(f)
                removed += 1
        except OSError:
            pass
    if removed:
        logger.info(f"Cleaned up {removed} old files from downloads/")
    return removed


def cleanup_all_downloads():
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try:
            os.remove(f)
        except OSError:
            pass


def _ensure_storage():
    """Clean old files and check storage before downloading."""
    cleanup_old_files()
    if not is_storage_safe():
        logger.warning("Storage limit reached, cleaning all downloads")
        cleanup_all_downloads()


# ═════════════════════════════════════════════════════
#  UNIQUE DOWNLOAD IDs
# ═════════════════════════════════════════════════════

def make_download_prefix(chat_id: int, user_id: int = 0) -> str:
    """Create a unique prefix for download files to avoid collisions."""
    ts = int(time.time() * 1000) % 100000  # last 5 digits of ms timestamp
    return f"{chat_id}_{user_id}_{ts}"


# ═════════════════════════════════════════════════════
#  URL DETECTION — Multi-Platform
# ═════════════════════════════════════════════════════

INSTAGRAM_PATTERN = re.compile(
    r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/"
    r"(reel|p|tv|reels)/[\w\-]+",
    re.IGNORECASE,
)

INSTAGRAM_SHARE_PATTERN = re.compile(
    r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/share/[\w\-]+",
    re.IGNORECASE,
)

YOUTUBE_PATTERN = re.compile(
    r"(https?://)?(www\.|m\.)?"
    r"(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)"
    r"[\w\-]+",
    re.IGNORECASE,
)

PINTEREST_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(pinterest\.\w+/pin/[\w\-]+|pin\.it/[\w\-]+)",
    re.IGNORECASE,
)


def detect_platform(text: str) -> str | None:
    """Detect which platform a URL belongs to."""
    if INSTAGRAM_PATTERN.search(text) or INSTAGRAM_SHARE_PATTERN.search(text):
        return "instagram"
    if YOUTUBE_PATTERN.search(text):
        return "youtube"
    if PINTEREST_PATTERN.search(text):
        return "pinterest"
    return None


def extract_url(text: str) -> str | None:
    """Extract and clean a media URL from text."""
    for pattern in [INSTAGRAM_PATTERN, INSTAGRAM_SHARE_PATTERN,
                    YOUTUBE_PATTERN, PINTEREST_PATTERN]:
        match = pattern.search(text)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            # Keep query params for YouTube (v= is needed)
            if "youtube.com/watch" in url.lower():
                # Keep v= but strip tracking params
                parts = url.split("&")
                return parts[0]
            return url.split("?")[0]
    return None


# ═════════════════════════════════════════════════════
#  FILE UTILITIES
# ═════════════════════════════════════════════════════

def cleanup_files(pattern: str) -> None:
    for f in glob.glob(pattern):
        try:
            os.remove(f)
        except OSError:
            pass


def get_file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_duration(seconds: int | float | None) -> str:
    if seconds is None or seconds < 0:
        return "Unknown"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# ═════════════════════════════════════════════════════
#  MEDIA METADATA (via ffprobe)
# ═════════════════════════════════════════════════════

VIDEO_EXT = (".mp4", ".mkv", ".webm", ".mov", ".avi")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
AUDIO_EXT = (".mp3", ".m4a", ".ogg", ".opus", ".wav", ".aac", ".wma")


async def _get_media_metadata(filepath: str) -> dict:
    """Use ffprobe to extract duration, width, height from a media file."""
    meta = {}
    if not _HAS_FFPROBE:
        return meta
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
        data = json.loads(stdout.decode("utf-8"))

        # Duration from format section
        fmt = data.get("format", {})
        duration = fmt.get("duration")
        if duration:
            meta["duration"] = int(float(duration))

        # Width/height from first video stream
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                meta["width"] = stream.get("width")
                meta["height"] = stream.get("height")
                if not meta.get("duration") and stream.get("duration"):
                    meta["duration"] = int(float(stream["duration"]))
                break
    except Exception:
        pass
    return meta


# ═════════════════════════════════════════════════════
#  COBALT API — Async aiohttp Implementation
# ═════════════════════════════════════════════════════

_COBALT_FALLBACK_URLS = [
    "https://api.cobalt.tools",
]


def _is_bot_blocked_error(error_str: str) -> bool:
    """Check if an error string indicates YouTube bot verification blocking."""
    keywords = (
        "sign in", "bot", "captcha", "verify", "403",
        "confirm your identity", "not a bot", "consent",
        "automated", "unusual traffic", "please sign in",
        "this helps protect our community",
        "not available", "unavailable", "blocked",
    )
    err = error_str.lower()
    return any(k in err for k in keywords)


async def _cobalt_download(url: str, download_prefix: str,
                           quality: str = "best") -> dict:
    """
    Download via Cobalt API using async aiohttp — no thread pool blocking.
    """
    result = {
        "success": False,
        "type": "audio" if quality == "audio" else "video",
        "path": None,
        "thumbnail": None,
        "duration": None,
        "width": None,
        "height": None,
        "title": "",
        "error": None,
        "file_size": 0,
        "platform": "youtube",
    }

    # Build list of Cobalt URLs to try
    cobalt_urls = []
    if COBALT_API_URL:
        cobalt_urls.append(COBALT_API_URL)
    for fallback in _COBALT_FALLBACK_URLS:
        if fallback not in cobalt_urls:
            cobalt_urls.append(fallback)

    if not cobalt_urls:
        result["error"] = "No Cobalt API URLs configured"
        return result

    last_error = None
    timeout = aiohttp.ClientTimeout(total=210, connect=15, sock_read=180)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for api_url in cobalt_urls:
            try:
                logger.info(f"Trying Cobalt API: {api_url}")

                payload = {
                    "url": url,
                    "videoQuality": COBALT_QUALITY_MAP.get(quality, "1080"),
                    "filenameStyle": "basic",
                }
                if quality == "audio":
                    payload["isAudioOnly"] = True
                    payload["audioFormat"] = "mp3"

                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "MediaGrabPro/3.1",
                }
                if COBALT_API_KEY:
                    headers["Authorization"] = f"Api-Key {COBALT_API_KEY}"

                # POST to Cobalt API
                api_endpoint = api_url.rstrip("/")
                async with session.post(api_endpoint, json=payload, headers=headers) as resp:
                    data = await resp.json()

                status = data.get("status")

                if status in ("redirect", "tunnel", "stream"):
                    download_url = data.get("url")
                elif status == "picker":
                    picker = data.get("picker", [])
                    download_url = picker[0].get("url") if picker else None
                    if not download_url:
                        last_error = "Cobalt returned empty picker"
                        continue
                elif status == "error":
                    error_info = data.get("error", {})
                    if isinstance(error_info, dict):
                        error_msg = error_info.get("code", "unknown")
                    else:
                        error_msg = str(error_info)
                    last_error = f"Cobalt error: {error_msg}"
                    logger.warning(f"Cobalt {api_url} error: {error_msg}")
                    continue
                else:
                    last_error = f"Cobalt unexpected status: {status}"
                    continue

                if not download_url:
                    last_error = "Cobalt returned no download URL"
                    continue

                # Download the actual file — streamed to avoid memory issues
                ext = ".mp3" if quality == "audio" else ".mp4"
                output_path = os.path.join(DOWNLOAD_DIR, f"{download_prefix}_cobalt{ext}")

                dl_headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }

                async with session.get(download_url, headers=dl_headers) as dl_resp:
                    if dl_resp.status != 200:
                        last_error = f"Cobalt download HTTP {dl_resp.status}"
                        continue
                    with open(output_path, "wb") as f:
                        async for chunk in dl_resp.content.iter_chunked(1024 * 1024):
                            f.write(chunk)

                if os.path.isfile(output_path) and os.path.getsize(output_path) > 1000:
                    result["success"] = True
                    result["path"] = output_path
                    result["file_size"] = os.path.getsize(output_path)

                    try:
                        meta = await _get_media_metadata(output_path)
                        result["duration"] = meta.get("duration")
                        result["width"] = meta.get("width")
                        result["height"] = meta.get("height")
                    except Exception:
                        pass

                    logger.info(f"Cobalt download success: {result['file_size']} bytes")
                    return result
                else:
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                    last_error = "Downloaded file is empty or too small"
                    continue

            except aiohttp.ClientError as e:
                last_error = f"Cobalt connection error: {e}"
                logger.warning(f"Cobalt {api_url} connection error: {e}")
                continue
            except asyncio.TimeoutError:
                last_error = "Cobalt request timed out"
                logger.warning(f"Cobalt {api_url} timed out")
                continue
            except Exception as e:
                last_error = f"Cobalt error: {e}"
                logger.warning(f"Cobalt {api_url} error: {e}")
                continue

    result["error"] = last_error or "All Cobalt instances failed"
    return result


# ═════════════════════════════════════════════════════
#  YT-DLP DOWNLOAD ENGINE
# ═════════════════════════════════════════════════════

_YT_BYPASS_TIMEOUT = 25
DOWNLOAD_TIMEOUT = 300  # 5 minutes

_YT_BYPASS_STRATEGIES = [
    {
        "name": "TV Embedded",
        "player_client": ["tv_embedded"],
    },
    {
        "name": "Mobile Web",
        "player_client": ["mweb"],
    },
    {
        "name": "Android VR",
        "player_client": ["android_vr"],
    },
]


async def _ytdlp_download(url: str, download_prefix: str,
                          quality: str = "best",
                          platform: str = "instagram",
                          player_clients: list = None) -> dict:
    """
    Download media via yt-dlp.
    Uses download_prefix for unique file naming.
    """
    output_template = os.path.join(DOWNLOAD_DIR, f"{download_prefix}_%(id)s.%(ext)s")

    is_audio = (quality == "audio")
    format_str = QUALITY_OPTIONS.get(quality, QUALITY_OPTIONS["best"])

    # If no FFmpeg, fall back to muxed streams (max 720p but works)
    if not _HAS_FFMPEG and not is_audio:
        simple_formats = {
            "best": "best",
            "1080p": "best[height<=1080]/best",
            "720p": "best[height<=720]/best",
            "360p": "best[height<=360]/best",
        }
        format_str = simple_formats.get(quality, "best")

    ydl_opts = {
        "outtmpl": output_template,
        "noplaylist": True,
        "format": format_str,
        "socket_timeout": 20,
        "retries": 3,
        "fragment_retries": 5,
        "concurrent_fragment_downloads": 8,
        "buffersize": 1024 * 64,
        "http_chunk_size": 1024 * 1024 * 10,
        "nocheckcertificate": True,
        "noprogress": True,
        "no_warnings": True,
        "quiet": True,
        "extract_flat": False,
        "writethumbnail": False,
        "writesubtitles": False,
        "writeautomaticsub": False,
        "writedescription": False,
        "writeinfojson": False,
        "writeannotations": False,
        "geo_bypass": True,
    }

    # ── Cookies ─────────────────────────────────────
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    # ── Audio extraction ────────────────────────────
    if is_audio and _HAS_FFMPEG:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    elif not is_audio and _HAS_FFMPEG:
        ydl_opts["merge_output_format"] = "mp4"
        ydl_opts["postprocessors"] = [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ]

    # ── YouTube-specific optimizations ──────────────
    if platform == "youtube":
        ydl_opts["socket_timeout"] = 12
        ydl_opts["retries"] = 1

        clients = player_clients or ["default"]
        ydl_opts["extractor_args"] = {
            "youtube": {
                "player_client": clients,
            }
        }

        if YOUTUBE_PROXY:
            ydl_opts["proxy"] = YOUTUBE_PROXY

    result = {
        "success": False,
        "type": "audio" if is_audio else "video",
        "path": None,
        "thumbnail": None,
        "duration": None,
        "width": None,
        "height": None,
        "title": "",
        "error": None,
        "file_size": 0,
        "platform": platform,
    }

    try:
        loop = asyncio.get_running_loop()

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info) if info else None
                return info, filepath

        info, filepath = await loop.run_in_executor(None, _download)

        if info is None:
            result["error"] = "Could not extract content from this link."
            return result

        # ── Locate the downloaded file ──────────────
        downloaded_file = None

        if is_audio and _HAS_FFMPEG:
            base = os.path.splitext(filepath)[0] if filepath else \
                os.path.join(DOWNLOAD_DIR, f"{download_prefix}_unknown")
            for ext in AUDIO_EXT:
                candidate = base + ext
                if os.path.isfile(candidate):
                    downloaded_file = candidate
                    break

        if not downloaded_file:
            if filepath and os.path.isfile(filepath):
                downloaded_file = filepath
            else:
                base = os.path.splitext(filepath)[0] if filepath else \
                    os.path.join(DOWNLOAD_DIR, f"{download_prefix}_unknown")
                for ext in (*AUDIO_EXT, *VIDEO_EXT, *IMAGE_EXT):
                    candidate = base + ext
                    if os.path.isfile(candidate):
                        downloaded_file = candidate
                        break

        # Last resort: glob
        if not downloaded_file:
            candidates = [
                f for f in glob.glob(os.path.join(DOWNLOAD_DIR, f"{download_prefix}_*"))
                if not f.endswith((".json", ".part"))
            ]
            if candidates:
                downloaded_file = candidates[0]

        if not downloaded_file or not os.path.isfile(downloaded_file):
            result["error"] = "Download completed but file not found."
            return result

        # ── Fill result ──────────────────────────────
        ext_lower = Path(downloaded_file).suffix.lower()
        if is_audio or ext_lower in AUDIO_EXT:
            result["type"] = "audio"
        elif ext_lower in IMAGE_EXT:
            result["type"] = "image"
        else:
            result["type"] = "video"

        result["path"] = downloaded_file
        result["success"] = True
        result["file_size"] = get_file_size(downloaded_file)
        result["duration"] = info.get("duration")
        result["width"] = info.get("width")
        result["height"] = info.get("height")
        result["title"] = (
            info.get("title", "") or info.get("description", "") or ""
        )[:200]

        return result

    except yt_dlp.utils.DownloadError as e:
        err = str(e).lower()
        if any(k in err for k in ("private", "login", "authentication", "requires")):
            result["error"] = "private"
        elif "not found" in err or "404" in err:
            result["error"] = "not_found"
        else:
            result["error"] = f"Download failed: {e}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
        logger.exception("yt-dlp download error")
        return result


# ═════════════════════════════════════════════════════
#  MAIN DOWNLOAD ENGINE — Multi-Strategy with Fallback
# ═════════════════════════════════════════════════════

async def download_media(url: str, chat_id: int,
                         quality: str = "best",
                         platform: str = "instagram",
                         user_id: int = 0) -> dict:
    """
    Download media from Instagram/YouTube/Pinterest.
    For YouTube: tries multiple bypass strategies before Cobalt API.
    """
    # Ensure storage is healthy before downloading
    _ensure_storage()

    download_prefix = make_download_prefix(chat_id, user_id)

    if platform != "youtube":
        return await _ytdlp_download(url, download_prefix, quality, platform)

    # ═══════════════════════════════════════════════
    #  YOUTUBE — Multi-Strategy Bypass Chain
    # ═══════════════════════════════════════════════
    last_error = None
    total = len(_YT_BYPASS_STRATEGIES)

    for i, strategy in enumerate(_YT_BYPASS_STRATEGIES, 1):
        name = strategy["name"]
        clients = strategy["player_client"]

        logger.info(f"YouTube attempt {i}/{total}: "
                    f"{name} ({', '.join(clients)})")

        cleanup_files(os.path.join(DOWNLOAD_DIR, f"{download_prefix}_*"))

        try:
            result = await asyncio.wait_for(
                _ytdlp_download(
                    url, download_prefix, quality, platform,
                    player_clients=clients,
                ),
                timeout=_YT_BYPASS_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏱ Strategy [{name}] timed out after "
                           f"{_YT_BYPASS_TIMEOUT}s")
            last_error = f"Strategy {name} timed out"
            continue

        if result["success"]:
            logger.info(f"✅ YouTube download succeeded via yt-dlp "
                        f"[{name}] on attempt {i}")
            return result

        error_str = str(result.get("error", ""))
        last_error = error_str

        if not _is_bot_blocked_error(error_str):
            logger.info(f"YouTube error is not bot-related, "
                        f"stopping bypass attempts: {error_str[:100]}")
            return result

        logger.warning(f"❌ Strategy [{name}] blocked: {error_str[:80]}")

    # ── Phase 2: Cobalt API as last resort ──────────
    logger.warning("All yt-dlp bypass strategies failed. "
                   "Trying Cobalt API as last resort...")

    cleanup_files(os.path.join(DOWNLOAD_DIR, f"{download_prefix}_*"))

    cobalt_result = await _cobalt_download(url, download_prefix, quality)

    if cobalt_result["success"]:
        logger.info("✅ YouTube download succeeded via Cobalt API")
        return cobalt_result

    # ── Everything failed ───────────────────────────
    err_preview = (last_error or "unknown")[:100]
    logger.error(f"All YouTube strategies failed. "
                 f"Last yt-dlp error: {err_preview}")
    logger.error(f"Cobalt error: {cobalt_result.get('error')}")

    cobalt_result["error"] = (
        "YouTube is blocking downloads from this server.\n"
        f"Tried {total} bypass strategies + Cobalt API.\n\n"
        "💡 Solutions:\n"
        "• Set COBALT_API_KEY in Railway env vars\n"
        "• Add cookies.txt from a YouTube account\n"
        "• Use a residential proxy (YOUTUBE_PROXY env var)"
    )
    return cobalt_result
