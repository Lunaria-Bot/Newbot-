import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# === CONFIG ===
DATA_FILE = "botdata.json"
GUILD_ID = 1399784437440319508  # replace with your server/guild ID
CAPTAIN_HOOK_ID = 1412644989908946954  # user who triggers High Tier Summon detection
HIGH_TIER_ROLE_ID = 1410321968279977985  # role required to receive DM alerts

# === STORAGE HELPERS ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"settings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# === BOT SETUP ===
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === EVENTS ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    try:
        # Clear global commands to avoid duplication
        await bot.tree.clear_commands(guild=None)
        await bot.tree.sync(guild=None)
        print("🧹 Cleared global commands.")

        # Sync commands to specific guild (instant availability)
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)

        print(f"📜 Synced {len(synced)} commands to guild {GUILD_ID}:")
        for cmd in synced:
            print(f"   • /{cmd.name} – {cmd.description}")

    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot and message.author.id == CAPTAIN_HOOK_ID:
        if "High Tier Summon" in message.content:
            guild = message.guild
            if not guild:
                return

            role = guild.get_role(HIGH_TIER_ROLE_ID)
            if not role:
                print(f"⚠️ Role {HIGH_TIER_ROLE_ID} not found in guild {guild.name}")
                return

            for member in role.members:
                try:
                    await member.send(
                        f"⚠️ High Tier Summon detected!\n"
                        f"🔗 [Jump to message]({message.jump_url})"
                    )
                except discord.Forbidden:
                    print(f"❌ Could not DM {member.display_name}")

# === SLASH COMMANDS ===
@bot.tree.command(name="settings", description="Update your DM preferences")
@app_commands.describe(dm_enabled="Enable or disable DM notifications (true/false)")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data(data)
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}",
        ephemeral=True
    )

@bot.tree.command(name="reload", description="Reloads the bot's commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        await interaction.response.send_message(
            f"✅ Commands reloaded. ({len(synced)} commands synced)",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

# === RUN ===
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
