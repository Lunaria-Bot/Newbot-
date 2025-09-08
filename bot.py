import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# === File for saving data ===
DATA_FILE = "botdata.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"settings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# === Discord Intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Constants ===
CAPTAIN_HOOK_ID = 1412644989908946954   # Captain Hook bot ID
HIGH_TIER_ROLE_ID = 1410321968279977985 # High Tier Summon role ID

# === Events ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"📜 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_message(message: discord.Message):
    # Ignore bots except Captain Hook
    if message.author.bot and message.author.id != CAPTAIN_HOOK_ID:
        return

    # Detect High Tier Summon messages from Captain Hook
    if message.author.id == CAPTAIN_HOOK_ID and "High tier summon" in message.content:
        role = message.guild.get_role(HIGH_TIER_ROLE_ID)
        if not role:
            print("⚠️ High Tier Summon role not found in this guild.")
            return

        for member in role.members:
            user_settings = data.get("settings", {}).get(str(member.id), {"dm_enabled": True})
            if user_settings.get("dm_enabled", True):
                try:
                    await member.send(
                        f"🚨 High Tier Summon detected in {message.channel.mention}!\n{message.jump_url}"
                    )
                except discord.Forbidden:
                    print(f"❌ Could not DM {member} (DMs closed).")

    await bot.process_commands(message)

# === Slash Commands ===
@bot.tree.command(name="settings", description="Update your DM preferences")
@app_commands.describe(dm_enabled="Enable or disable DM notifications (true/false)")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    if "settings" not in data:
        data["settings"] = {}
    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data(data)
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}", ephemeral=True
    )

@bot.tree.command(name="reload", description="Reloads the bot's commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.", ephemeral=True
        )
        return
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(
            f"✅ Commands reloaded successfully. ({len(synced)} commands synced)",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

# === Main ===
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
