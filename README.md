# Discord Bot

A simple Discord bot with persistent settings and cooldowns.

## Setup

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your bot token:
   ```
   DISCORD_BOT_TOKEN=your_token_here
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Deploy to Railway

- Push this repo to GitHub.
- Link it with Railway.
- Add `DISCORD_BOT_TOKEN` as an environment variable in Railway dashboard.
