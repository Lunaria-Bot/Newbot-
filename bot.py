import os
import discord
from discord.ext import commands
from discord import app_commands

from utils.storage import load_data, save_data
from commands import settings, reload_cmd

DATA_FILE = "data/botdata.json"
data = load_data(DATA_FILE)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"📜 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Register commands
bot.tree.add_command(settings.settings)
bot.tree.add_command(reload_cmd.reload)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
