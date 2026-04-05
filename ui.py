"""
╔══════════════════════════════════════════════════════╗
║   🎨  MediaGrab Pro — Premium UI Messages             ║
║   Systematic design system with consistent layout     ║
║   v3.1 — Unified headers, spacing, and structure      ║
╚══════════════════════════════════════════════════════╝
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    BOT_NAME, BOT_VERSION, DEVELOPER_NAME,
    DEVELOPER_CHANNEL, SUPPORT_LINK,
)
from downloader import format_size, format_duration
from lang import t, LANG_NAMES, QUALITY_NAMES, PLATFORM_NAMES


# ═════════════════════════════════════════════════════
#  DESIGN SYSTEM — Consistent building blocks
# ═════════════════════════════════════════════════════
#
#  Every message follows the same structure:
#    ┌─ HEADER ──────────────┐
#    │  ═══  icon  Title  ═══│
#    ├─ BODY ────────────────┤
#    │  Content sections     │
#    │  ─── divider ───      │
#    │  More content         │
#    ├─ FOOTER ──────────────┤
#    │  ⚡ Powered by ...    │
#    └───────────────────────┘

_W = 30  # Design width (characters)


def _header(icon: str, title: str) -> str:
    """Standard message header with double-line border."""
    return (
        f"{'═' * _W}\n"
        f"  {icon}  <b>{title}</b>\n"
        f"{'═' * _W}"
    )


def _divider() -> str:
    """Light section divider."""
    return f"{'─' * _W}"


def _footer() -> str:
    """Standard message footer with branding."""
    return f"<i>⚡ {BOT_NAME} by {DEVELOPER_NAME}</i>"


def _section(icon: str, title: str, body: str) -> str:
    """A labeled section with icon, bold title, and indented body."""
    return f"{icon}  <b>{title}</b>\n\n{body}"


def _field(icon: str, label: str, value: str) -> str:
    """A single key-value field line, right-aligned value."""
    return f"  {icon}  {label}:  <b>{value}</b>"


# ═════════════════════════════════════════════════════
#  KEYBOARDS
# ═════════════════════════════════════════════════════

def main_menu_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_how", lang), callback_data="help"),
            InlineKeyboardButton(t("btn_stats", lang), callback_data="stats"),
        ],
        [
            InlineKeyboardButton(t("btn_hist", lang), callback_data="history"),
            InlineKeyboardButton(t("btn_set", lang), callback_data="settings"),
        ],
        [
            InlineKeyboardButton(t("btn_dev", lang), url=DEVELOPER_CHANNEL),
            InlineKeyboardButton(t("btn_about", lang), callback_data="about"),
        ],
    ])


def back_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="start")],
    ])


def help_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_reels", lang), callback_data="help_reels"),
            InlineKeyboardButton(t("btn_yt", lang), callback_data="help_yt"),
        ],
        [
            InlineKeyboardButton(t("btn_pin", lang), callback_data="help_pin"),
            InlineKeyboardButton(t("btn_vid", lang), callback_data="help_vid"),
        ],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="start")],
    ])


def settings_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("set_quality", lang), callback_data="setting_quality")],
        [InlineKeyboardButton(t("set_lang", lang), callback_data="setting_lang")],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="start")],
    ])


def quality_settings_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("qp_best", lang), callback_data="setq_best")],
        [InlineKeyboardButton(t("qp_1080", lang), callback_data="setq_1080p")],
        [InlineKeyboardButton(t("qp_720", lang), callback_data="setq_720p")],
        [InlineKeyboardButton(t("qp_360", lang), callback_data="setq_360p")],
        [InlineKeyboardButton(t("qp_audio", lang) + " (MP3)", callback_data="setq_audio")],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="settings")],
    ])


def language_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_en", lang), callback_data="setlang_en")],
        [InlineKeyboardButton(t("btn_hi", lang), callback_data="setlang_hi")],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="settings")],
    ])


def quality_picker_keyboard(lang="en"):
    """Inline keyboard shown when user sends a link to pick download quality."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("qp_best", lang), callback_data="dl_best"),
            InlineKeyboardButton(t("qp_1080", lang), callback_data="dl_1080p"),
        ],
        [
            InlineKeyboardButton(t("qp_720", lang), callback_data="dl_720p"),
            InlineKeyboardButton(t("qp_360", lang), callback_data="dl_360p"),
        ],
        [
            InlineKeyboardButton(t("qp_audio", lang), callback_data="dl_audio"),
        ],
    ])


def admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Users", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔧 System", callback_data="admin_system"),
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")],
    ])


