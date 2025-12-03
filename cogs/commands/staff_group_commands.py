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

    message_group = app_commands.Group(
        name="message", description="Staff message commands"
    )
    staff_group.add_command(message_group)
    # 🎀───────────────────────────────────────────
    #          🌸 /staff list-top-grinders 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="list-top-grinders",
        description="Assign Top Monthly Grinder roles to members",
    )
    async def list_top_grinders(
        self,
        interaction: discord.Interaction,
        message_link: str,
    ):
        slash_cmd_name = "staff list-top-grinders"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=assign_top_grinder_roles,
            message_link=message_link,
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
        slash_cmd_name = "staff role-members"

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
        slash_cmd_name = "staff invite"

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
        slash_cmd_name = "staff list-members"

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
    # 🎀───────────────────────────────────────────
    #          🌸 /staff message send 🌸
    # 🎀───────────────────────────────────────────
    @message_group.command(
        name="send",
        description="Send a message to a specified channel",
    )
    @app_commands.describe(
        channel="The channel to send the message to",
        ping_role="An optional role to ping in the message",
    )
    async def message_send(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        ping_role: discord.Role = None,
    ):
        slash_cmd_name = "staff message send"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=message_send_func,
            channel=channel,
            ping_role=ping_role,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff message edit 🌸
    # 🎀───────────────────────────────────────────
    @message_group.command(
        name="edit",
        description="Edit a message in a specified channel",
    )
    @app_commands.describe(
        channel="The channel where the message is located",
        message_id="The ID of the message to edit",
    )
    async def message_edit(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message_id: str,
    ):
        slash_cmd_name = "staff message edit"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=message_edit_func,
            channel=channel,
            message_id=message_id,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff extract-joined-date 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="extract-joined-date",
        description="Extract joined date from a message link and update the member's record",
    )
    @app_commands.describe(
        message_link="The link to the message to extract joined dates from",
    )
    async def extract_joined_date(
        self,
        interaction: discord.Interaction,
        message_link: str,
    ):
        slash_cmd_name = "staff extract-joined-date"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=extract_joined_date_func,
            message_link=message_link,
        )

    # 🎀───────────────────────────────────────────
    #          🌸 /staff update-member 🌸
    # 🎀───────────────────────────────────────────
    @staff_group.command(
        name="update-member",
        description="Update a VNA member's information",
    )
    @app_commands.describe(
        member="The VNA member to update",
        pokemeow_name="The updated PokéMeow username",
        channel="The updated clan channel",
        perks="The updated perks",
        faction="The updated faction",
        clan_joined_date="The updated clan joined date (Unix timestamp)",
    )
    async def update_member(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        pokemeow_name: str = None,
        channel: discord.TextChannel = None,
        perks: str = None,
        faction: str = None,
        clan_joined_date: str = None,
    ):
        slash_cmd_name = "staff update-member"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=update_member_func,
            member=member,
            pokemeow_name=pokemeow_name,
            channel=channel,
            perks=perks,
            faction=faction,
            clan_joined_date=clan_joined_date,
        )

# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = StaffGroupCommand(bot)
    await bot.add_cog(cog)
