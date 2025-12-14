from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.public_trophy import *
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Public Trophy Group Command
# 🍭──────────────────────────────
class PublicTrophyGroupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Register the group command
    public_trophy_group = app_commands.Group(
        name="public-trophy", description="Commands related to public trophies"
    )

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy view 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="view",
        description="View a member's public trophies",
    )
    @app_commands.describe(
        member="The member to view the public trophies of (staff only)",
    )
    async def public_trophy_view(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
    ):
        slash_cmd_name = "/public-trophy view"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=public_trophies_view_func,
            member=member,
        )

    public_trophy_view.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy remove 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="remove",
        description="Remove trophies from a member (staff only)",
    )
    @app_commands.describe(
        member="The member to remove trophies from",
        amount="The amount of trophies to remove",
    )
    async def public_trophy_remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int,
    ):
        slash_cmd_name = "/public-trophy remove"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=public_trophy_remove_func,
            member=member,
            amount=amount,
        )

    public_trophy_remove.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy add 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="add",
        description="Add trophies to a member (staff only)",
    )
    @app_commands.describe(
        member="The member to add trophies to",
        amount="The amount of trophies to add",
    )
    async def public_trophy_add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int,
    ):
        slash_cmd_name = "/public-trophy add"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=public_trophy_add_func,
            member=member,
            amount=amount,
        )

    public_trophy_add.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy leaderboard 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="leaderboard",
        description="View the trophy leaderboard",
    )
    async def public_trophy_leaderboard(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "/public-trophy leaderboard"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=view_public_leaderboard_func,
        )

    public_trophy_leaderboard.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy reset 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="reset",
        description="Reset all trophies and the leaderboard (staff only)",
    )
    async def public_trophy_reset(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "/public-trophy reset"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=public_trophy_reset_func,
        )

    public_trophy_reset.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #          🌸 /public-trophy multi 🌸
    # 🎀────────────────────────────────────────────
    @public_trophy_group.command(
        name="multi",
        description="Add or remove trophies to/from multiple members (staff only)",
    )
    @app_commands.describe(
        action="Whether to add or remove trophies",
        amount="The amount of trophies to add or remove",
        member1="The first member",
        member2="The second member (optional)",
        member3="The third member (optional)",
        member4="The fourth member (optional)",
        member5="The fifth member (optional)",
        member6="The sixth member (optional)",
        member7="The seventh member (optional)",
        member8="The eighth member (optional)",
        member9="The ninth member (optional)",
        member10="The tenth member (optional)",
    )
    async def public_trophy_multi(
        self,
        interaction: discord.Interaction,
        action: Literal["add", "remove"],
        amount: int,
        member1: discord.Member,
        member2: discord.Member = None,
        member3: discord.Member = None,
        member4: discord.Member = None,
        member5: discord.Member = None,
        member6: discord.Member = None,
        member7: discord.Member = None,
        member8: discord.Member = None,
        member9: discord.Member = None,
        member10: discord.Member = None,
    ):
        slash_cmd_name = "public-trophy multi"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=public_trophy_multi_func,
            action=action,
            amount=amount,
            member1=member1,
            member2=member2,
            member3=member3,
            member4=member4,
            member5=member5,
            member6=member6,
            member7=member7,
            member8=member8,
            member9=member9,
            member10=member10,
        )

    public_trophy_multi.extras = {"category": "Staff"}


# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(PublicTrophyGroupCommand(bot))
