import re
from datetime import datetime, timedelta, timezone

import discord
import pytz
from discord.ext import commands

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import (
    kick_list_cache,
    probation_list_cache,
    top_monthly_grinders_cache,
    vna_members_cache,
)
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.essentials.stats_parsers import (
    fetch_message_obj_from_link,
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

PROBATION_LIST_DAYS = [7, 14, 21, 28]
WEEKLY_REQUIREMENT_CATCHES = 1500


def is_past_11pm_probation_day_est():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day in PROBATION_LIST_DAYS and now_est.hour >= 23


def get_est_day_number():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day  # Returns the day of the month as int


def get_est_hour():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.hour  # Returns the hour (0-23) in EST


def is_clan_member_less_than_7_days_est(clan_joined_unix: int) -> bool:
    est = pytz.timezone("US/Eastern")
    joined_dt = datetime.fromtimestamp(clan_joined_unix, tz=est)
    now_dt = datetime.now(est)
    return (now_dt - joined_dt) < timedelta(days=7)


async def send_probation_report_embed(
    bot: discord.Client,
    title: str,
    member: discord.Member,
    catches: int,
    fishes: int,
    total_catches: int,
):
    if "add" in title.lower() or "assigned" in title.lower():
        color = discord.Color.red()
    else:
        color = discord.Color.green()

    embed = discord.Embed(
        title=title,
        description=(
            f"**Member:** {member.mention} ({member.display_name})\n"
            f"**Catches:** {catches}\n"
            f"**Fishes:** {fishes}\n"
            f"**Total Catches:** {total_catches}\n"
        ),
        color=color,
        timestamp=datetime.now(),
    )
    guild = bot.get_guild(VNA_SERVER_ID)
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"User ID: {member.id}", icon_url=guild.icon.url if guild.icon else None
    )
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
        pretty_log(
            "info",
            f"Sent probation report for {member.display_name} to server log channel.",
            label="Auto Probation Role Assignment",
        )


