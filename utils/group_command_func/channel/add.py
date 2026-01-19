from datetime import datetime

import discord
from discord.ext import commands

from constants.permissions import MEMBER_PERMISSIONS
from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.vna_members_db_func import get_personal_channel_id_by_user_id
from utils.essentials.pretty_defer import pretty_defer
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log


async def channel_add_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
):
    """Adds a user to a member's personal channel"""
    user = interaction.user
    guild = interaction.guild

    loader = await pretty_defer(
        interaction=interaction,
        content=f"Adding {member.display_name} to your channel...",
    )

    # Check if user is clan member
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_member_role not in user.roles:
        await loader.error("Only VNA Members can use this command!")
        return

    # Check if user is adding  themselves
    if user.id == member.id:
        await loader.error("You cannot add yourself to your own channel!")
        return

    # Check if user has a personal channel
    personal_channel_id = await get_personal_channel_id_by_user_id(bot, user.id)
    if not personal_channel_id:
        await loader.error(
            "You do not have a personal channel to add members to! Please contact a staff member!"
        )
        return
    personal_channel = guild.get_channel(personal_channel_id)
    if not personal_channel:
        await loader.error(
            "Your personal channel could not be found! Please contact a staff member!"
        )
        return

    # Check if member is explicitly listed in the channel's permission overwrites (i.e., in the Members list)
    if member.id in [
        target.id
        for target in personal_channel.overwrites
        if isinstance(target, discord.Member)
    ]:
        await loader.error(
            f"{member.display_name} is already listed as a member with access to your personal channel!"
        )
        return

    # 🔐 Update permissions
    try:
        await personal_channel.set_permissions(
            member, overwrite=discord.PermissionOverwrite(**MEMBER_PERMISSIONS)
        )

    except Exception as e:
        await loader.error(
            f"An error occurred while adding {member.display_name} to your personal channel. Please contact a staff member!"
        )
        pretty_log(
            "error",
            f"Error adding member ID {member.id} to personal channel ID {personal_channel.id}: {e}",
        )
        return

    # Confirmation embed
    content = f"{member.mention} has been added to your personal channel {personal_channel.mention}!"
    await loader.success(content)

    # Log action to staff webhook
    desc = (
        f"**Added Member:** {member.mention} (`{member.id}`)\n"
        f"**Added By:** {user.mention} (`{user.id}`)\n"
        f"**Channel:** {personal_channel.mention} (`{personal_channel.name}`)"
    )
    log_embed = discord.Embed(
        title="Member Added to Personal Channel",
        color=discord.Color.green(),
        description=desc,
        timestamp=datetime.now(),
    )
    log_embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    log_embed.set_thumbnail(url=member.display_avatar.url)
    log_embed.set_footer(
        text=f"Channel ID: {personal_channel.id}", icon_url=guild.icon.url
    )
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    await send_webhook(
        bot=bot,
        channel=log_channel,
        embed=log_embed,
    )