def after_download_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_stats", lang), callback_data="stats"),
            InlineKeyboardButton(t("btn_hist", lang), callback_data="history"),
        ],
        [
            InlineKeyboardButton(t("btn_rate", lang), url=DEVELOPER_CHANNEL),
        ],
    ])


def credit_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_yt_ch", lang), url=DEVELOPER_CHANNEL)],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="start")],
    ])


# ═════════════════════════════════════════════════════
#  MESSAGE TEMPLATES — Main Screens
# ═════════════════════════════════════════════════════

def welcome_message(first_name: str, lang="en") -> str:
    return (
        f"{_header('🎬', f'{BOT_NAME}  v{BOT_VERSION}')}\n\n"
        f"{t('welcome_greet', lang, name=first_name)}\n"
        f"{t('welcome_sub', lang)}\n\n"
        f"{_divider()}\n\n"
        f"<b>{t('welcome_feat', lang)}</b>\n\n"
        f"  {t('feat_reels', lang)}\n"
        f"  {t('feat_yt', lang)}\n"
        f"  {t('feat_shorts', lang)}\n"
        f"  {t('feat_pin', lang)}\n"
        f"  {t('feat_audio', lang)}\n\n"
        f"{_divider()}\n\n"
        f"{t('welcome_tip', lang)}\n\n"
        f"{_footer()}"
    )


def help_message(lang="en") -> str:
    return (
        f"{_header('📖', t('help_title', lang, bot=BOT_NAME))}\n\n"
        f"<b>📋  Quick Guide:</b>\n\n"
        f"  {t('help_steps', lang)}\n\n"
        f"{_divider()}\n\n"
        f"<b>{t('help_supported', lang)}</b>\n\n"
        f"  ✅  <b>Instagram</b> — Reels, Videos, IGTV\n"
        f"  ✅  <b>YouTube</b> — Videos, Shorts\n"
        f"  ✅  <b>Pinterest</b> — Pins\n\n"
        f"{_divider()}\n\n"
        f"<b>{t('help_limits_title', lang)}</b>\n\n"
        f"  {t('help_limit1', lang)}\n"
        f"  {t('help_limit2', lang)}\n"
        f"  {t('help_limit3', lang)}\n\n"
        f"{_footer()}"
    )


def _help_section_message(icon: str, title_key: str, steps_key: str,
                          example_key: str, features_key: str,
                          lang: str) -> str:
    """Generic help sub-section builder — eliminates copy-paste."""
    return (
        f"{_header(icon, t(title_key, lang))}\n\n"
        f"<b>📋  Steps:</b>\n\n"
        f"  {t(steps_key, lang)}\n\n"
        f"{_divider()}\n\n"
        f"<b>📎  Example:</b>\n"
        f"<code>{t(example_key, lang)}</code>\n\n"
        f"{_divider()}\n\n"
        f"<b>✨  Features:</b>\n"
        f"  {t(features_key, lang)}\n\n"
        f"{_footer()}"
    )


def help_reels_message(lang="en") -> str:
    return _help_section_message(
        "📹", "help_reels_title", "help_reels_steps",
        "help_reels_example", "help_reels_features", lang
    )


def help_youtube_message(lang="en") -> str:
    return _help_section_message(
        "🎬", "help_yt_title", "help_yt_steps",
        "help_yt_example", "help_yt_features", lang
    )


def help_pinterest_message(lang="en") -> str:
    return _help_section_message(
        "📌", "help_pin_title", "help_pin_steps",
        "help_pin_example", "help_pin_features", lang
    )


def help_videos_message(lang="en") -> str:
    return _help_section_message(
        "🎥", "help_vid_title", "help_vid_steps",
        "help_vid_example", "help_vid_features", lang
    )


# ═════════════════════════════════════════════════════
#  MESSAGE TEMPLATES — User Data Screens
# ═════════════════════════════════════════════════════

def quality_picker_message(platform: str, lang="en") -> str:
    pname = PLATFORM_NAMES.get(platform, platform.title())
    return (
        f"{_header('⚡', t('qp_title', lang))}\n\n"
        f"  {t('qp_detected', lang)}\n"
        f"  {t('qp_platform', lang, platform=pname)}\n\n"
        f"{_divider()}\n\n"
        f"  {t('qp_prompt', lang)}"
    )


def about_message(lang="en") -> str:
    return (
        f"{_header('ℹ️', t('about_title', lang, bot=BOT_NAME))}\n\n"
        f"  🤖  <b>{BOT_NAME}</b> v{BOT_VERSION}\n\n"
        f"  {t('about_desc', lang)}\n\n"
        f"{_divider()}\n\n"
        f"  👨‍💻  <b>{t('about_dev', lang)}</b>\n\n"
        f"     🎮  <b>{DEVELOPER_NAME}</b>\n"
        f"     🎬  <a href='{DEVELOPER_CHANNEL}'>YouTube Channel</a>\n\n"
        f"{_divider()}\n\n"
        f"  💝  <b>{t('about_support', lang)}</b>\n\n"
        f"  {t('about_support_txt', lang)}\n\n"
        f"{_divider()}\n\n"
        f"  📜  <b>{t('about_oss', lang)}</b>\n"
        f"  Built with ❤️ by {DEVELOPER_NAME}\n\n"
        f"{_footer()}"
    )


