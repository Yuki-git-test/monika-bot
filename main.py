import asyncio
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from constants.settings import YUKI_USER_ID
from constants.vn_allstars_constants import VNA_SERVER_ID
from utils.db.get_pg_pool import get_pg_pool
from utils.logs.pretty_log import pretty_log, set_monika_bot
from utils.cache.central_cache_loader import load_all_caches
from utils.schedule.scheduler import setup_schedulers
ALLOWED_GUILD_IDS = [VNA_SERVER_ID, 1220718310455250996]
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
#          ⚡ On Guild Join ⚡
# 🍑────────────────────────────────────────────
@bot.event
async def on_guild_join(guild: discord.Guild):
    bot_owner = bot.get_user(YUKI_USER_ID)
    try:
        guild_owner = guild.owner or await bot.fetch_user(guild.owner_id)
        owner_name = guild_owner.name if guild_owner else "Unknown"
        owner_id = guild_owner.id if guild_owner else "Unknown"

        # DM Yuki about the new guild
        if bot_owner:
            if guild.id in ALLOWED_GUILD_IDS:
                try:
                    await bot_owner.send(
                        f"Joined new guild: {guild.name} (ID: {guild.id})\n"
                        f"Owner: {owner_name} (ID: {owner_id})\n"
                        f"Member Count: {guild.member_count}"
                    )
                    pretty_log(
                        message=f"📥 Notified Yuki about new guild join: {guild.name} (ID: {guild.id})"
                    )
                except Exception as e:
                    pretty_log(
                        message=f"❌ Failed to DM Yuki about new guild join: {e}",
                        tag="error",
                    )
            else:
                try:
                    await bot_owner.send(
                        f"Joined unauthorized guild: {guild.name} (ID: {guild.id})\n"
                        f"Owner: {owner_name} (ID: {owner_id})\n"
                        f"Member Count: {guild.member_count}\n"
                        f"Leaving guild..."
                    )
                    pretty_log(
                        message=f"📥 Notified Yuki about unapproved guild join: {guild.name} (ID: {guild.id})"
                    )
                except Exception as e:
                    pretty_log(
                        message=f"❌ Failed to DM Yuki about unapproved guild join: {e}",
                        tag="error",
                    )
                # Send a dm to the guild owner first
                if guild_owner:
                    try:
                        await guild_owner.send(
                            f"Hello! I am Monika, a bot designed to assist with VN Allstars server management. "
                            f"However, I am not authorized to be in your server ({guild.name}). "
                            f"I will be leaving shortly. If you believe this is a mistake, please contact my owner."
                        )
                        pretty_log(
                            message=f"📥 Notified guild owner about leaving: {owner_name} (ID: {owner_id})"
                        )
                    except Exception as e:
                        pretty_log(
                            message=f"❌ Failed to DM guild owner about leaving: {e}",
                            tag="error",
                        )
                await guild.leave()
                pretty_log(
                    message=f"🚪 Left unapproved guild: {guild.name} (ID: {guild.id})"
                )
                #

    except Exception as e:
        pretty_log(
            message=f"❌ Error handling guild join for {guild.name} (ID: {guild.id}): {e}",
            tag="error",
        )


# 🍑────────────────────────────────────────────
#          ⚡ Hourly Cache Refresh Task ⚡
# 🍑────────────────────────────────────────────
@tasks.loop(hours=1)
async def refresh_all_caches():
    # Skip the very first run to avoid double loading at startup
    if not hasattr(refresh_all_caches, "has_run"):
        refresh_all_caches.has_run = True
        return

    await load_all_caches(bot)


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
    # pretty_log(message=f"📦 Extension Loading Summary:", tag="ready")
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

    # Load all caches immediately at startup
    await load_all_caches(bot)
    # Start the hourly cache refresh task
    if not refresh_all_caches.is_running():
        refresh_all_caches.start()
        pretty_log(message="✅ Started hourly cache refresh task", tag="ready")

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

    # Setup scheduled tasks
    await setup_schedulers(bot)

    token = os.getenv("DISCORD_TOKEN")
    await bot.start(token)


# 🍑────────────────────
#   🚀 Start Bot 🚀
# 🍑────────────────────
asyncio.run(main())
