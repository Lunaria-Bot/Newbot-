import os
import json
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "botdata.json"
HIGH_TIER_ROLE_ID = 1410321968279977985
CAPTAIN_HOOK_ID = 1412644989908946954

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"settings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

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
    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data(data)
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

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.author.id == CAPTAIN_HOOK_ID and "High Tier Summon" in (message.content or ""):
        for member in message.guild.members:
            if discord.utils.get(member.roles, id=HIGH_TIER_ROLE_ID):
                user_settings = data.get("settings", {}).get(str(member.id), {})
                if user_settings.get("dm_enabled"):
                    try:
                        await member.send(f"⚠️ High Tier Summon detected!
{message.jump_url}")
                    except Exception:
                        pass

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
