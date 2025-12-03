import re
from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_joined_date, upsert_member
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.essentials.stats_parsers import fetch_message_obj_from_link
from utils.logs.pretty_log import pretty_log


async def extract_joined_date_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    message_link: str,
):
    """Extract joined date from a message link and update the member's record."""

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Extracting joined date...",
        ephemeral=False,
    )
    # Check if user is a staff member
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can extract joined dates.", ephemeral=True
        )
        return

    # Fetch message object from link
    message, error_message = await fetch_message_obj_from_link(bot, message_link)
    if error_message:
        await loader.error(content=error_message)
        return

    # Parse embed fields
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        await loader.error(content="No embed found in the specified message.")
        return

    # Get current page number from footer
    footer_text = (
        embed.footer.text
    )  # This will give you "Page 1/5 • Stat categories: ;clan stats daily/weekly/monthly/yearly"
    page_match = re.search(r"Page\s+(\d+)/(\d+)", footer_text)

    current_page = None
    total_pages = None
    if page_match:
        current_page = int(page_match.group(1))
        total_pages = int(page_match.group(2))

    user_lines = embed.fields[0].value.splitlines()
    joined_lines = embed.fields[2].value.splitlines()

    summary = {"updated_users": []}
    skipped_users = []
    not_found_users = []
    vna_guild = bot.get_guild(VNA_SERVER_ID)
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    for user_line, joined_line in zip(user_lines, joined_lines):
        parts = user_line.strip().split(" ", 1)
        if len(parts) == 2:
            number = int(parts[0].replace("*", ""))
            user_name = parts[1].replace("**", "").strip()
        else:
            number = None
            user_name = user_line.replace("**", "").strip()
        name_line = f"{number}. {user_name}" if number else user_name
        # Extract unix timestamp from joined line
        joined_clean = joined_line.replace("**", "").strip()
        match = re.search(r"<t:(\d+):[a-zA-Z]>", joined_clean)
        if match:
            joined_clean = int(match.group(1))
        else:

            skipped_users.append((name_line, "Invalid joined date format"))
            continue

        # Look up user id from cache by username
        user_id = fetch_vna_member_id_by_username_or_pokemeow_name(user_name)
        if not user_id:
            not_found_users.append(
                (
                    name_line,
                    f"User not found in cache, Joined Timestamp: {joined_clean}",
                )
            )
            continue

        # Get discord member object
        member = vna_guild.get_member(user_id)
        if not member:
            skipped_users.append((name_line, "Discord member not found"))
            continue

        # Compare joined date
        member_info = vna_members_cache.get(user_id)
        if not member_info:
            not_found_users.append(
                (
                    name_line,
                    f"Member info not found in cache, Joined Timestamp: {joined_clean}",
                )
            )
            continue

        old_joined_date = member_info.get("clan_joined_date")
        updated = False

        if joined_clean and joined_clean != old_joined_date:
            # Update joined date in database
            try:

                await update_member_joined_date(bot, member, joined_clean)
                pretty_log(
                    "success",
                    f"Updated joined date for user '{user_name}' ({user_id}) from {old_joined_date} to {joined_clean}.",
                )
                updated = True
                summary["updated_users"].append(
                    (name_line, old_joined_date, joined_clean)
                )
            except Exception as e:
                pretty_log(
                    "error",
                    f"Error updating joined date for user '{name_line}' ({user_id}): {e}",
                )
                not_found_users.append((name_line, "Database update error"))
                continue
        if not updated:
            skipped_users.append((name_line, "No update needed"))

    # Prepare summary embed
    updated_users = summary.get("updated_users", [])
    if not updated_users and not skipped_users and not not_found_users:
        await loader.success("No users were updated.")
        return

    embed = discord.Embed(
        title="✅ Joined Date Extraction Summary",
        color=MONIKA_EMBED_COLOR,
        timestamp=datetime.now(),
    )
    if current_page:
        page_info = f"Page {current_page}/{total_pages} of VNA members list"
        embed.set_footer(
            text=page_info,
            icon_url=message.guild.icon.url if message.guild.icon else None,
        )

    if updated_users:
        updated_users_count = len(updated_users)
        field_name = f"Updated Users ({updated_users_count})"
        updated_lines = []
        for name_line, old_date, new_date in updated_users:
            if not old_date:
                old_date_str = "N/A"
            else:
                old_date_str = f"<t:{old_date}:D>"
            new_date_str = f"<t:{new_date}:D>"
            updated_lines.append(f"- {name_line}: {old_date_str} ➔ {new_date_str}")
        embed.add_field(
            name=field_name,
            value="\n".join(updated_lines),
            inline=False,
        )
    if skipped_users:
        skip_lines = []
        field_name = f"Skipped Users ({len(skipped_users)})"

        for name_line, reason in skipped_users:
            skip_lines.append(f"- {name_line}: {reason}")

        embed.add_field(
            name=field_name,
            value="\n".join(skip_lines),
            inline=False,
        )
    if not_found_users:
        not_found_lines = []
        field_name = f"Not Found Users ({len(not_found_users)})"

        for name_line, reason in not_found_users:
            not_found_lines.append(f"- {name_line}: {reason}")

        embed.add_field(
            name=field_name,
            value="\n".join(not_found_lines),
            inline=False,
        )
    await loader.success(embed=embed, content="")
