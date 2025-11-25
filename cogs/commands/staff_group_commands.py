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

    # 🎀───────────────────────────────────────────
    #          🌸 /staff list-members 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="list-members",
        description="List all VNA members to the database",
    )
    @app_commands.describe(
        message_link="The link to the message to list members from",
    )
    async def list_members(
        self,
        interaction: discord.Interaction,
        message_link: str,
    ):
        slash_cmd_name = "/staff list-members"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=list_vna_members_func,
            message_link=message_link,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff set-channel 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="set-channel",
        description="Set the clan channel for a VNA member",
    )
    @app_commands.describe(
        member="The VNA member to set the channel for",
        channel="The channel to set as the clan channel",
    )
    async def set_channel(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        channel: discord.TextChannel,
    ):
        slash_cmd_name = "staff set-channel"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=set_channel_func,
            member=member,
            channel=channel,

        )
    # 🎀───────────────────────────────────────────
    #          🌸 /staff clan-members 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="clan-members",
        description="List all members of the VNA Clan",
    )
    async def clan_members(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "staff clan-members"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=clan_members_func,
        )

# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = StaffGroupCommand(bot)
    await bot.add_cog(cog)
