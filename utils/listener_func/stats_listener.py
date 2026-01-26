import re

import discord

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VNA_SERVER_ID
from utils.cache.cache_list import vna_members_cache
from utils.db.db_cleanup import db_cleanup_handler
from utils.db.vna_members_db_func import remove_member, update_member_faction
from utils.listener_func.faction_listener import (
    extract_faction_emoji,
    get_faction_by_emoji,
)
from utils.logs.pretty_log import pretty_log


def extract_clan_name(description: str) -> str:
    """
    Extracts the clan name from a Discord embed description.
    Handles 'Owner of', 'Co-Owner of', 'Member of', and 'None' variants.
    Returns the clan name as a string, or None if not found or 'None'.
    """
    # Find the line containing 'Clan'
    clan_line = None
    for line in description.splitlines():
        if "Clan" in line:
            clan_line = line.strip()
            break
    if not clan_line:
        return None

    # Check for 'None'
    if re.search(r"Clan.*None", clan_line, re.IGNORECASE):
        return None

    # Extract after 'of' (handles emojis and text)
    match = re.search(r"of\s*(?:<a?:\w+:\d+>\s*)?([A-Za-z0-9 ]+)", clan_line)
    if match:
        return match.group(1).strip()

    # Fallback: try to get last word(s) after colon
    parts = clan_line.split(":")
    if len(parts) > 1:
        possible_name = parts[-1].strip()
        if possible_name and possible_name.lower() != "none":
            return possible_name
    return None


async def stats_command_handler(
    bot: discord.Client,
    message: discord.Message,
):
    """Checks for stats command and processes clan stats messages.
    Handles clan membership and faction updates.
    """

    if not message.embeds:
        return

    embed = message.embeds[0]
    if not embed.author or not embed.author.name or not embed.description:
        return

    username = embed.author.name.split("'s ")[0]
    embed_description = embed.description

    clan_name = extract_clan_name(embed_description)
    pretty_log("info", f"Extracted clan name '{clan_name}'")
    # Get member info
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    user_id = fetch_vna_member_id_by_username_or_pokemeow_name(username)
    if not user_id:
        return

    # Check if user_id in members cache
    member_info = vna_members_cache.get(user_id)
    if not member_info:
        return

    # Get member
    guild = bot.get_guild(VNA_SERVER_ID)
    member = guild.get_member(user_id)
    user = None
    if not member:
        user = await bot.fetch_user(user_id)

    else:
        user = member
    # Check if their clan is still VN Allstar
    clan_name = extract_clan_name(embed_description)
    pretty_log("info", f"Extracted clan name '{clan_name}' for member '{user.name}'")
    if member_info and clan_name != "VN Allstar":
        # check if member has vna member role
        if member:
            vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
            if vna_member_role in member.roles:
                # Remove VNA Member role
                await member.remove_roles(
                    vna_member_role, reason="Left VN Allstar clan"
                )
                pretty_log(
                    message=(
                        f"Removed VNA Member role from '{member.display_name}' "
                        f"as they left the VN Allstars clan."
                    ),
                    tag="info",
                    label="Stats Listener",
                )
                return
            elif vna_member_role not in member.roles:
                # Remove from database
                await remove_member(bot=bot, member=member)
                await db_cleanup_handler(bot=bot, user_id=user_id)
                pretty_log(
                    message=(
                        f"Removed '{member.display_name}' from the database "
                        f"as they left the VN Allstars clan."
                    ),
                    tag="info",
                    label="Stats Listener",
                )
                return
        else:
            # Remove from database
            await db_cleanup_handler(bot=bot, user_id=user_id)
            pretty_log(
                message=(
                    f"Removed user_id '{user_id}' from the database "
                    f"as they left the VN Allstars clan."
                ),
                tag="info",
                label="Stats Listener",
            )
    
    # Update faction
    member_faction = member_info.get("faction")
    faction_emoji = extract_faction_emoji(embed_description)
    if faction_emoji:
        faction = None
        faction = get_faction_by_emoji(faction_emoji)
        if faction and member_faction != faction:
            await update_member_faction(bot, member, faction)
            pretty_log(
                message=(
                    f"Updated faction for member '{member.display_name}' "
                    f"from '{member_faction}' to '{faction}'."
                ),
                tag="info",
                label="Stats Listener",
            )
