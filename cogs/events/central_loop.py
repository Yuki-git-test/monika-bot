import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from utils.logs.pretty_log import pretty_log
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VNA_SERVER_ID
)
from utils.background_loop.clan_break_checker import clan_break_checker

# 🍭──────────────────────────────
#  🎀 Central Loop
# Handles background tasks every 60 seconds
# 🍭──────────────────────────────
class CentralLoop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_task = None

    def cog_unload(self):
        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
            pretty_log(
                "background_task",
                "Central loop task has been cancelled.",
                label="Central Loop",
            )
    async def central_loop(self):
        """Main central loop that runs background tasks every 60 seconds."""
        await self.bot.wait_until_ready()
        pretty_log(
            "background_task",
            "Central loop has started.",
            label="Central Loop",
        )
        while not self.bot.is_closed():
            try:
                """pretty_log(
                    "background_task",
                    "🔄 Running background checks.."
                )"""
                # Check for due clan break members
                await clan_break_checker(self.bot)

            except Exception as e:
                pretty_log(
                    "error",
                    f"Error in central loop: {e}",
                    label="Central Loop",
                )
            await asyncio.sleep(60)  # Wait for 60 seconds before next iteration
    @commands.Cog.listener()
    async def on_ready(self):
        """Start the loop automatically once the bot is ready"""
        if not self.loop_task:
            self.loop_task = asyncio.create_task(self.central_loop())

async def setup(bot: commands.Bot):
    await bot.add_cog(CentralLoop(bot))
