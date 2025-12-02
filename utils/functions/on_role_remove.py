from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import top_monthly_grinders_cache, vna_members_cache
from utils.db.top_monthly_grinders_db import delete_top_monthly_grinder
from utils.db.vna_members_db_func import remove_member
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
from utils.functions.webhook_func import send_webhook


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

    # ————————————————————————————————
    # 🩵 VNA Member Role Removed
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.vna_member:
        # Check if member is in cache
        cached_member = vna_members_cache.get(member.id)
        if cached_member:
            # Remove member from the database
            await remove_member(bot, member)

    # ————————————————————————————————
    # 🩵 VNA Top Monthly Grinder Role Remove
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.top_monthly_grinder:
        # Check if in cache
        cached_grinder = top_monthly_grinders_cache.get(member.id)
        if cached_grinder:
            # Remove from db
            await delete_top_monthly_grinder(bot, member)

    # ————————————————————————————————
    # 🩵 VNA Role Logs
    # ————————————————————————————————
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
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
