import asyncio
import re
import zoneinfo
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

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
    DAILY_CATCH_REQUIREMENT,
    MONTHLY_CATCH_REQUIREMENT
)
from utils.cache.cache_list import probation_list_cache, vna_members_cache
from utils.db.probation_list_db import (
    update_probation_catch_requirement_by_id,
    update_stacking_requirements,
    upsert_probation_member,
)
from utils.db.vna_members_db_func import update_member_last_month_catches
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.essentials.stats_parsers import (
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.functions.webhook_func import send_webhook
from utils.listener_func.weekly_stats_listener import send_probation_report_embed
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.probation_assignment_removal_handler")
enable_debug(f"{__name__}.new_monthly_stats_checker")
EXEMPTED_FROM_PROBATION_ROLE_IDS = [
    VN_ALLSTARS_ROLES.clan_break,
    VN_ALLSTARS_ROLES.coowner,
    VN_ALLSTARS_ROLES.staff,
    VN_ALLSTARS_ROLES.legendary_donator,
    VN_ALLSTARS_ROLES.shiny_donator,
    VN_ALLSTARS_ROLES.owner,
]
PROBATION_ASSIGNMENT_DAYS = [7, 14, 21, 28]
PROCESSED_MONTHLY_STATS_PAGES = set()
PROCESSED_WEEKLY_STATS_END_TIMESTAMPS = set()
UNKNOWN_MEMBERS = set()


def is_exempted_from_probation(member: discord.Member) -> bool:
    """
    Check if a member is exempted from probation based on their roles.
    """
    for role_id in EXEMPTED_FROM_PROBATION_ROLE_IDS:
        if discord.utils.get(member.roles, id=role_id):
            debug_log(
                f"Member {member.display_name} is exempted from probation due to role ID {role_id}."
            )
            return True
    debug_log(f"Member {member.display_name} is NOT exempted from probation.")
    return False


def get_est_day_number():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    debug_log(f"Current EST day number: {now_est.day}")
    return now_est.day  # Returns the day of the month as int


def get_est_hour():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    debug_log(f"Current EST hour: {now_est.hour}")
    return now_est.hour  # Returns the hour (0-23) in EST


def get_last_day_of_month_est(dt: Optional[datetime] = None) -> datetime:
    """
    Returns the last day of the month for the given datetime in EST.
    If no datetime is provided, uses the current time.
    """
    est = pytz.timezone("US/Eastern")
    if dt is None:
        dt = datetime.now(est)
    else:
        dt = dt.astimezone(est)
    # Move to the first day of the next month, then subtract one day
    next_month = dt.replace(day=1) + timedelta(days=32)
    last_day = next_month.replace(day=1) - timedelta(days=1)
    debug_log(f"Last day of month in EST: {last_day}")
    return last_day


async def send_probation_report(
    bot: discord.Client,
    guild: discord.Guild,
    member: discord.Member,
    title: str,
    color: discord.Color,
    catches: int,
    total_catches: int,
    required_catches: int,
    context: str,
    fishes: int = None,
    last_month_catches: int = None,
):
    debug_log(
        f"Preparing to send probation report for {member.display_name} (ID: {member.id}), title: {title}, catches: {catches}, fishes: {fishes}, total_catches: {total_catches}, required_catches: {required_catches}, context: {context}, last_month_catches: {last_month_catches}"
    )
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    if log_channel:
        description_w_fish = (
            f"**Member:** {member.mention}\n"
            f"**Pokémon Caught:** {catches:,}\n"
            f"**Fish Caught:** {fishes:,}\n"
            f"**Total Catches:** {total_catches:,}\n"
            f"**Catch Requirements:** {required_catches:,}\n"
        )
        description_wo_fish = (
            f"**Member:** {member.mention}\n"
            f"**Pokémon Caught:** {catches:,}\n"
            f"**Total Catches:** {total_catches:,}\n"
            f"**Catch Requirements:** {required_catches:,}\n"
        )
        description_for_double_probation_wo_fish = (
            f"**Member:** {member.mention}\n"
            f"**Pokémon Caught:** {catches:,}\n"
            f"**Total Catches:** {total_catches:,}\n"
            f"**Last Month Catches:** {last_month_catches if last_month_catches is not None else 0:,}\n"
            f"**Catch Requirements:** {required_catches:,}\n"
        )
        description_for_double_probation_w_fish = (
            f"**Member:** {member.mention}\n"
            f"**Pokémon Caught:** {catches:,}\n"
            f"**Fish Caught:** {fishes:,}\n"
            f"**Total Catches:** {total_catches:,}\n"
            f"**Last Month Catches:** {last_month_catches if last_month_catches is not None else 0:,}\n"
            f"**Catch Requirements:** {required_catches:,}\n"
        )
        desc = description_w_fish
        if context == "Command User":
            desc = description_wo_fish
            title = title + " (Command User)"
            if "Double" in title:
                desc = description_for_double_probation_wo_fish
        if context == "Member Loop" and "Double" in title:
            desc = description_for_double_probation_w_fish

        embed = discord.Embed(
            title=title,
            description=desc,
            color=color,
            timestamp=datetime.now(),
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}", icon_url=guild.icon.url)
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
        debug_log(
            f"Sent probation report embed for {member.display_name} to log channel {log_channel.name if hasattr(log_channel, 'name') else log_channel.id}"
        )


async def probation_assignment_removal_handler(
    bot: discord.Client,
    guild: discord.Guild,
    current_day: int,
    current_hour: int,
    member: discord.Member,
    catches: int,
    fishes: int,
    total_catches: int,
    context: str = None,
):
    # Get roles
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)
    double_probation_role = guild.get_role(VN_ALLSTARS_ROLES.kick_list)

    # Determine global requirement
    current_day = get_est_day_number()
    current_hour = get_est_hour()

    # just update stats if its last day of the month and 11pm est or later
    last_day_est = get_last_day_of_month_est()
    now_est = datetime.now(pytz.timezone("US/Eastern"))
    if now_est.day == last_day_est.day and now_est.hour >= 23:
        # Update last month catches
        await update_member_last_month_catches(bot, member.id, catches)
        pretty_log(
            "info",
            f"Updated last month catches for member {member.display_name} ({member.id}) to {catches}.",
            label="Monthly Stats Listener",
        )
        debug_log(
            f"Updated last month catches for {member.display_name} to {catches} (last day of month logic)"
        )
    if is_exempted_from_probation(member):
        msg = (
            f"Member {member.display_name} is exempted from probation role assignment."
        )
        debug_log(
            f"Probation assignment skipped for {member.display_name}: exempted from probation."
        )
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
        debug_log(
            f"Probation assignment skipped for {member.display_name}: not found in VNA members cache."
        )
        return False, msg

    joined_date = member_info.get("clan_joined_date")
    last_month_catches = member_info.get("last_month_catches", 0)
    probation_member_info = probation_list_cache.get(member.id)
    pokemeow_name = member_info.get("pokemeow_name", "Unknown")

    # Global catch requirement logic
    global_catch_requirement = current_day * DAILY_CATCH_REQUIREMENT
    debug_log(
        f"Global catch requirement for {member.display_name}: {global_catch_requirement}"
    )

    # Determine if member is new this month
    eastern = pytz.timezone("US/Eastern")
    now_est = datetime.now(eastern)
    month_start = now_est.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    month_end = next_month - timedelta(seconds=1)
    user_joined_dt = (
        datetime.fromtimestamp(joined_date, tz=eastern) if joined_date else None
    )
    new_member = False

    # Determine per-member requirement
    # Adjust Requirements for New Members
    if joined_date and month_start <= user_joined_dt <= month_end:
        days_in_clan = (now_est - user_joined_dt).days
        member_required_catches = days_in_clan * DAILY_CATCH_REQUIREMENT
        new_member = True
        debug_log(
            f"Member {member.name} is a new member. Days in clan this month: {days_in_clan}. Required catches: {member_required_catches}",
        )
        debug_log(
            f"New member logic for {member.display_name}: days_in_clan={days_in_clan}, required_catches={member_required_catches}"
        )
    else:
        member_required_catches = global_catch_requirement
        # Double Probation Logic
        if double_probation_role in member.roles:
            probation_member_info = probation_list_cache.get(member.id)
            if probation_member_info:
                stacking_requirements = probation_member_info.get(
                    "stacking_requirements", 0
                )
                catch_requirement = stacking_requirements + global_catch_requirement
                member_required_catches = catch_requirement
                debug_log(
                    f"Double probation logic for {member.display_name}: stacking_requirements={stacking_requirements}, catch_requirement={catch_requirement}"
                )
            else:
                member_required_catches = global_catch_requirement
                debug_log(
                    f"Double probation logic for {member.display_name}: no stacking_requirements found, using global_catch_requirement={global_catch_requirement}"
                )

    # Probation Removal
    if catches >= member_required_catches or total_catches >= member_required_catches:
        if probation_role in member.roles:
            roles_to_remove = [probation_role]
            title = f"✅ Probation Role Auto-Removed"
            color = discord.Color.green()
            if double_probation_role in member.roles:
                roles_to_remove.append(double_probation_role)
                title = f"✅ Double Probation and Probation Roles Auto-Removed"
                roles_to_remove.append(double_probation_role)
            await member.remove_roles(*roles_to_remove, reason="Met catch requirements")
            # Get last month catches before updating
            member_info = vna_members_cache.get(member.id)
            last_month_catches = member_info.get("last_month_catches", 0)
            await send_probation_report(
                bot=bot,
                guild=guild,
                member=member,
                title=title,
                color=color,
                catches=catches,
                total_catches=total_catches,
                required_catches=member_required_catches,
                context=context,
                fishes=fishes,
                last_month_catches=last_month_catches,
            )
            msg = (
                f"Probation role removed from member {member.display_name} "
                f"for meeting catch requirements."
            )
            debug_log(
                f"Removed probation (and possibly double probation) role(s) from {member.display_name} for meeting requirements. Roles removed: {[r.name for r in roles_to_remove if hasattr(r, 'name')]}"
            )
            return True, msg
        else:
            msg = (
                f"Member {member.display_name} has met catch requirements but "
                f"does not have probation role."
            )
            debug_log(
                f"{member.display_name} met catch requirements but did not have probation role."
            )
            return False, msg

    # Member did not meet requirements
    elif catches < member_required_catches and total_catches < member_required_catches:
        if probation_role in member.roles and current_day == 7 and current_hour >= 23:
            if double_probation_role not in member.roles and last_month_catches < MONTHLY_CATCH_REQUIREMENT:
                stacking_requirements = MONTHLY_CATCH_REQUIREMENT - last_month_catches
                await update_stacking_requirements(
                    bot=bot,
                    user_id=member.id,
                    stacking_requirements=stacking_requirements,
                )
                # Upgrade to Double Probation
                await member.add_roles(
                    double_probation_role, reason="Did not meet catch requirements"
                )
                title = f"⚠️ Double Probation Role Auto-Assigned"
                color = discord.Color.dark_orange()
                # Get last month catches before updating
                member_info = vna_members_cache.get(member.id)
                last_month_catches = member_info.get("last_month_catches", 0)
                member_required_catches = global_catch_requirement + last_month_catches
                await send_probation_report(
                    bot=bot,
                    guild=guild,
                    member=member,
                    title=title,
                    color=color,
                    catches=catches,
                    total_catches=total_catches,
                    required_catches=member_required_catches,
                    context=context,
                    fishes=fishes,
                    last_month_catches=last_month_catches,
                )
                # Update catch requirement in DB
                await update_probation_catch_requirement_by_id(
                    bot=bot,
                    user_id=member.id,
                    catch_requirement=member_required_catches,
                )
                msg = (
                    f"Double Probation role assigned to member {member.display_name} "
                    f"for not meeting catch requirements."
                )
                debug_log(
                    f"Assigned double probation role to {member.display_name}. stacking_requirements={stacking_requirements}, last_month_catches={last_month_catches}, member_required_catches={member_required_catches}"
                )
                return True, msg
            elif double_probation_role in member.roles:
                # Update catch requirement in DB
                member_info = vna_members_cache.get(member.id)
                last_month_catches = member_info.get("last_month_catches", 0)
                old_stacking_requirements = probation_member_info.get(
                    "stacking_requirements", 0
                )
                new_stacking_requirements = MONTHLY_CATCH_REQUIREMENT - last_month_catches
                total_stacking_requirements = (
                    old_stacking_requirements + new_stacking_requirements
                )
                day_catch_requirement = current_day * DAILY_CATCH_REQUIREMENT
                new_catch_requirement = (
                    day_catch_requirement + total_stacking_requirements
                )
                await update_probation_catch_requirement_by_id(
                    bot=bot,
                    user_id=member.id,
                    catch_requirement=new_catch_requirement,
                )
                await update_stacking_requirements(
                    bot=bot,
                    user_id=member.id,
                    stacking_requirements=total_stacking_requirements,
                )
                title = f"⚠️ Double Probation Catch Requirement Updated"
                color = discord.Color.dark_orange()
                # Get last month catches before updating
                member_info = vna_members_cache.get(member.id)
                last_month_catches = member_info.get("last_month_catches", 0)
                await send_probation_report(
                    bot=bot,
                    guild=guild,
                    member=member,
                    title=title,
                    color=color,
                    catches=catches,
                    total_catches=total_catches,
                    required_catches=new_catch_requirement,
                    context=context,
                    fishes=fishes,
                    last_month_catches=last_month_catches,
                )
                msg = (
                    f"Updated catch requirement for double probation member "
                    f"{member.display_name}."
                )
                debug_log(
                    f"Updated double probation catch requirement for {member.display_name}. old_stacking_requirements={old_stacking_requirements}, new_stacking_requirements={new_stacking_requirements}, total_stacking_requirements={total_stacking_requirements}, new_catch_requirement={new_catch_requirement}"
                )
                return True, msg
        elif (
            probation_role not in member.roles
            and current_day in PROBATION_ASSIGNMENT_DAYS
            and current_hour >= 23
        ):
            await member.add_roles(
                probation_role, reason="Did not meet catch requirements"
            )
            title = f"⚠️ Probation Role Auto-Assigned"
            color = discord.Color.orange()
            await send_probation_report(
                bot=bot,
                guild=guild,
                member=member,
                title=title,
                color=color,
                catches=catches,
                total_catches=total_catches,
                required_catches=member_required_catches,
                context=context,
                fishes=fishes,
                last_month_catches=last_month_catches,
            )
            # Upsert in DB
            await upsert_probation_member(
                bot=bot,
                user=member,
                pokemeow_name=pokemeow_name,
                catch_requirement=member_required_catches,
            )

            msg = (
                f"Probation role assigned to member {member.display_name} "
                f"for not meeting catch requirements."
            )
            debug_log(
                f"Assigned probation role to {member.display_name}. member_required_catches={member_required_catches}, catches={catches}, fishes={fishes}"
            )
            return True, msg
        else:
            # Did not meet requirements but its not probation assignment day
            msg = (
                f"Member {member.display_name} has not met catch requirements. "
                f"No action taken as it is not a probation assignment day."
            )
            debug_log(
                f"No probation action for {member.display_name}: not a probation assignment day or requirements not met."
            )


