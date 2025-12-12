import re
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
from utils.cache.cache_list import probation_list_cache, vna_members_cache
from utils.db.kick_list_db import remove_kick_list_member
from utils.db.probation_list_db import remove_probation_member
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.essentials.stats_parsers import (
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.listener_func.weekly_stats_listener import send_probation_report_embed
from utils.logs.pretty_log import pretty_log


async def probation_removal_handler(
    bot: discord.Client,
    member: discord.Member,
    catches: int,
    fishes: int,
    total_catches: int,
):
    # Get roles
    guild = bot.get_guild(VNA_SERVER_ID)
    kick_role = guild.get_role(VN_ALLSTARS_ROLES.kick_list)
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)

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

    probation_member_info = probation_list_cache.get(member.id)
    if not probation_member_info:
        pretty_log(
            "info",
            f"Member {member.display_name} not found in probation list cache.",
            label="Auto Probation Role Assignment",
        )
        msg = f"Member {member.display_name} not found in probation list cache."
        return False, msg
    previous_catch_requirement = probation_member_info.get("catch_requirement", 1500)

    if (
        catches < previous_catch_requirement
        or total_catches < previous_catch_requirement
    ):
        msg = f"Member {member.display_name} did not meet their catch requirement of {previous_catch_requirement} with {catches} catches."
        return False, msg

    if (
        catches >= previous_catch_requirement
        or total_catches >= previous_catch_requirement
    ):

        if probation_role in member.roles:
            await member.remove_roles(
                probation_role,
                reason="Met catch requirement for probation removal.",
            )
            title = "✅ Probation Role Removed"
        elif probation_role in member.roles and kick_role in member.roles:
            await member.remove_roles(
                probation_role,
                kick_role,
                reason="Met catch requirement for probation and kick removal.",
            )
            title = "✅ Probation and Double Probation Roles Removed"
        await send_probation_report_embed(
            bot=bot,
            title=title,
            member=member,
            catches=catches,
            fishes=fishes,
            total_catches=total_catches,
            required_catches=previous_catch_requirement,
        )
        # Remove from probation list db and kick list db
        await remove_probation_member(bot, member)
        await remove_kick_list_member(bot, member)
        return True, None


async def monthly_stats_checker(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):

    # Extract stats from message
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        return

    embed_title = embed.title or ""

    if "Clan Monthly Stats — VN Allstar" not in embed_title:
        return

    embed_description = embed.description or ""
    if not embed_description:
        return

    # Get member first
    command_user = await get_pokemeow_reply_member(before_message)
    if not command_user:
        return

    # Check if probation list is empty
    if not probation_list_cache:
        pretty_log(
            "info",
            "Probation list is empty. Skipping monthly stats probation check.",
            label="Auto Probation Role Assignment",
        )
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
        command_user_catches = int(command_user_top_line_match.group(1).replace(",", ""))
        pretty_log(
            f"Command user catches parsed from embed: {command_user_catches}",
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
    success, msg = await probation_removal_handler(
        bot=bot,
        member=command_user,
        catches=command_user_catches,
        fishes=0,
        total_catches=command_user_catches,
    )
    if not success:
        pretty_log(
            "info",
            msg,
            label="Auto Probation Role Assignment",
        )

    # Assign roles to top 10
    for member, username, catches, fishes in known_members:
        member_id = member.id
        total_catches = int(catches) + int(fishes)
        if member_id == HARMLESS_USER_ID:
            continue  # Skip harmless

        success, msg = await probation_removal_handler(
            bot=bot,
            member=member,
            catches=catches,
            fishes=fishes,
            total_catches=total_catches,
        )
        if not success:
            pretty_log(
                "info",
                msg,
                label="Auto Probation Role Assignment",
            )
            continue
