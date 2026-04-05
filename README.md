# 📸 InstaGrab Pro v2.0.0

### Premium Instagram Downloader Bot for Telegram
> Developed by **[ProofyGamerz](https://www.youtube.com/@ProofyGamerz)**

---

## ✨ Features

### 📥 Download Engine
- 📹  **Reels** — Full HD quality
- 🖼  **Posts & Images** — Original resolution
- 🎬  **IGTV / Videos** — Best available quality
- 📸  **Carousel Posts** — All media types
- 🎥  Video duration preview in Telegram player
- 🖼  Thumbnail support

### 🎨 Premium UI
- Clean, formatted messages with emojis
- Inline keyboard navigation
- Progress bar status updates
- Beautiful borders and sections
- ProofyGamerz branding

### 👤 User System
- Automatic user registration
- Personal download statistics
- Download history (last 10)
- User ranking system
- Rate limiting (5 downloads/min)
- Ban/Unban system

### 🛡️ Admin Panel
- `/admin` — Admin control panel
- `/broadcast <msg>` — Message all users
- `/ban <id>` — Ban a user
- `/unban <id>` — Unban a user
- Global bot statistics
- Top users leaderboard
- System info

### 🔒 Security
- Rate limiting per user
- Ban system
- Error tracking
- Input validation

---

## 🚀 Quick Setup

### 1. Get a Bot Token
1. Open Telegram → search **@BotFather**
2. Send `/newbot` → follow the prompts
3. Copy the **API Token**

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure
Edit `config.py`:
```python
BOT_TOKEN = "your_token_here"
ADMIN_IDS = [your_telegram_id]  # Optional — for admin panel
```

> 💡 Send `/id` to the bot to get your Telegram ID

### 4. Run
```bash
python bot.py
```

---

## 📋 Commands

| Command | Description |
|---|---|
| `/start` | 🏠 Main Menu with inline buttons |
| `/help` | 📖 How to use (with per-feature guides) |
| `/stats` | 📊 Personal download statistics |
| `/history` | 📜 Recent download history |
| `/settings` | ⚙️ Bot settings |
| `/about` | ℹ️ About & credits |
| `/id` | 🆔 Show your Telegram ID |

### Admin Commands
| Command | Description |
|---|---|
| `/admin` | 🛡️ Admin control panel |
| `/broadcast <msg>` | 📢 Send message to all users |
| `/ban <user_id>` | 🚫 Ban a user |
| `/unban <user_id>` | ✅ Unban a user |

---

## 📁 Project Structure

```
InstaGrab Pro/
├── bot.py          # Main bot — handlers & entry point
├── config.py       # Configuration & credentials
├── database.py     # SQLite database layer
├── downloader.py   # Instagram download engine
├── ui.py           # Premium UI messages & keyboards
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **python-telegram-bot 21.x** — Telegram Bot API
- **yt-dlp** — Instagram content extraction
- **SQLite** — Local database for stats & history

---

## 📜 Credits

**Developed by [ProofyGamerz](https://www.youtube.com/@ProofyGamerz)**

- 🎬 YouTube: [youtube.com/@ProofyGamerz](https://www.youtube.com/@ProofyGamerz)

---

## ⚠️ Notes

- Only **public** Instagram content can be downloaded
- Telegram file size limit: **50 MB**
- FFmpeg is **optional** (auto-detected)
- No proxies required
