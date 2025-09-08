import os
import json
import time
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "data/botdata.json"
MAZOKU_BOT_ID = 1242388858897956906  # Mazoku bot ID

# --------------------------
# Persistence Helpers
# --------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"cooldowns": {}, "settings": {}, "alerts_role": None}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# --------------------------
# Discord Setup
# --------------------------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cooldown defaults
COOLDOWN_SECONDS = {
    "Refreshing Box": 60,
    "summon": 1800,
    "Premium pack": 60,
    "summer": 1800,
}

ALIASES = {
    "open-boxes": "Refreshing Box",
    "summon": "summon",
    "premium-pack": "Premium pack",
    "summer": "summer",
}

# --------------------------
# Utility
# --------------------------
def get_interaction_from_message(message: discord.Message):
    return getattr(message, "interaction_metadata", None)

async def notify_user(user: discord.User, message: str, channel: discord.TextChannel):
    user_id = str(user.id)
    settings = data.get("settings", {}).get(user_id, {"dm_enabled": True})

    if settings.get("dm_enabled", True):
        try:
            await user.send(message)
            return
        except discord.Forbidden:
            pass
    await channel.send(f"{user.mention} {message}")

# --------------------------
# Events
# --------------------------
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"📜 Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Failed to sync: {e}")
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_message(message: discord.Message):
    if message.author.id == bot.user.id:
        return

    # Debug
    print(f"[DEBUG] {message.author}: {message.content}")

    # High tier summon detector
    if "High Tier Summon" in message.content:
        role_id = data.get("alerts_role")
        if role_id:
            for member in message.guild.members:
                if role_id in [r.id for r in member.roles]:
                    try:
                        await member.send(
                            f"🌟 High Tier Summon detected!\nLink: {message.jump_url}"
                        )
                    except Exception:
                        pass

    # Only track Mazoku bot
    if message.author.bot and message.author.id == MAZOKU_BOT_ID:
        inter = get_interaction_from_message(message)
        if not inter:
            return

        cmd_name = getattr(inter, "name", None)
        user = getattr(inter, "user", None)
        if not cmd_name or not user:
            return

        canonical = ALIASES.get(cmd_name, cmd_name)
        if canonical not in COOLDOWN_SECONDS:
            return

        # Skip cooldown if response says no available items
        if (
            "No premium packs available to open." in message.content
            or "You can summon again in" in message.content
        ):
            return

        now = time.time()
        key = f"{user.id}:{canonical}"
        end = data["cooldowns"].get(key, 0)

        if end > now:
            remaining = int(end - now)
            await notify_user(user, f"⏳ Cooldown for {canonical}: {remaining}s left.", message.channel)
            return

        cd = COOLDOWN_SECONDS[canonical]
        data["cooldowns"][key] = now + cd
        save_data()

        await notify_user(user, f"⚡ Cooldown started for {canonical} ({cd} seconds).", message.channel)

        async def clear_cd():
            await asyncio.sleep(cd)
            if data["cooldowns"].get(key, 0) <= time.time():
                data["cooldowns"].pop(key, None)
                save_data()
                await notify_user(user, f"✅ Cooldown for {canonical} is over!", message.channel)

        asyncio.create_task(clear_cd())

# --------------------------
# Slash Commands
# --------------------------
@bot.tree.command(name="settings", description="Enable or disable DM notifications")
@app_commands.describe(dm_enabled="True = DM enabled, False = DM disabled")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data()
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}.", ephemeral=True
    )

@bot.tree.command(name="reload", description="Reload bot commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    try:
        await bot.tree.sync()
        await interaction.response.send_message("✅ Commands reloaded.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

@bot.tree.command(name="setrole", description="Set role for High Tier Summon alerts (Admin only)")
@app_commands.describe(role="The role to notify")
async def setrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    data["alerts_role"] = role.id
    save_data()
    await interaction.response.send_message(f"✅ High Tier Summon alerts will notify {role.mention}", ephemeral=True)

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
