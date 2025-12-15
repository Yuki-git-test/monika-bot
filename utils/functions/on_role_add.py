from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import (
    probation_list_cache,
    top_monthly_grinders_cache,
    vna_members_cache,
)
from utils.db.probation_list_db import upsert_probation_member
from utils.db.top_monthly_grinders_db import upsert_top_monthly_grinder
from utils.db.vna_members_db_func import upsert_member
from utils.functions.clan_break_role_handler import handle_clan_break_add_role
from utils.functions.monthly_requirements_utils import (
    get_member_weeks_in_clan,
    is_member_less_than_a_month_old,
    read_monthly_requirements,
    write_monthly_requirements,
)
from utils.functions.server_booster_handler import handle_server_booster_role_add
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs


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
            pretty_log(
                message=f"Upserting VNA member '{member.display_name}' into the database.",
                tag="info",
                label="Role Add Event",
            )
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
    # 🩵 VNA Clan Break Role Add
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.clan_break:
        # Handle clan break role addition
        await handle_clan_break_add_role(bot, member)

    # ————————————————————————————————
    # 🩵 VNA Probation Role Add
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.probation:
        member_probation_info = probation_list_cache.get(member.id)
        if not member_probation_info:
            vna_member_info = vna_members_cache.get(member.id)
            joined_date = vna_member_info.get("clan_joined_date")  # unix timestamp
            if vna_member_info:
                pokemeow_name = vna_member_info.get("pokemeow_name", "Unknown")
                # Upsert probation member into the database
                expected_catches, _ = read_monthly_requirements()
                # Adjust catch requirement if member is less than a month old
                catch_requirement = expected_catches
                if is_member_less_than_a_month_old(member.id):
                    weeks_in_clan = get_member_weeks_in_clan(member.id)
                    catch_requirement = 1500 * weeks_in_clan

                await upsert_probation_member(
                    bot,
                    user=member,
                    pokemeow_name=pokemeow_name,
                    catch_requirement=catch_requirement,
                )
                pretty_log(
                    message=f"Upserted probation member '{member.display_name}' into the database with catch requirement of {catch_requirement:,}.",
                    tag="info",
                    label="Role Add Event",
                )

    # ————————————————————————————————
    # 🩵 VNA Role Logs
    # ————————————————————————————————
    pretty_log(
        message=f"Role '{role.name}' added to member '{member.display_name}'.",
        tag="info",
        label="Member Update Event",
    )
    if role_id != VN_ALLSTARS_ROLES.clan_break:
        log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="✅ Role Added",
                color=discord.Color.green(),
                description=(
                    f"**Member:** {member.mention}\n" f"**Role:** {role.mention}"
                ),
                timestamp=datetime.now(),
            )
            if role.icon:
                embed.set_thumbnail(url=role.icon.url)
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )
            embed.set_footer(
                text=f"Role ID: {role.id}",
                icon_url=member.guild.icon.url if member.guild.icon else None,
            )
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )
