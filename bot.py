import os
import sys
import json
import discord
from discord import app_commands
from discord.ext import commands

# Ensure local imports work on Railway
sys.path.append(os.path.dirname(__file__))

from utils.storage import load_data, save_data

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

@bot.tree.command(name="settings", description="Update your DM preferences")
@app_commands.describe(dm_enabled="Enable or disable DM notifications (true/false)")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    if "settings" not in data:
        data["settings"] = {}
    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data(DATA_FILE, data)
    await interaction.response.send_message(f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}")

@bot.tree.command(name="reload", description="Reloads the bot's commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return
    try:
        await bot.tree.sync()
        await interaction.response.send_message("✅ Commands reloaded successfully.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
