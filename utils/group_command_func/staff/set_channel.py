import re
from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_channel
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log


async def set_channel_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    channel: discord.TextChannel,
):
    """Set a member's channel to the specified channel."""

    # Check if user is a staff member
    user = interaction.user
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can set member channels.", ephemeral=True
        )
        return

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Setting the channel for {member.display_name}...",
        ephemeral=False,
    )

    # Check if member has clan role
    member_id = member.id
    vna_clan_role_id = VN_ALLSTARS_ROLES.vna_member
    if vna_clan_role_id not in [role.id for role in member.roles]:
        msg = (
            f"{member.display_name} is not a VNA Member and cannot have a channel set."
        )
        await loader.error(content=msg)
        return
    # Check if member already has the channel set
    member_info = vna_members_cache.get(member_id)
    if member_info:
        current_channel_id = member_info.get("channel_id")
        if current_channel_id == channel.id:
            msg = f"{member.display_name} already has the channel set to {channel.mention}."
            await loader.error(content=msg)
            return
    # Update the member's channel in the database
    try:
        await update_member_channel(bot, member, channel.id)
        pretty_log(
            "success",
            f"Set channel for member '{member.display_name}' to '{channel.name}'.",
        )
        embed = discord.Embed(
            title="✅ Channel Set Successfully",
            description=f"**Member:** {member.mention}\n**Channel:** {channel.mention}",
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_footer(
            text=f"User ID: {member.id}",
            icon_url=member.guild.icon.url if member.guild.icon else None,
        )
        await loader.success(embed=embed, content="")

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to set channel for member '{member.display_name}': {e}",
        )
        await loader.error(
            content=f"Failed to set the channel for {member.display_name}."
        )
        return
