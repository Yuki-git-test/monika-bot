from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.trophy import *
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Trophy Group Command
# 🍭──────────────────────────────
class TrophyGroupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Register the group command
    trophy_group = app_commands.Group(
        name="trophy", description="Commands related to trophies"
    )

    # 🎀────────────────────────────────────────────
    #          🌸 /trophy view 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="view",
        description="View a member's trophies",
    )
    @app_commands.describe(
        member="The member to view the trophies of (staff only)",
    )
    async def trophy_view(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
    ):
        slash_cmd_name = "/trophy view"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=trophies_view_func,
            member=member,
        )

    # 🎀────────────────────────────────────────────
    #          🌸 /trophy remove 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="remove",
        description="Remove trophies from a member (staff only)",
    )
    @app_commands.describe(
        member="The member to remove trophies from",
        amount="The amount of trophies to remove",
    )
    async def trophy_remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int,
    ):
        slash_cmd_name = "/trophy remove"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=trophy_remove_func,
            member=member,
            amount=amount,
        )

    # 🎀────────────────────────────────────────────
    #          🌸 /trophy add 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="add",
        description="Add trophies to a member (staff only)",
    )
    @app_commands.describe(
        member="The member to add trophies to",
        amount="The amount of trophies to add",
    )
    async def trophy_add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int,
    ):
        slash_cmd_name = "/trophy add"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=trophy_add_func,
            member=member,
            amount=amount,
        )

    # 🎀────────────────────────────────────────────
    #          🌸 /trophy leaderboard 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="leaderboard",
        description="View the trophy leaderboard",
    )
    async def trophy_leaderboard(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "/trophy leaderboard"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=view_leaderboard_func,
        )

    # 🎀────────────────────────────────────────────
    #          🌸 /trophy reset 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="reset",
        description="Reset all trophies and the leaderboard (staff only)",
    )
    async def trophy_reset(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "/trophy reset"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=trophy_reset_func,
        )


# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TrophyGroupCommand(bot))
