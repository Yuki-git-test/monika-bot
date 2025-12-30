import re
from datetime import datetime, timedelta, timezone

import discord
import pytz
from discord.ext import commands

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    PROBATION_EXEMPTED_USER_IDS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import (
    kick_list_cache,
    probation_list_cache,
    vna_members_cache,
)
from utils.db.monthly_req_db import get_expected_catches, reset_expected_catches
from utils.db.probation_list_db import (
    update_all_probation_catch_requirements,
    update_probation_catch_requirement,
    upsert_probation_member,
)
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.essentials.stats_parsers import (
    fetch_message_obj_from_link,
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.functions.monthly_requirements_utils import (
    get_member_weeks_in_clan,
    is_member_less_than_a_month_old,
    read_monthly_requirements,
    write_monthly_requirements,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

EXEMPTED_FROM_PROBATION_ROLE_IDS = [
    VN_ALLSTARS_ROLES.clan_break,
    VN_ALLSTARS_ROLES.coowner,
    VN_ALLSTARS_ROLES.staff,
    VN_ALLSTARS_ROLES.legendary_donator,
    VN_ALLSTARS_ROLES.shiny_donator,
    VN_ALLSTARS_ROLES.owner,
]

EXPECTED_CATCHES = set()
PROBATION_LIST_DAYS = [6, 13, 20, 27]  # Every Saturday
WEEKLY_REQUIREMENT_CATCHES = 1500
MODERATOR_PLAY_CHANNEL_ID = 952810535928348732
PROCESSED_WEEKLY_STATS_PAGES = set()
PROCESSED_WEEKLY_STATS_END_TIMESTAMPS = set()
NEW_EXPECTED_CATCHES = None


def is_past_11pm_probation_day_est():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day in PROBATION_LIST_DAYS and now_est.hour >= 23


def is_saturday_30min_before_midnight_est(now=None):
    """
    Returns True if the current time (or provided datetime) is Saturday,
    between 11:30 PM and 11:59:59 PM EST.
    """
    est = pytz.timezone("US/Eastern")
    if now is None:
        now = datetime.now(est)
    else:
        now = now.astimezone(est)
    return (
        now.weekday() == 5  # Saturday (Monday=0)
        and now.hour == 23
        and 30 <= now.minute < 60
    )


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
    required_catches: int = None,
    old_required_catches: int = None,
    clan_joined_date: int = None,
):
    if "add" in title.lower() or "assigned" in title.lower():
        color = discord.Color.red()
    else:
        color = discord.Color.green()

    required_catches_text = ""
    if required_catches:
        required_catches_text = f"**Required Catches:** {required_catches:,}\n"
        if old_required_catches:
            required_catches_text += (
                f"**Previous Required Catches:** {old_required_catches:,}\n"
            )
    embed = discord.Embed(
        title=title,
        description=(
            f"**Member:** {member.mention} ({member.display_name})\n"
            f"**Catches:** {catches}\n"
            f"**Fishes:** {fishes}\n"
            f"**Total Catches:** {total_catches}\n"
            f"{required_catches_text}"
            f"**Clan Joined Date:** <t:{clan_joined_date}:D> <t:{clan_joined_date}:R> \n"
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


async def probation_assignment_handler(
    bot: discord.Client,
    member: discord.Member,
    catches: int,
    fishes: int,
    total_catches: int,
):

    # Get roles
    guild = bot.get_guild(VNA_SERVER_ID)
    kick_role = guild.get_role(VN_ALLSTARS_ROLES.kick_list)
    clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    if staff_role in member.roles:
        msg = f"Member {member.display_name} is a staff member."
        return False, msg

    # Get member info
    member_info = vna_members_cache.get(member.id)
    if not member_info:
        pretty_log(
            "info",
            f"Member {member.display_name} not found in VNA members cache.",
            label="Auto Probation Role Assignment",
        )
        msg = f"Member {member.display_name} not found in VNA members cache."
        return False, msg

    joined_date = member_info.get("clan_joined_date")
    pokemeow_name = member_info.get("pokemeow_name", "Unknown")
    is_new_to_clan = False

    if joined_date and is_clan_member_less_than_7_days_est(joined_date):
        is_new_to_clan = True
        pretty_log(
            "info",
            f"Member {member.display_name} is new to clan (joined less than 7 days).",
            label="Auto Probation Role Assignment",
        )
        msg = f"Member {member.display_name} is new to clan (joined less than 7 days)."
        return False, msg

    if (
        catches >= WEEKLY_REQUIREMENT_CATCHES
        or total_catches >= WEEKLY_REQUIREMENT_CATCHES
    ):
        msg = f"Member {member.display_name} met weekly catches requirement with {catches} catches."
        return False, msg

    if clan_break_role in member.roles:
        # Skip members on clan break
        msg = f"Member {member.display_name} is on clan break."
        return False, msg

    upsert_catch_requirement = NEW_EXPECTED_CATCHES
    if is_member_less_than_a_month_old(member.id):
        week_in_clan = get_member_weeks_in_clan(member.id)
        upsert_catch_requirement = WEEKLY_REQUIREMENT_CATCHES * week_in_clan

    if (
        catches < WEEKLY_REQUIREMENT_CATCHES
        and total_catches < WEEKLY_REQUIREMENT_CATCHES
    ):
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
                clan_joined_date=joined_date,
            )
            # Upsert to probation list db with 1500 catch requirement
            await upsert_probation_member(
                bot=bot,
                user=member,
                pokemeow_name=pokemeow_name,
                catch_requirement=upsert_catch_requirement,
            )
            return True, None
        elif probation_role in member.roles:
            # Get current catch requirement from cache
            probation_member_info = probation_list_cache.get(member.id)
            previous_catch_requirement = probation_member_info.get(
                "catch_requirement", 1500
            )
            int_previous_catch_requirement = int(previous_catch_requirement)
            new_catch_requirement = (
                int_previous_catch_requirement + WEEKLY_REQUIREMENT_CATCHES
            )

            # Add double probation aka kick role
            if kick_role not in member.roles:
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
                    required_catches=new_catch_requirement,
                    old_required_catches=int_previous_catch_requirement,
                    clan_joined_date=joined_date,
                )
            elif kick_role in member.roles:
                title = "⚠️ Catch Requirement Updated for Member"
                await send_probation_report_embed(
                    bot=bot,
                    title=title,
                    member=member,
                    catches=catches,
                    fishes=fishes,
                    total_catches=total_catches,
                    required_catches=new_catch_requirement,
                    old_required_catches=int_previous_catch_requirement,
                    clan_joined_date=joined_date,
                )
            # Update catch requirement in db
            await update_probation_catch_requirement(
                bot=bot,
                user=member,
                catch_requirement=new_catch_requirement,
            )
            return True, None


async def weekly_stats_checker(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):

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

    # Check if 10 minutes before midnight EST on Saturday
    if not is_saturday_30min_before_midnight_est():
        pretty_log(
            "info",
            "Not the scheduled time for weekly stats check reminder.",
            label="Weekly Stats Listener",
        )
        return

    if after_message.channel.id != MODERATOR_PLAY_CHANNEL_ID:
        pretty_log(
            "info",
            "Weekly stats message not in the designated Moderator Play channel.",
            label="Weekly Stats Listener",
        )
        return

    # Get reset timestamp from embed description
    reset_timestamp = None
    match = re.search(r"<t:(\d+):f>", embed_description)
    if not match:
        return

    reset_timestamp = int(match.group(1))
    if reset_timestamp not in PROCESSED_WEEKLY_STATS_END_TIMESTAMPS:
        # Clear processed pages for new reset
        PROCESSED_WEEKLY_STATS_PAGES.clear()
        # Clear processed timestamps
        PROCESSED_WEEKLY_STATS_END_TIMESTAMPS.clear()

        PROCESSED_WEEKLY_STATS_END_TIMESTAMPS.add(reset_timestamp)

    # Get current page number from footer
    footer_text = (
        embed.footer.text
    )  # This will give you "Page 1/5 • Stat categories: ;clan stats daily/weekly/monthly/yearly"
    page_match = re.search(r"Page\s+(\d+)/(\d+)", footer_text)
    if not page_match:
        return
    current_page = int(page_match.group(1))
    total_pages = int(page_match.group(2))

    if current_page in PROCESSED_WEEKLY_STATS_PAGES:
        pretty_log(
            "info",
            f"Weekly stats page {current_page} has already been processed. Skipping.",
            label="Weekly Stats Listener",
        )
        return

    PROCESSED_WEEKLY_STATS_PAGES.add(current_page)
    expected_catches = await get_expected_catches(bot)
    global EXPECTED_CATCHES
    EXPECTED_CATCHES = expected_catches
    pretty_log(
        "info",
        f"Updated monthly expected catches to {EXPECTED_CATCHES} in monthly_requirements.json.",
        label="Weekly Stats Listener",
    )

    # Get member first
    command_user = await get_pokemeow_reply_member(before_message)
    if not command_user:
        return

    # Get roles
    guild = bot.get_guild(VNA_SERVER_ID)

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
                f"Logged {unknow_member_count} unknown members to server log channel.",
                label="Auto Probation Role Assignment",
            )

    # Get top line
    command_user_catches = 0
    command_user_top_line_match = re.search(
        r".*You're Rank \d+ in your clan's weekly stats — with ([\d,]+) catches!",
        embed_description,
    )
    if command_user_top_line_match:
        user_catches = int(command_user_top_line_match.group(1).replace(",", ""))
        pretty_log(
            f"Command user catches parsed from embed: {user_catches}",
        )

    # Check command user first
    command_user_id = command_user.id
    command_user = guild.get_member(command_user_id)
    if command_user:
        success, message = await probation_assignment_handler(
            bot=bot,
            member=command_user,
            catches=command_user_catches,
            fishes=0,
            total_catches=command_user_catches,
        )
        if success:
            pretty_log(
                "info",
                f"Processed probation assignment for command user {command_user.display_name}.",
                label="Auto Probation Role Assignment",
            )
        else:
            pretty_log(
                "info",
                f"Skipped probation assignment for command user {command_user.display_name}. Reason: {message}",
                label="Auto Probation Role Assignment",
            )

    # Assign roles to top 10
    for member, username, catches, fishes in known_members:
        member_id = member.id
        total_catches = int(catches) + int(fishes)
        if member_id in PROBATION_EXEMPTED_USER_IDS:
            continue  # Skip probation exempted users

        if any(role.id in EXEMPTED_FROM_PROBATION_ROLE_IDS for role in member.roles):
            continue  # Skip members on clan break, coowners, or staff
        success, message = await probation_assignment_handler(
            bot=bot,
            member=member,
            catches=int(catches),
            fishes=int(fishes),
            total_catches=total_catches,
        )
        if success:
            pretty_log(
                "info",
                f"Processed probation assignment for {member.display_name}.",
                label="Auto Probation Role Assignment",
            )
        else:
            pretty_log(
                "info",
                f"Skipped probation assignment for {member.display_name}. Reason: {message}",
                label="Auto Probation Role Assignment",
            )
            continue

    if current_page == total_pages:
        # At the end of all pages, update all probation members' catch requirements those who didnt get updated
        await update_all_probation_catch_requirements(bot)
        pretty_log(
            "info",
            "Updated all probation members' catch requirements after processing all weekly stats pages.",
            label="Auto Probation Role Assignment",
        )
