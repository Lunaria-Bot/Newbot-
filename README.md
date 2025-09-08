# Discord Summon Alert Bot

A Discord bot that:
- Detects "High Tier Summon" messages from Captain Hook (even inside embeds).
- Sends private DMs to members with the High Tier Summon role, if they have opted in with `/settings dm true`.
- Provides slash commands:
  - `/settings dm <true/false>` to enable or disable private DMs.
  - `/reload` to reload commands (admin only).

## Setup

1. Clone repo
2. Create a Discord bot & get your token
3. Add it as an environment variable in Railway/GitHub: `DISCORD_BOT_TOKEN`
4. Enable **MESSAGE CONTENT** and **SERVER MEMBERS** intents in the Developer Portal.
5. Deploy!

## Requirements
- Python 3.9+
- discord.py 2.3.2
