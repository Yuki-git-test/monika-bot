from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.message_logs

from utils.functions.webhook_func import send_webhook


# 🍭──────────────────────────────
#   🎀 Event: On Message Edit Log
# 🍭──────────────────────────────
async def message_edit_log(bot, before: discord.Message, after: discord.Message):
    """Log message edit events."""

    # Return if bot edited the message
    if after.author.bot:
        return

    guild = after.guild
    if not guild or guild.id != VNA_SERVER_ID:
        return
    desc = (
        f"**Member:**{after.author.mention}\n**Before:** {before.content}\n\n**After +:** {after.content}"
        if before.content or after.content
        else "Message content was empty."
    )
    embed = discord.Embed(
        title=f"✏️ Message Edited in {after.channel.name}",
        url=after.jump_url,
        description=desc,
        color=MONIKA_EMBED_COLOR,
        timestamp=datetime.now(),
    )

    embed.set_author(
        name=after.author.display_name, icon_url=after.author.display_avatar.url
    )
    embed.set_footer(
        text=f"Message ID: {after.id}", icon_url=guild.icon.url if guild.icon else None
    )
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
