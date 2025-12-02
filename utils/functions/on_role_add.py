from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import top_monthly_grinders_cache, vna_members_cache
from utils.db.top_monthly_grinders_db import upsert_top_monthly_grinder
from utils.db.vna_members_db_func import upsert_member
from utils.functions.server_booster_handler import handle_server_booster_role_add
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
from utils.functions.webhook_func import send_webhook


# 🍭──────────────────────────────
#   🎀 Event: On Role Add
# 🍭──────────────────────────────
async def handle_role_add(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role,
):
    """Handle role addition events."""
    role_id = role.id

    # ————————————————————————————————
    # 🩵 VNA Server Booster Role Add
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.server_booster:
        # Handle server booster role addition
        pretty_log(
            message=f"Detected server booster role addition for member '{member.display_name}'.",
            tag="info",
            label="Role Add Event",
        )
        await handle_server_booster_role_add(bot, member)

    # ————————————————————————————————
    # 🩵 VNA Member Role Add
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.vna_member:
        # Check if member is in cache
        cached_member = vna_members_cache.get(member.id)
        if not cached_member:
            # Upsert member into the database
            await upsert_member(bot, member)

    # ————————————————————————————————
    # 🩵 VNA Top Monthly Grinder Role Add
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.top_monthly_grinder:
        # Check if in cache
        cached_grinder = top_monthly_grinders_cache.get(member.id)
        if not cached_grinder:
            # Upsert top monthly grinder into the database
            await upsert_top_monthly_grinder(
                bot,
                user=member,
            )

    # ————————————————————————————————
    # 🩵 VNA Role Logs
    # ————————————————————————————————
    pretty_log(
        message=f"Role '{role.name}' added to member '{member.display_name}'.",
        tag="info",
        label="Member Update Event",
    )
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="✅ Role Added",
            color=discord.Color.green(),
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
