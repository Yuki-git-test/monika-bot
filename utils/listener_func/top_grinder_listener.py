import re
from datetime import datetime, timedelta

import discord
import pytz
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import top_monthly_grinders_cache, vna_members_cache
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.essentials.stats_parsers import (
    fetch_message_obj_from_link,
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.logs.pretty_log import pretty_log
from utils.functions.webhook_func import send_webhook

def is_past_11pm_first_day_est():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day == 1 and now_est.hour >= 23


async def assign_top_grinder_roles_listener(
    bot: discord.Client, message: discord.Message
):
    # Check if time is past 11 PM EST on the first day of the month
    if not is_past_11pm_first_day_est():
        pretty_log(
            "info",
            "Top Grinder role assignment skipped: Not past 11 PM EST on the first day of the month.",
        )
        return

    # Extract stats from message
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    embed_title = embed.title or ""

    if "Clan Monthly Stats — VN Allstar" not in embed_title:
        return

    embed_description = embed.description or ""
    if not embed_description:
        return

    # Get current page number from footer
    footer_text = (
        embed.footer.text
    )  # This will give you "Page 1/5 • Stat categories: ;clan stats daily/weekly/monthly/yearly"
    page_match = re.search(r"Page\s+(\d+)/(\d+)", footer_text)
    if not page_match:
        return
    current_page = int(page_match.group(1))

    if current_page != 1:
        return

    # Parse clan stats from embed description
    clan_members_stats = parse_clan_stats_message(embed_description)
    if not clan_members_stats:
        return

    # Split known and unknown members
    guild = bot.get_guild(VNA_SERVER_ID)
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    known_members, unknown_members = await split_known_and_unknown_members(
        bot=bot,
        guild=guild,
        members=clan_members_stats,
    )
    if unknown_members:
        desc_lines = []
        for username, catches, fishes in unknown_members:
            desc_lines.append(f"- {username} (Catches: {catches}, Fishes: {fishes})")
        desc_text = "\n".join(desc_lines)
        embed = discord.Embed(
            title="⚠️ Unknown Members Detected",
            description=(
                "The following members were not found in the server. "
                "Kindly update their info using `/staff update-member`:\n\n"
                f"{desc_text}"
            ),
            color=discord.Color.yellow(),
            timestamp=datetime.now(),
        )
        unknow_member_count = len(unknown_members)
        embed.set_footer(
            text=f"Total Unknown Members: {unknow_member_count}",
            icon_url=guild.icon.url if guild.icon else None,
        )
        if log_channel:
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )

    pretty_log(
        "info",
        f"Assigning Top Grinder roles: {len(known_members)} known members, {len(unknown_members)} unknown members.",
    )

    # Role
    top_grinder_role = guild.get_role(VN_ALLSTARS_ROLES.top_monthly_grinder)
    # Fetch top grinders from cache
    if top_monthly_grinders_cache:
        # Get member using ids from cache
        for user_id in top_monthly_grinders_cache.keys():
            member = guild.get_member(user_id)
            if member:
                # Remove existing top grinder roles
                if top_grinder_role in member.roles:
                    await member.remove_roles(top_grinder_role)
                    pretty_log(
                        "info",
                        f"Removed Top Monthly Grinder role from {member.display_name}",
                    )
    else:
        # Remove existing top grinder roles from all members
        for member in guild.members:
            if top_grinder_role in member.roles:
                await member.remove_roles(top_grinder_role)
                pretty_log(
                    "info",
                    f"Removed Top Monthly Grinder role from {member.display_name}",
                )

    # Assign roles to top 10
    for member, username, catches, fishes in known_members:
        try:
            await member.add_roles(top_grinder_role)
            pretty_log(
                "info",
                f"Assigned Top Monthly Grinder role to {username} (Catches: {catches}, Fishes: {fishes})",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to assign Top Monthly Grinder role to {username}: {e}",
            )
    pretty_log("success", "Top Monthly Grinder role assignment completed.")
