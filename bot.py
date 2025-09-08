import os
import discord
from discord import app_commands
from discord.ext import commands

# Force sync to your server
GUILD_ID = 1399784437440319508  
HIGH_TIER_ROLE_ID = 1410321968279977985  
CAPTAIN_HOOK_ID = 1412644989908946954  

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"📜 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# /setrole command
@bot.tree.command(name="setrole", description="Set the role required for High Tier summon alerts")
@app_commands.describe(role="The role that should receive DM alerts")
async def setrole(interaction: discord.Interaction, role: discord.Role):
    global HIGH_TIER_ROLE_ID
    HIGH_TIER_ROLE_ID = role.id
    await interaction.response.send_message(
        f"✅ High Tier summon alerts will now DM members with the role: {role.mention}",
        ephemeral=True
    )

# Listen for High Tier summons
@bot.event
async def on_message(message: discord.Message):
    if message.author.id == CAPTAIN_HOOK_ID and "High Tier Summon" in message.content:
        guild = bot.get_guild(GUILD_ID)
        if guild is None:
            return
        
        role = guild.get_role(HIGH_TIER_ROLE_ID)
        if not role:
            return

        for member in role.members:
            try:
                await member.send(
                    f"⚠️ High Tier Summon detected!\n"
                    f"👉 [Jump to message]({message.jump_url})"
                )
            except discord.Forbidden:
                print(f"❌ Could not DM {member.display_name}")

    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)
