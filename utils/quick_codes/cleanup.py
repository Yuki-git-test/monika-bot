import asyncio

import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    KHY_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log

GRAVEYARD_CATEGORY_ID = 1329157603573633126


async def clean_graveyard_channels_func(message: discord.Message):
    guild = message.guild
    user = message.author

    # Check if user has staff role
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
    seafoam_role = guild.get_role(VN_ALLSTARS_ROLES.seafoam)

    if staff_role not in user.roles and seafoam_role not in user.roles:
        await message.reply(
            f"❌ {user.mention}, you do not have permission to use this command."
        )
        return

    # Add please wait message
    loading_msg = await message.reply(
        f"{Emojis.orange_loading} {user.mention}, cleaning up channels, please wait..."
    )
    # Get graveyard category
    graveyard_category = guild.get_channel(GRAVEYARD_CATEGORY_ID)
    if not graveyard_category:
        # Fetch graveyard category
        graveyard_category = await guild.fetch_channel(GRAVEYARD_CATEGORY_ID)

    # Delete all channels in graveyard category
    deleted_channels = []
    for channel in graveyard_category.channels:
        try:
            await channel.delete(reason=f"Cleanup by {user} ({user.id})")
            deleted_channels.append(channel.name)
            pretty_log(
                "info",
                f"Deleted channel {channel.name} ({channel.id}) in graveyard category.",
                label="Cleanup Channels",
            )
            await asyncio.sleep(0.5)

        except Exception as e:
            await loading_msg.edit(
                content=f"❌ {user.mention}, an error occurred while deleting channel {channel.mention}: {e}"
            )
            pretty_log(
                "error",
                f"Error deleting channel {channel.name} ({channel.id}): {e}",
                label="Cleanup Channels",
            )
            return

    if deleted_channels:
        deleted_channels_str = "\n".join([f"- {name}" for name in deleted_channels])
        embed = discord.Embed(
            title="✅ Cleanup Complete",
            description=f"The following channels have been deleted:\n{deleted_channels_str}",
            color=MONIKA_EMBED_COLOR,
        )
        deleted_channel_count = len(deleted_channels)
        embed.set_footer(
            text=f"Total channels deleted: {deleted_channel_count}",
            icon_url=guild.icon.url,
        )
        await loading_msg.edit(
            content=f"{user.mention}, cleanup complete!",
            embed=embed,
        )
    else:
        deleted_channels_str = "No channels were deleted."
        await loading_msg.edit(
            content=f"No channels to delete, {user.mention}.",
        )