def stats_message(user_stats: dict, first_name: str, lang="en") -> str:
    total_size = format_size(user_stats["total_bytes"])
    rank_val = f"#{user_stats['rank']}"
    joined_val = user_stats["joined_at"][:10]
    return (
        f"{_header('📊', t('stats_title', lang))}\n\n"
        f"  👤  <b>{first_name}</b>\n\n"
        f"{_divider()}\n\n"
        f"{_field('📥', t('stats_total', lang), str(user_stats['total_downloads']))}\n"
        f"{_field('📹', t('stats_videos', lang), str(user_stats['videos']))}\n"
        f"{_field('🖼', t('stats_images', lang), str(user_stats['images']))}\n"
        f"{_field('🎵', t('stats_audios', lang), str(user_stats.get('audios', 0)))}\n"
        f"{_field('💾', t('stats_data', lang), total_size)}\n\n"
        f"{_divider()}\n\n"
        f"{_field('🏆', t('stats_rank', lang), rank_val)}\n"
        f"{_field('📅', t('stats_joined', lang), joined_val)}\n\n"
        f"{_footer()}"
    )


def history_message(history: list, lang="en") -> str:
    if not history:
        return (
            f"{_header('📜', t('hist_title', lang))}\n\n"
            f"  {t('hist_empty', lang)}\n\n"
            f"{_footer()}"
        )

    _plat_icons = {"instagram": "📸", "youtube": "🎬", "pinterest": "📌"}
    _type_icons = {"audio": "🎵", "image": "🖼", "video": "📹"}

    lines = [f"{_header('📜', t('hist_recent', lang))}\n"]

    for i, item in enumerate(history, 1):
        ct = item.get("content_type", "video")
        plat = item.get("platform", "instagram")
        icon = _type_icons.get(ct, "📹")
        plat_icon = _plat_icons.get(plat, "🔗")
        size = format_size(item.get("file_size", 0))
        date = item["downloaded_at"][:16].replace("T", " ")

        lines.append(
            f"\n  {icon}  <b>#{i}</b>  {plat_icon} {plat.title()}"
            f"\n     📦 {size}  •  📅 {date}"
        )

    lines.append(f"\n\n{_divider()}\n\n{_footer()}")
    return "\n".join(lines)


def settings_message(lang="en", current_quality="best", current_lang="en") -> str:
    qname = QUALITY_NAMES.get(current_quality, current_quality)
    lname = LANG_NAMES.get(current_lang, current_lang)
    return (
        f"{_header('⚙️', t('set_title', lang))}\n\n"
        f"  {t('set_sub', lang)}\n\n"
        f"{_divider()}\n\n"
        f"  {t('set_quality', lang)}\n"
        f"  ➜  {t('set_quality_current', lang, quality=qname)}\n\n"
        f"  {t('set_lang', lang)}\n"
        f"  ➜  {t('set_lang_current', lang, lang_name=lname)}\n\n"
        f"{_divider()}\n\n"
        f"{_footer()}"
    )


# ═════════════════════════════════════════════════════
#  DOWNLOAD STATUS MESSAGES
# ═════════════════════════════════════════════════════

def downloading_message(platform="instagram", lang="en") -> str:
    pname = PLATFORM_NAMES.get(platform, platform.title())
    return (
        f"{_header('📥', t('dl_downloading', lang))}\n\n"
        f"  {t('dl_fetching', lang, platform=pname)}\n\n"
        f"  ⏳ ░░░░░░░░░░░░░░░░\n\n"
        f"  <i>Please wait...</i>"
    )


def uploading_message(lang="en") -> str:
    return (
        f"{_header('📤', t('dl_uploading', lang))}\n\n"
        f"  {t('dl_sending', lang)}\n\n"
        f"  ⏳ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░\n\n"
        f"  <i>Almost there!</i>"
    )


