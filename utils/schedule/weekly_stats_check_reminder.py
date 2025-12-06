from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)

from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Weekly Stats Check Reminder
# 🍭──────────────────────────────
async def weekly_stats_check_reminder(
    bot: commands.Bot,
):
    """Send a reminder to the staff channel to check weekly stats."""

    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log(
            "error",
            "Weekly Stats Check Reminder: VNA server not found.",
        )
        return

    staff_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.moderator_bot_play)
    if not staff_channel:
        pretty_log(
            "error",
            "Weekly Stats Check Reminder: Staff channel not found.",
        )
        return

    reminder_message = (
        f"Hello <@&{VN_ALLSTARS_ROLES.staff}>, this is a friendly reminder to check the "
        "`;clan stats w` Thank you!"
    )

    try:
        await staff_channel.send(reminder_message)
        pretty_log(
            "info",
            "Weekly Stats Check Reminder sent successfully.",
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Weekly Stats Check Reminder: Failed to send message. Error: {e}",
        )