async def new_monthly_stats_checker(
    bot: discord.Client,
    before_message: discord.Message,
    after_message: discord.Message,
    replied_member_id: int = None,
):
    debug_log("Starting new_monthly_stats_checker")
    guild = bot.get_guild(VNA_SERVER_ID)
    command_user = None
    # Get member first
    if not replied_member_id:
        command_user = await get_pokemeow_reply_member(before_message)
        debug_log(
            f"get_pokemeow_reply_member returned: {command_user.display_name if command_user else 'None'}"
        )
        if not command_user:
            # Fallback: try to get the user from the slash command interaction
            interaction = getattr(before_message, "interaction", None)
            if (
                interaction
                and hasattr(interaction, "user")
                and isinstance(interaction.user, discord.Member)
            ):
                command_user = interaction.user
                debug_log(
                    f"Found command_user from interaction: {command_user.display_name}"
                )
            else:
                # Try to get from raw_data if available (for REST fetches)
                if (
                    hasattr(before_message, "raw_data")
                    and "interaction" in before_message.raw_data
                ):
                    user_data = before_message.raw_data["interaction"].get("user")
                    if user_data and "id" in user_data:
                        guild = before_message.guild
                        if guild:
                            command_user = guild.get_member(int(user_data["id"]))
                            debug_log(
                                f"Found command_user from raw_data: {command_user.display_name if command_user else 'None'}"
                            )
            if not command_user:
                debug_log("No command_user found, aborting new_monthly_stats_checker.")
                return
    else:
        command_user = guild.get_member(replied_member_id)
        debug_log(
            f"Found command_user from replied_member_id: {command_user.display_name if command_user else 'None'}"
        )
        if not command_user:
            debug_log(
                "No command_user found for replied_member_id, aborting new_monthly_stats_checker."
            )
            return
    # Get probation role
    guild = bot.get_guild(VNA_SERVER_ID)
    clan_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)

    # Check if member has clan member role
    if clan_role not in command_user.roles:
        debug_log(
            f"Command user {command_user.display_name} does not have clan member role, aborting."
        )
        return

    # Return if date is 1st to 7th EST
    current_day = get_est_day_number()
    current_hour = get_est_hour()

    #  Check catches from message embed
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        debug_log("No embed found in after_message, aborting.")
        return
    embed_description = embed.description
    if not embed_description:
        debug_log("No embed description found, aborting.")
        return

    # Get reset timestamp from embed description
    reset_timestamp = None
    match = re.search(r"<t:(\d+):f>", embed_description)
    if not match:
        debug_log("No reset timestamp found in embed description, aborting.")
        return

    reset_timestamp = int(match.group(1))

    # Get current page number from footer
    footer_text = (
        embed.footer.text
    )  # This will give you "Page 1/5 • Stat categories: ;clan stats daily/weekly/monthly/yearly"
    page_match = re.search(r"Page\s+(\d+)/(\d+)", footer_text)
    if not page_match:
        debug_log("No page number found in embed footer, aborting.")
        return
    current_page = int(page_match.group(1))
    total_pages = int(page_match.group(2))

    if current_page in PROCESSED_MONTHLY_STATS_PAGES:
        pretty_log(
            "info",
            f"Monthly stats page {current_page} has already been processed. Skipping.",
            label="Monthly Stats Listener",
        )
        debug_log(f"Monthly stats page {current_page} already processed, skipping.")
        return

    PROCESSED_MONTHLY_STATS_PAGES.add(current_page)

    # Parse clan stats message
    clan_members_stats = parse_clan_stats_message(embed_description)
    if not clan_members_stats:
        debug_log(
            "No clan members stats found in the monthly stats message.",
        )
        debug_log("No clan_members_stats parsed from embed description, aborting.")
        return

    # Split known and unknown members
    guild = bot.get_guild(VNA_SERVER_ID)
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)

    # Get top line
    command_user_catches = 0
    command_user_top_line_match = re.search(
        r".*You're Rank \d+ in your clan's monthly stats — with ([\d,]+) catches!",
        embed_description,
    )
    if command_user_top_line_match:
        command_user_catches = int(
            command_user_top_line_match.group(1).replace(",", "")
        )
        debug_log(
            f"command user_catches parsed from embed: {command_user_catches}",
            highlight=True,
        )
        pretty_log(
            f"Command user catches parsed from embed: {command_user_catches}",
        )
    else:
        debug_log("Could not parse command user catches from embed description.")
    # Check command user first
    command_user_id = command_user.id
    command_user = guild.get_member(command_user_id)
    if command_user:
        success, msg = await probation_assignment_removal_handler(
            bot=bot,
            guild=guild,
            current_day=current_day,
            current_hour=current_hour,
            member=command_user,
            catches=command_user_catches,
            fishes=0,
            total_catches=command_user_catches,
            context="Command User",
        )
        if success:
            pretty_log(
                "info",
                f"Auto probation handler processed command user {command_user.display_name}: {msg}",
                label="Weekly Stats Listener",
            )
            debug_log(
                f"Probation handler processed command user {command_user.display_name}: {msg}"
            )
        else:
            pretty_log(
                "info",
                f"Auto probation handler for command user {command_user.display_name}: {msg}",
                label="Weekly Stats Listener",
            )
            debug_log(
                f"Probation handler for command user {command_user.display_name}: {msg}"
            )

    # Now process all other members
    known_members, unknown_members = await split_known_and_unknown_members(
        bot=bot,
        guild=guild,
        members=clan_members_stats,
    )

    if unknown_members:
        global UNKNOWN_MEMBERS

        for username, catches, fishes in unknown_members:
            # If it's already in the global set, skip
            if (username, catches, fishes) in UNKNOWN_MEMBERS:
                continue

            # Add to global unknown members set
            UNKNOWN_MEMBERS.add((username, catches, fishes))
            debug_log(
                f"Added unknown member: {username}, catches: {catches}, fishes: {fishes}"
            )

    for member, username, catches, fishes in known_members:
        member_id = member.id
        total_catches = int(catches) + int(fishes)
        if member_id in PROBATION_EXEMPTED_USER_IDS:
            continue  # Skip probation exempted users
        if is_exempted_from_probation(member):
            pretty_log(
                "info",
                f"Member {member.display_name} is exempted from probation role assignment.",
                label="Auto Probation Role Assignment",
            )
            continue
        debug_log(
            f"Processing known member: {member.display_name}, catches: {catches}, fishes: {fishes}, total_catches: {total_catches}"
        )
        success, msg = await probation_assignment_removal_handler(
            bot=bot,
            guild=guild,
            current_day=current_day,
            current_hour=current_hour,
            member=member,
            catches=int(catches),
            fishes=int(fishes),
            total_catches=total_catches,
            context="Member",
        )
        if success:
            pretty_log(
                "info",
                f"Auto probation handler processed member {member.display_name}: {msg}",
                label="Weekly Stats Listener",
            )
            debug_log(
                f"Probation handler processed member {member.display_name}: {msg}"
            )
        else:
            pretty_log(
                "info",
                f"Auto probation handler for member {member.display_name}: {msg}",
                label="Weekly Stats Listener",
            )
            debug_log(f"Probation handler for member {member.display_name}: {msg}")
    # After processing all pages, send probation report for unknown members
    if current_page == total_pages:
        # Clear processed pages for next month
        PROCESSED_MONTHLY_STATS_PAGES.clear()

        debug_log("Cleared PROCESSED_MONTHLY_STATS_PAGES for next month.")

        # Log unknown members if any
        if UNKNOWN_MEMBERS:
            unknown_members = list(UNKNOWN_MEMBERS)
            UNKNOWN_MEMBERS.clear()  # Clear after copying
            debug_log(
                f"Logging {len(unknown_members)} unknown members to server log channel."
            )
            if unknown_members:
                desc_lines = []
                for username, catches, fishes in unknown_members:
                    desc_lines.append(
                        f"- {username} (Catches: {catches}, Fishes: {fishes})"
                    )
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
                unknown_member_count = len(unknown_members)
                embed.set_footer(
                    text=f"Total Unknown Members: {unknown_member_count}",
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
                        f"Logged {unknown_member_count} unknown members to server log channel.",
                        label="Auto Probation Role Assignment",
                    )
                    # Send in the same channel a reminder to staff
                    await after_message.channel.send(embed=embed)
                    pretty_log(
                        "info",
                        f"Sent unknown members reminder in channel {after_message.channel.name}.",
                        label="Auto Probation Role Assignment",
                    )
                    debug_log(
                        f"Sent unknown members embed to log channel and after_message.channel: {after_message.channel.name}"
                    )