def download_complete_caption(content_type: str, file_size: int,
                               duration: int = None, platform: str = "instagram",
                               lang="en") -> str:
    size = format_size(file_size)
    dur = format_duration(duration) if content_type in ("video", "audio") and duration else None
    pname = PLATFORM_NAMES.get(platform, platform.title())

    lines = [
        f"{t('dl_complete', lang)}\n",
        _divider(),
    ]

    lines.append(f"\n{_field('📦', 'Size', size)}")
    if dur:
        lines.append(f"\n{_field('⏱', 'Duration', dur)}")
    lines.append(f"\n{_field('📁', 'Type', content_type.title())}")
    lines.append(f"\n{_field('🔗', 'Source', pname)}")

    lines.append(f"\n{_divider()}\n")
    lines.append(f"\n⚡ <b>{BOT_NAME}</b> • by <a href='{DEVELOPER_CHANNEL}'>{DEVELOPER_NAME}</a>")

    return "\n".join(lines)


# ═════════════════════════════════════════════════════
#  ERROR MESSAGES — All use a consistent pattern
# ═════════════════════════════════════════════════════

def _error_message(icon: str, title_key: str, body_key: str,
                   lang: str, extra: str = "", **kwargs) -> str:
    """Generic error message builder — eliminates copy-paste."""
    parts = [
        f"{_header(icon, t(title_key, lang))}",
        f"\n\n  {t(body_key, lang, **kwargs)}",
    ]
    if extra:
        parts.append(f"\n\n{_divider()}\n\n{extra}")
    parts.append(f"\n\n{_footer()}")
    return "".join(parts)


def error_invalid_url(lang="en") -> str:
    supported = (
        "  <b>📎  Supported:</b>\n\n"
        "  • <b>Instagram</b> — Reels, Videos\n"
        "  • <b>YouTube</b> — Videos, Shorts\n"
        "  • <b>Pinterest</b> — Pins\n\n"
        f"  {t('err_invalid_tip', lang)}"
    )
    return _error_message("❌", "err_invalid_title", "err_invalid_body",
                          lang, extra=supported)


def error_private_content(lang="en") -> str:
    return _error_message("🔒", "err_private_title", "err_private_body", lang)


def error_not_found(lang="en") -> str:
    return _error_message("🔍", "err_notfound_title", "err_notfound_body", lang)


def error_too_large(file_size: int, lang="en") -> str:
    size = format_size(file_size)
    return _error_message("⚠️", "err_toolarge_title", "err_toolarge_body",
                          lang, size=size)


def error_rate_limit(lang="en") -> str:
    return _error_message("⏱", "err_ratelimit_title", "err_ratelimit_body", lang)


def error_banned(lang="en") -> str:
    return _error_message("🚫", "err_banned_title", "err_banned_body", lang)


def error_download_failed(error_msg: str, lang="en") -> str:
    return _error_message("❌", "err_dlfail_title", "err_dlfail_body", lang)


def error_upload_failed(lang="en") -> str:
    return _error_message("❌", "err_upfail_title", "err_upfail_body", lang)


# ═════════════════════════════════════════════════════
#  ADMIN MESSAGES
# ═════════════════════════════════════════════════════

def admin_panel_message() -> str:
    return (
        f"{_header('🛡️', 'Admin Panel')}\n\n"
        f"  Welcome, Administrator.\n\n"
        f"  Select an option below:\n\n"
        f"{_footer()}"
    )


def admin_stats_message(stats: dict) -> str:
    total_size = format_size(stats["total_bytes"])

    top_lines = ""
    for i, u in enumerate(stats.get("top_users", []), 1):
        name = u.get("first_name") or u.get("username") or str(u["user_id"])
        medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1] if i <= 5 else f"{i}."
        top_lines += f"  {medal}  {name} — <b>{u['total_downloads']}</b>\n"

    return (
        f"{_header('📊', 'Bot Statistics')}\n\n"
        f"  <b>👥  Users</b>\n\n"
        f"{_field('📋', 'Total', str(stats['total_users']))}\n"
        f"{_field('🟢', 'Active Today', str(stats['active_today']))}\n"
        f"{_field('🚫', 'Banned', str(stats['banned_users']))}\n\n"
        f"{_divider()}\n\n"
        f"  <b>📥  Downloads</b>\n\n"
        f"{_field('📋', 'Total', str(stats['total_downloads']))}\n"
        f"{_field('📅', 'Today', str(stats['downloads_today']))}\n"
        f"{_field('📹', 'Videos', str(stats['total_videos']))}\n"
        f"{_field('🖼', 'Images', str(stats['total_images']))}\n"
        f"{_field('🎵', 'Audios', str(stats.get('total_audios', 0)))}\n"
        f"{_field('❌', 'Failed', str(stats['failed_downloads']))}\n"
        f"{_field('💾', 'Total Size', total_size)}\n\n"
        f"{_divider()}\n\n"
        f"  <b>🏆  Top Users</b>\n\n"
        f"{top_lines}\n"
        f"{_footer()}"
    )
