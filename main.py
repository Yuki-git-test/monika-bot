import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from constants.vn_allstars_constants import VNA_SERVER_ID
from utils.db.get_pg_pool import get_pg_pool
from utils.logs.pretty_log import pretty_log, set_monika_bot

# 🍑────────────────────────────────────────────
#          ⚡ Bot Initialization ⚡
# 🍑────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)
set_monika_bot(bot=bot)


# 🍑────────────────────────────────────────────
#          ⚡ Load Extensions Dynamically ⚡
# 🍑────────────────────────────────────────────
async def load_extensions():
    """
    Dynamically load all Python files in the 'cogs' folder (ignores __pycache__).
    Displays a summary and count of loaded cogs.
    """
    loaded_cogs = []
    failed_cogs = []

    for root, dirs, files in os.walk("cogs"):
        # Skip __pycache__ folders
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = (
                    os.path.join(root, file).replace(os.sep, ".").replace(".py", "")
                )
                try:
                    await bot.load_extension(module_path)
                    loaded_cogs.append(module_path)
                except Exception as e:
                    failed_cogs.append((module_path, str(e)))

    # Display summary
    pretty_log(message=f"📦 Extension Loading Summary:", tag="ready")
    pretty_log(message=f"✅ Successfully loaded {len(loaded_cogs)} cog(s)", tag="ready")

    """if loaded_cogs:
        cog_list = ", ".join([cog.split(".")[-1] for cog in loaded_cogs])
        pretty_log(message=f"📋 Loaded cogs: {cog_list}", tag="ready")"""

    if failed_cogs:
        pretty_log(message=f"❌ Failed to load {len(failed_cogs)} cog(s)", tag="error")
        for cog, error in failed_cogs:
            pretty_log(message=f"  • {cog}: {error}", tag="error")


# 🍑────────────────────────────────────────────
#              ⚡ On Ready Event ⚡
# 🍑────────────────────────────────────────────
@bot.event
async def on_ready():
    pretty_log(message=f"✅ Logged in as {bot.user}", tag="ready")

    # Set bot presence
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Watching every channel… every message… I see it all ♡",
        )
    )

    # Sync all slash commands globally
    await bot.tree.sync()

    # Number of slash commands
    command_count = len(bot.tree.get_commands())
    pretty_log(message=f"{command_count} slash command(s) loaded", tag="ready")


# 🍑────────────────────────────────────────────
#               ⚡ Main Entry Point ⚡
# 🍑────────────────────────────────────────────
async def main():
    await load_extensions()
    # Load the PostgreSQL connection pool
    try:
        bot.pg_pool = await get_pg_pool()
        pretty_log(message="✅ PostgreSQL connection pool established", tag="ready")
    except Exception as e:
        pretty_log(
            message=f"❌ Failed to establish PostgreSQL connection pool: {e}",
            tag="error",
        )
        return
    token = os.getenv("DISCORD_TOKEN")
    await bot.start(token)


# 🍑────────────────────
#   🚀 Sttrt Bot 🚀
# 🍑────────────────────
asyncio.run(main())
