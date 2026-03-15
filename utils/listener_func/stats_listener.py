import re
from typing import Optional

import discord

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VNA_SERVER_ID
from utils.cache.cache_list import vna_members_cache
from utils.db.db_cleanup import db_cleanup_handler
from utils.db.vna_members_db_func import remove_member, update_member_faction
from utils.listener_func.faction_listener import (
    extract_faction_emoji,
    get_faction_by_emoji,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.stats_command_handler")


def extract_user_id_from_command(content: str) -> Optional[int]:
    """
    Extracts the user ID from a command snippet like ';stats 123456789012345678'.
    Returns the user ID as an integer if found, else None.
    """
    match = re.search(r";(?:stats|pro|profile)\s+(\d{15,21})", content)
    if match:
        return int(match.group(1))
    return None


def extract_clan_name(description: str) -> str:
    """
    Extracts the clan name from a Discord embed description.
    Handles 'Owner of', 'Co-Owner of', 'Member of', and 'None' variants.
    Returns the clan name as a string, or None if not found or 'None'.
    """
    debug_log(f"extract_clan_name: description='{description}'")
    # Find the line containing 'Clan'
    clan_line = None
    for line in description.splitlines():
        debug_log(f"extract_clan_name: checking line='{line}'")
        if "Clan" in line:
            clan_line = line.strip()
            debug_log(f"extract_clan_name: found clan_line='{clan_line}'")
            break
    if not clan_line:
        debug_log("extract_clan_name: clan_line not found")
        return None

    # Check for 'None'
    if re.search(r"Clan.*None", clan_line, re.IGNORECASE):
        debug_log(f"extract_clan_name: clan_line contains 'None'")
        return None

    # Extract after 'of' (handles emojis and text)
    match = re.search(r"of\s*(?:<a?:\w+:\d+>\s*)?([A-Za-z0-9 ]+)", clan_line)
    if match:
        debug_log(f"extract_clan_name: regex match found '{match.group(1).strip()}'")
        return match.group(1).strip()

    # Fallback: try to get last word(s) after colon
    parts = clan_line.split(":")
    debug_log(f"extract_clan_name: parts after split='{parts}'")
    if len(parts) > 1:
        possible_name = parts[-1].strip()
        debug_log(f"extract_clan_name: possible_name='{possible_name}'")
        if possible_name and possible_name.lower() != "none":
            return possible_name
    debug_log("extract_clan_name: no valid clan name found")
    return None


async def stats_command_handler(
    bot: discord.Client,
    message: discord.Message,
):
    """Checks for stats command and processes clan stats messages.
    Handles clan membership and faction updates.
    """

    debug_log(
        f"message.id={message.id}, author={message.author}, embeds={message.embeds}"
    )
    if not message.embeds:
        debug_log("message has no embeds")
        return

    embed = message.embeds[0]
    debug_log(
        f"embed.author={embed.author}, embed.author.name={getattr(embed.author, 'name', None)}, embed.description={embed.description}"
    )
    if not embed.author or not embed.author.name or not embed.description:
        debug_log("embed missing author/name/description")
        return

    username = embed.author.name.split("'s ")[0]
    embed_description = embed.description
    debug_log(
        f"username='{username}', embed_description='{embed_description}'"
    )

    clan_name = extract_clan_name(embed_description)
    pretty_log("info", f"Extracted clan name '{clan_name}'")
    debug_log(f"clan_name='{clan_name}'")
    # Get member info
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    user_id = fetch_vna_member_id_by_username_or_pokemeow_name(username)
    debug_log(
        f"fetched user_id='{user_id}' for username='{username}'"
    )
    debug_log(f"{username} is in vna_members_cache: {user_id in vna_members_cache}")
    if not user_id:
        debug_log("user_id not found , Resortin to fallback method of extracting user_id from command")
        # Fallback: try to get user ID from replied message content
        replied_message = getattr(message.reference, "resolved", None)
        if replied_message:
            replied_message_content = getattr(replied_message, "content", "") or ""
            user_id = extract_user_id_from_command(replied_message_content)
            debug_log(
                f"extracted user_id='{user_id}' from replied message content='{replied_message_content}'"
            )
            if not user_id:
                debug_log("user_id could not be extracted from command, aborting stats handler")
                return


    # Check if user_id in members cache
    member_info = vna_members_cache.get(user_id)
    debug_log(
        f"member_info='{member_info}' for user_id='{user_id}'"
    )
    if not member_info:
        debug_log("member_info not found in cache")
        return

    # Get member
    guild = bot.get_guild(VNA_SERVER_ID)
    debug_log(f"fetched guild='{guild}'")
    member = guild.get_member(user_id)
    debug_log(
        f"fetched member='{member}' for user_id='{user_id}'"
    )
    user = None
    if not member:
        debug_log(
            f"member not found, fetching user for user_id='{user_id}'"
        )
        user = await bot.fetch_user(user_id)
    else:
        user = member
    # Check if their clan is still VN Allstar
    clan_name = extract_clan_name(embed_description)
    pretty_log("info", f"Extracted clan name '{clan_name}' for member '{user.name}'")
    debug_log(f"clan_name='{clan_name}' for user='{user.name}'")
    if member_info and clan_name != "VN Allstar":
        debug_log(
            f"member '{user.name}' is not in VN Allstar clan, removing from DB and roles"
        )
        # Remove from database
        debug_log(
            f"calling db_cleanup_handler for user_id='{user_id}'"
        )
        await db_cleanup_handler(bot=bot, user_id=user_id)
        pretty_log(
            message=(
                f"Removed user_id '{user_id}' from the database "
                f"as they left the VN Allstars clan."
            ),
            tag="info",
            label="Stats Listener",
        )
        # check if member has vna member role
        if member:
            vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
            debug_log(
                f"vna_member_role='{vna_member_role}' for member='{member.display_name}'"
            )
            if vna_member_role in member.roles:
                debug_log(
                    f"removing VNA Member role from '{member.display_name}'"
                )
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
                debug_log(
                    f"finished removing VNA Member role from '{member.display_name}'"
                )
                return
            elif vna_member_role not in member.roles:
                debug_log(
                    f"vna_member_role not in roles for '{member.display_name}', removing from DB"
                )
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
                debug_log(
                    f"finished removing '{member.display_name}' from DB"
                )
                return

    # Update faction
    member_faction = member_info.get("faction")
    debug_log(
        f"member_faction='{member_faction}' for user_id='{user_id}'"
    )
    faction_emoji = extract_faction_emoji(embed_description)
    debug_log(f"faction_emoji='{faction_emoji}'")
    if faction_emoji:
        faction = None
        faction = get_faction_by_emoji(faction_emoji)
        debug_log(
            f"faction='{faction}' from emoji='{faction_emoji}'"
        )
        if faction and member_faction != faction:
            debug_log(
                f"updating faction for member from '{member_faction}' to '{faction}'"
            )
            if member is None:
                pretty_log(
                    message=(
                        f"[ERROR] Tried to update faction but member is None for user_id '{user_id}'. Cannot update faction.",
                    ),
                    tag="info",
                    label="Stats Listener",
                )
                debug_log(
                    f"member is None, cannot update faction for user_id='{user_id}'"
                )
                return
            await update_member_faction(bot, member, faction)
            pretty_log(
                message=(
                    f"Updated faction for member '{member.display_name}' "
                    f"from '{member_faction}' to '{faction}'."
                ),
                tag="info",
                label="Stats Listener",
            )
            debug_log(
                f"finished updating faction for member '{member.display_name}'"
            )
