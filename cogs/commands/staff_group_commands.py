from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.staff import *
from utils.logs.pretty_log import pretty_log

# 🍭──────────────────────────────
#   🎀 Staff Group Command
# 🍭──────────────────────────────
class StaffGroupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Register the group command
    staff_group = app_commands.Group(
        name="staff", description="Staff only commands"
    )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff role-members 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="role-members",
        description="Display members with a specific role",
    )
    @app_commands.describe(
        role="The role to display members for",
    )
    async def role_members(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        slash_cmd_name = "/staff role-members"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=role_members_func,
            role=role,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff invite 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="invite",
        description="Manually create a clan channel for a member",
    )
    @app_commands.describe(
        channel_name="The name of the clan channel to create",
        member="The member to create the clan channel for",
    )
    async def clan_invite(
        self,
        interaction: discord.Interaction,
        channel_name: str,
        member: discord.Member,
    ):
        slash_cmd_name = "/staff invite"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=clan_invite_func,
            channel_name=channel_name,
            member=member,
        )



# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = StaffGroupCommand(bot)
    await bot.add_cog(cog)
