from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs


# 🍭──────────────────────────────
#   🎀 Event: On Role Remove
# 🍭──────────────────────────────
async def handle_role_remove(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role,
):
    """Handle role removal events."""
    role_id = role.id

    # ————————————————————————————————
    # 🩵 VNA Server Role Remove Logic
    # ————————————————————————————————
    # Log role removal
    pretty_log(
        message=f"Role '{role.name}' removed from member '{member.display_name}'.",
        tag="info",
        label="Member Update Event",
    )
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="❌ Role Removed",
            color=discord.Color.red(),
            description=(f"**Member:** {member.mention}\n" f"**Role:** {role.mention}"),
            timestamp=datetime.now(),
        )
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_footer(
            text=f"Role ID: {role.id}",
            icon_url=member.guild.icon.url if member.guild.icon else None,
        )
        await log_channel.send(embed=embed)
