import asyncio
import re
import zoneinfo
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import discord
import pytz
from discord.ext import commands

from constants.vn_allstars_constants import PROBATION_EXEMPTED_USER_IDS
from utils.cache.cache_list import probation_list_cache, vna_members_cache
from utils.db.probation_list_db import upsert_probation_member
from utils.functions.webhook_func import send_webhook
from utils.listener_func.weekly_stats_listener import send_probation_report_embed
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log


def get_est_day_number():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day  # Returns the day of the month as int


# 🍭──────────────────────────────
#   🎀 Probation Role Add Handler
# 🍭──────────────────────────────
async def probation_role_add(
    bot: discord.Client,
    member: discord.Member,
):
    """Handle probation role addition for a member."""
    # Check if member is exempted
    if member.id in PROBATION_EXEMPTED_USER_IDS:
        pretty_log(
            "info",
            f"Member '{member.display_name}' is exempted from probation role handling.",
            label="Probation Role Add",
        )
        return

    # Sleep for 5 seconds to ensure roles are updated
    await asyncio.sleep(5)
    # Check if user has probation data in cache
    probation_data = probation_list_cache.get(member.id)
    if probation_data:
        pretty_log(
            "info",
            f"Probation data found in cache for member '{member.display_name}'. No action needed.",
            label="Probation Role Add",
        )
        return
    else:
        current_day = get_est_day_number()
        # Get member info
        member_info = vna_members_cache.get(member.id)
        if not member_info:
            pretty_log(
                "error",
                f"Member '{member.display_name}' not found in VNA members cache.",
                label="Probation Role Add",
            )
            return
        joined_date = member_info.get("clan_joined_date")
        # Determine if member is new this month
        eastern = pytz.timezone("US/Eastern")
        now_est = datetime.now(eastern)
        month_start = now_est.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        month_end = next_month - timedelta(seconds=1)
        user_joined_dt = (
            datetime.fromtimestamp(joined_date, tz=eastern) if joined_date else None
        )
        # Compute for catch requirement
        # Adjust Requirements for New Members
        if joined_date and month_start <= user_joined_dt <= month_end:
            days_in_clan = (now_est - user_joined_dt).days
            member_required_catches = days_in_clan * 200
        else:
            member_required_catches = current_day * 200

        pokemeow_name = member_info.get("pokemeow_name", "Unknown")
        # Upsert probation member into the database
        await upsert_probation_member(
            bot,
            user=member,
            pokemeow_name=pokemeow_name,
            catch_requirement=member_required_catches,
        )
        pretty_log(
            "info",
            f"Probation member '{member.display_name}' added with catch requirement of {member_required_catches}.",
            label="Probation Role Add",
        )
