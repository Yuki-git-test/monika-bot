from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS, VN_ALLSTARS_ROLES
from utils.db.vna_members_db_func import get_personal_channel_id_by_user_id
from utils.essentials.pretty_defer import pretty_defer
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log


async def channel_remove_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
):
    """Removes a user from a member's personal channel"""
    user = interaction.user
    guild = interaction.guild

    loader = await pretty_defer(
        interaction=interaction,
        content=f"Removing {member.display_name} from your channel...",
    )

    # Check if user is clan member
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_member_role not in user.roles:
        await loader.error(
            "Only VNA Members can use this command!"
        )
        return

    # Check if user is removing themselves
    if user.id == member.id:
        await loader.error("You cannot remove yourself from your own channel!")
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

    # Check if member is in member list of the channel , exit if not
    overwrite = personal_channel.overwrites_for(member)
    if overwrite.is_empty():
        await loader.error(content=f"{member.display_name} is not in your channel.")
        return

    # 🔐 Update permissions
    try:
        await personal_channel.set_permissions(member, overwrite=None)
    except Exception as e:
        await loader.error(
            content="An error occurred while trying to remove the member from your channel. Please contact a staff member!"
        )
        pretty_log(
            "error",
            f"Error removing member `{member.id}` from personal channel `{personal_channel.id}`: {e}",
        )
        return

    # Confirmation embed
    content = f"{member.display_name} has been removed from your personal channel {personal_channel.mention}!"
    await loader.success(content)

    # Log action to staff webhook
    desc = (
        f"**Removed Member:** {member.mention} (`{member.id}`)\n"
        f"**Removed By:** {user.mention} (`{user.id}`)\n"
        f"**Channel:** {personal_channel.mention} (`{personal_channel.name}`)"
    )
    log_embed = discord.Embed(
        title="Member Removed From Personal Channel",
        color=discord.Color.red(),
        description=desc,
        timestamp=datetime.now(),
    )
    log_embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    log_embed.set_thumbnail(url=member.display_avatar.url)
    log_embed.set_footer(
        text=f"Channel ID: {personal_channel.id}", icon_url=guild.icon.url
    )
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_logs)
    await send_webhook(
        bot=bot,
        channel=log_channel,
        embed=log_embed,
    )
