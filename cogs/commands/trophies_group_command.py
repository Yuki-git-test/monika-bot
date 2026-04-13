from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.team_trophies import *


# 🐾────────────────────────────────────────────
#     🎐 team Trophies Command Group Cog
# 🐾────────────────────────────────────────────
class TrophiesCommandGroup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ⚡ Top-level group (only register once!)
    team_trophy_group = app_commands.Group(
        name="team-trophy",
        description="Team Trophies related commands",
    )

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy multi 🌸
    # 🎀────────────────────────────────────────────
    @team_trophy_group.command(
        name="multi",
        description="Add or remove trophies for multiple teams at once",
    )
    @app_commands.describe(
        action="Whether to add or remove trophies",
        amount="The amount of trophies to add or remove",
        team1="The first team (required)",
        team2="The second team (optional)",
        team3="The third team (optional)",
        team4="The fourth team (optional)",
        team5="The fifth team (optional)",
        team6="The sixth team (optional)",
        team7="The seventh team (optional)",
        team8="The eighth team (optional)",
        team9="The ninth team (optional)",
        team10="The tenth team (optional)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Only allow administrators to use this command
    async def trophy_multi(
        self,
        interaction: discord.Interaction,
        action: Literal["add", "remove"],
        amount: int,
        team1: discord.Role,
        team2: discord.Role = None,
        team3: discord.Role = None,
        team4: discord.Role = None,
        team5: discord.Role = None,
        team6: discord.Role = None,
        team7: discord.Role = None,
        team8: discord.Role = None,
        team9: discord.Role = None,
        team10: discord.Role = None,
    ):

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy multi",
            command_func=trophy_multi_func,
            action=action,
            amount=amount,
            team1=team1,
            team2=team2,
            team3=team3,
            team4=team4,
            team5=team5,
            team6=team6,
            team7=team7,
            team8=team8,
            team9=team9,
            team10=team10,
        )

    trophy_multi.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy reset 🌸
    # 🎀────────────────────────────────────────────
    @team_trophy_group.command(
        name="reset",
        description="Reset all team trophies (staff only)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Only allow administrators to use this command
    async def trophy_reset(self, interaction: discord.Interaction):
        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy reset",
            command_func=reset_trophies_func,
        )

    trophy_reset.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy leaderboard 🌸
    # 🎀────────────────────────────────────────────
    @team_trophy_group.command(
        name="leaderboard",
        description="View the current team trophies leaderboard",
    )
    async def trophy_leaderboard(self, interaction: discord.Interaction):
        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy leaderboard",
            command_func=view_leaderboard_func,
        )

    trophy_leaderboard.extras = {"category": "Public"}

# 🐾────────────────────────────────────────────
#     🎐 Setup Function
# 🐾────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TrophiesCommandGroup(bot))
