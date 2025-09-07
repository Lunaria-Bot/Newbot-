# 🤖 Discord Bot

A simple and extensible Discord bot built with [discord.py](https://github.com/Rapptz/discord.py).  
Supports persistent cooldowns, DM notification preferences, and admin-only commands.

## 🚀 Features
- Persistent user settings (saved in JSON)
- Slash commands (`/settings`, `/reload`)
- Admin-only reload command
- Ready for expansion with new commands

## 🛠️ Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set your bot token as environment variable:  
   ```bash
   export DISCORD_BOT_TOKEN=your_token_here
   ```
4. Run: `python bot.py`
