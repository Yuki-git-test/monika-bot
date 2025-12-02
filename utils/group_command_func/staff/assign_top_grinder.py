import re
from datetime import datetime, timedelta

import discord
import pytz
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
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


async def assign_top_grinder_roles(
    bot: commands.Bot,
    interaction: discord.Interaction,
    message_link: str,
):
    # Defer response
    loader = await pretty_defer(
        interaction=interaction, content="Processing...", ephemeral=True
    )

    # Check if user is a staff member
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await loader.error("You do not have permission to use this command.")
        return

    # Parse message link
    message, error_message = await fetch_message_obj_from_link(bot, message_link)
    if error_message:
        await loader.error(error_message)
        return

    # Extract stats from message
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        await loader.error("The provided message does not contain an embed.")
        return

    embed_title = embed.title or ""

    if "Clan Monthly Stats — VN Allstar" not in embed_title:
        await loader.error("The embed title is not recognized for VN Allstars stats.")
        return

    embed_description = embed.description or ""
    if not embed_description:
        await loader.error("The embed does not contain a description.")
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
        await loader.error("Please provide the message link of the first page.")
        return

    # Parse clan stats from embed description
    clan_members_stats = parse_clan_stats_message(embed_description)
    if not clan_members_stats:
        await loader.error("No clan member stats found in the embed description.")
        return

    # Split known and unknown members
    guild = bot.get_guild(VNA_SERVER_ID)
    known_members, unknown_members = await split_known_and_unknown_members(
        bot=bot,
        guild=guild,
        members=clan_members_stats,
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
    else:
        # Remove existing top grinder roles from all members
        for member in guild.members:
            if top_grinder_role in member.roles:
                await member.remove_roles(top_grinder_role)

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

    await loader.success("Top Monthly Grinder roles have been assigned successfully.")
