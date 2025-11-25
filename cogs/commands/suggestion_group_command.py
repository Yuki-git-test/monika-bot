from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.suggestion import *
from utils.logs.pretty_log import pretty_log
from utils.db.suggestions_db_func import suggestion_title_autocomplete

# 🍭──────────────────────────────
#   🎀 Suggestion Group Command
# 🍭──────────────────────────────
class SuggestionGroupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Register the group command
    suggestion_group = app_commands.Group(
        name="suggestion", description="Suggestion related commands"
    )

    # 🎀───────────────────────────────────────────
    #          🌸 /suggestion submit 🌸
    # 🎀───────────────────────────────────────────
    @suggestion_group.command(
        name="submit",
        description="Submit a suggestion",
    )
    async def submit(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "suggestion submit"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=submit_suggestion_func,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /suggestion verdict
    # 🎀───────────────────────────────────────────
    @suggestion_group.command(
        name="verdict",
        description="Give a verdict on a suggestion",
    )
    @app_commands.describe(
        suggestion_id="The ID of the suggestion to give a verdict on",
        verdict="The verdict to give",
    )
    @app_commands.autocomplete(suggestion_id=suggestion_title_autocomplete)
    async def verdict(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        verdict: Literal["Approved", "Denied"],
        reason: str = None,
    ):
        slash_cmd_name = "suggestion verdict"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=suggestion_verdict_func,
            suggestion_id=suggestion_id,
            verdict=verdict,
            reason=reason,
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionGroupCommand(bot))