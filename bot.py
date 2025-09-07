# bot.py
import os
import json
import time
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "botdata.json"
MAZOKU_BOT_ID = 1242388858897956906  # Replace if different

# Default cooldowns (seconds)
DEFAULT_COOLDOWNS = {
    "Refreshing Box": 60,
    "summer": 1800,
    "summon": 1800,
    "Premium Pack": 60,
}

# ---------------------------
# Persistence Helpers
# ---------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"cooldowns": {}, "settings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ---------------------------
# Bot Setup
# ---------------------------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# In-memory cooldowns: (user_id, command) -> end_timestamp
cooldowns = {}

# ---------------------------
# Utility
# ---------------------------
def get_interaction_from_message(message: discord.Message):
    inter = getattr(message, "interaction_metadata", None)
    if not inter:
        inter = getattr(message, "interaction", None)  # fallback
    return inter

def user_dm_enabled(user_id: int) -> bool:
    return data.get("settings", {}).get(str(user_id), {}).get("dm_enabled", True)

# ---------------------------
# Events
# ---------------------------
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
    if message.author.id == bot.user.id:
        return

    if message.author.bot and message.author.id == MAZOKU_BOT_ID:
        inter = get_interaction_from_message(message)
        if not inter:
            return

        cmd_name = getattr(inter, "name", None)
        user = getattr(inter, "user", None)
        if not cmd_name or not user:
            return

        # Check if this is a tracked command
        if cmd_name not in DEFAULT_COOLDOWNS:
            return

        # Skip cooldowns based on message content
        if cmd_name == "Premium Pack" and "No premium packs available to open." in message.content:
            return
        if cmd_name == "summon" and "You can summon again in" in message.content:
            return

        now = time.time()
        key = (user.id, cmd_name)
        end = cooldowns.get(key, 0)

        if end > now:
            remaining = int(end - now)
            try:
                await message.channel.send(
                    f"⏳ {user.mention}, you're still on cooldown for {cmd_name} ({remaining}s left)."
                )
            except Exception:
                pass
            return

        # Start cooldown
        cd = DEFAULT_COOLDOWNS[cmd_name]
        cooldowns[key] = now + cd
        save_data(data)

        # Try sending DM
        if user_dm_enabled(user.id):
            try:
                await user.send(
                    f"⚡ Cooldown started for {cmd_name} — I'll remind you in {cd} seconds."
                )
            except discord.Forbidden:
                await message.channel.send(
                    f"⚡ {user.mention}, cooldown started for {cmd_name} — I'll remind you in {cd} seconds. (DMs blocked)"
                )
        else:
            await message.channel.send(
                f"⚡ {user.mention}, cooldown started for {cmd_name} — I'll remind you in {cd} seconds."
            )

        # Sleep and notify when cooldown ends
        await asyncio.sleep(cd)
        if cooldowns.get(key, 0) <= time.time():
            cooldowns.pop(key, None)
            try:
                if user_dm_enabled(user.id):
                    await user.send(f"✅ Your cooldown for {cmd_name} is over — you can use it again.")
                else:
                    await message.channel.send(f"✅ {user.mention}, cooldown for {cmd_name} is over!")
            except Exception:
                pass

# ---------------------------
# Slash Commands
# ---------------------------
@bot.tree.command(name="settings", description="Enable or disable DM notifications")
@app_commands.describe(dm_enabled="True = enable DMs, False = disable DMs")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    data.setdefault("settings", {})[user_id] = {"dm_enabled": dm_enabled}
    save_data(data)
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}",
        ephemeral=True
    )

@bot.tree.command(name="reload", description="Reload slash commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
        return
    try:
        if interaction.guild:
            await bot.tree.sync(guild=interaction.guild)
        else:
            await bot.tree.sync()
        await interaction.response.send_message("✅ Commands reloaded successfully.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

@bot.tree.command(name="checkcooldowns", description="Check your active cooldowns")
async def checkcooldowns(interaction: discord.Interaction):
    now = time.time()
    user_id = interaction.user.id
    active = []
    for (uid, cmd), end_time in cooldowns.items():
        if uid == user_id and end_time > now:
            active.append(f"{cmd}: {int(end_time - now)}s left")

    if not active:
        await interaction.response.send_message("✅ You have no active cooldowns.", ephemeral=True)
    else:
        await interaction.response.send_message("⏳ Active cooldowns:\n" + "\n".join(active), ephemeral=True)

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