async def weekly_stats_checker(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):

    is_probation_time = is_past_11pm_probation_day_est()
    # Extract stats from message
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        return

    embed_title = embed.title or ""

    if "Clan Weekly Stats — VN Allstar" not in embed_title:
        return

    embed_description = embed.description or ""
    if not embed_description:
        return

    # Get member first
    command_user = await get_pokemeow_reply_member(before_message)
    if not command_user:
        return

    # Get current day and hour in EST
    current_day = get_est_day_number()
    current_hour = get_est_hour()

    # Get roles
    guild = bot.get_guild(VNA_SERVER_ID)
    kick_role = guild.get_role(VN_ALLSTARS_ROLES.kick_list)
    clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)

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
    """if unknown_members:
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
                f"Logged {unknow_member_count} unknown members to server log channel.",
                label="Auto Probation Role Assignment",
            )
    """
    # Get top line
    command_user_catches = 0
    command_user_top_line_match = re.search(
        r"You're Rank \d+ in your clan's monthly stats — with ([\d,]+) catches!",
        embed_description,
    )
    if command_user_top_line_match:
        user_catches = int(command_user_top_line_match.group(1).replace(",", ""))
        pretty_log(
            f"Command user catches parsed from embed: {user_catches}",
        )

    # Check command user first
    command_user_id = command_user.id
    command_user_info = vna_members_cache.get(command_user_id)
    if not command_user_info:
        pretty_log(
            "error",
            f"Command user {command_user.display_name} not found in VNA members cache.",
            label="Auto Probation Role Assignment",
        )
    command_user_joined_date = command_user_info.get("clan_joined_date")
    new_to_clan = False
    if command_user_joined_date:
        if is_clan_member_less_than_7_days_est(command_user_joined_date):
            new_to_clan = True
            pretty_log(
                "info",
                f"Command user {command_user.display_name} is new to clan (joined less than 7 days).",
                label="Auto Probation Role Assignment",
            )
        if (
            command_user_joined_date
            and not new_to_clan
            and command_user_id != HARMLESS_USER_ID
        ):
            # Remove if on probation if met requirements
            if probation_role in command_user.roles:
                if command_user_catches >= WEEKLY_REQUIREMENT_CATCHES:
                    roles_to_remove = []
                    if probation_role in command_user.roles:
                        roles_to_remove.append(probation_role)
                    if kick_role in command_user.roles:
                        roles_to_remove.append(kick_role)
                    if roles_to_remove:
                        await command_user.remove_roles(
                            *roles_to_remove,
                            reason="Met weekly catches requirement.",
                        )
                        pretty_log(
                            "info",
                            f"Removed probation/kick roles from {command_user.display_name} for meeting weekly catches requirement.",
                            label="Auto Probation Role Assignment",
                        )
                        title = "✅ Command User Probation Role Removed"
                        if kick_role in roles_to_remove:
                            title = "✅  Command User Probation and Double Probation Roles Removed"
                        await send_probation_report_embed(
                            bot=bot,
                            title=title,
                            member=command_user,
                            catches=command_user_catches,
                            fishes=0,
                            total_catches=command_user_catches,
                        )

                # Assign probation if didnt meet requirements and doesnt have probation
                elif command_user_catches < WEEKLY_REQUIREMENT_CATCHES:
                    # Check time to assign probation
                    if current_day in PROBATION_LIST_DAYS and current_hour >= 23:
                        if probation_role not in command_user.roles:
                            await command_user.add_roles(
                                probation_role,
                                reason="Did not meet weekly catches requirement.",
                            )
                            pretty_log(
                                "info",
                                f"Assigned probation role to {command_user.display_name} for not meeting weekly catches requirement.",
                                label="Auto Probation Role Assignment",
                            )
                            title = "⚠️ Command User Probation Role Assigned"
                            await send_probation_report_embed(
                                bot=bot,
                                title=title,
                                member=command_user,
                                catches=command_user_catches,
                                fishes=0,
                                total_catches=command_user_catches,
                            )
                        elif (
                            probation_role in command_user.roles
                            and not kick_role in command_user.roles
                        ):
                            # Add double probation aka kick role
                            await command_user.add_roles(
                                kick_role,
                                reason="Second week of not meeting weekly catches requirement.",
                            )
                            pretty_log(
                                "info",
                                f"Assigned kick role to {command_user.display_name} for second week of not meeting weekly catches requirement.",
                                label="Auto Probation Role Assignment",
                            )
                            title = "⚠️ Command User Double Probation Role Assigned"
                            await send_probation_report_embed(
                                bot=bot,
                                title=title,
                                member=command_user,
                                catches=command_user_catches,
                                fishes=0,
                                total_catches=command_user_catches,
                            )

    # Assign roles to top 10
    for member, username, catches, fishes in known_members:
        member_id = member.id
        total_catches = int(catches) + int(fishes)
        if member_id == HARMLESS_USER_ID:
            continue  # Skip harmless

        if clan_break_role in member.roles:
            continue  # Skip members on clan break

        # Check if member is new to clan
        member_info = vna_members_cache.get(member_id)
        is_new_to_clan = False
        if member_info:
            joined_date = member_info.get("clan_joined_date")
            if joined_date and is_clan_member_less_than_7_days_est(joined_date):
                is_new_to_clan = True

        if is_probation_time and not is_new_to_clan:
            if total_catches < WEEKLY_REQUIREMENT_CATCHES:
                # Assign probation role
                if probation_role not in member.roles:
                    await member.add_roles(
                        probation_role,
                        reason="Did not meet weekly catches requirement.",
                    )
                    pretty_log(
                        "info",
                        f"Assigned probation role to {member.display_name} for not meeting weekly catches requirement.",
                        label="Auto Probation Role Assignment",
                    )
                    await send_probation_report_embed(
                        bot=bot,
                        title="⚠️ Probation Role Assigned",
                        member=member,
                        catches=catches,
                        fishes=fishes,
                        total_catches=total_catches,
                    )
                elif probation_role in member.roles and not kick_role in member.roles:
                    # Add double probation aka kick role
                    await member.add_roles(
                        kick_role,
                        reason="Second week of not meeting weekly catches requirement.",
                    )
                    pretty_log(
                        "info",
                        f"Assigned kick role to {member.display_name} for second week of not meeting weekly catches requirement.",
                        label="Auto Probation Role Assignment",
                    )
                    title = "⚠️ Double Probation Role Assigned"
                    await send_probation_report_embed(
                        bot=bot,
                        title=title,
                        member=member,
                        catches=catches,
                        fishes=fishes,
                        total_catches=total_catches,
                    )
            elif total_catches >= WEEKLY_REQUIREMENT_CATCHES:
                # Remove probation role if met requirements
                roles_to_remove = []
                if probation_role in member.roles:
                    roles_to_remove.append(probation_role)
                if kick_role in member.roles:
                    roles_to_remove.append(kick_role)
                if roles_to_remove:
                    await member.remove_roles(
                        *roles_to_remove,
                        reason="Met weekly catches requirement.",
                    )

                    pretty_log(
                        "info",
                        f"Removed probation/kick roles from {member.display_name} for meeting weekly catches requirement.",
                        label="Auto Probation Role Assignment",
                    )
                    title = "✅ Probation Role Removed"
                    if kick_role in roles_to_remove:
                        title = "✅ Probation and Double Probation Roles Removed"
                    await send_probation_report_embed(
                        bot=bot,
                        title=title,
                        member=member,
                        catches=catches,
                        fishes=fishes,
                        total_catches=total_catches,
                    )
