import re

import discord

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_faction, update_member_perks
from utils.logs.pretty_log import pretty_log
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member

from constants.aesthetic import *

BANNED_PHRASES = {"PokeMeow Clans — Perks Info", "PokeMeow Clans — Rank Info"}
RANK_PRIORITY = ["onyx", "amethyst", "diamond", "gold", "silver", "bronze"]
CLAN_EMOJI_MAP = {
    ":diamondclan:": "diamond",
    ":goldclan:": "gold",
    ":silverclan:": "silver",
    ":bronzeclan:": "bronze",
    ":amethystclan:": "amethyst",
    ":onyxclan:": "onyx",
}


# 🟣────────────────────────────────────────────
#       🎨 Extract Username from Embed Title
# 🟣────────────────────────────────────────────
def extract_username_from_title(title: str) -> str:
    """
    Extracts the username part from a title like:
    <:emoji:id>**_0rz_** -> _0rz_
    """
    # Remove custom emojis (<:name:id> or <a:name:id>)
    no_emoji = re.sub(r"<a?:\w+:\d+>", "", title)

    # Remove bold/italic markdown (** or __ or *)
    no_format = re.sub(r"[*]{1,2}|_{2}", "", no_emoji)

    # Final cleanup: strip spaces only
    return no_format.strip()


# 🍭──────────────────────────────
#   🎀 Update Member Perks Handler
# 🍭──────────────────────────────
async def extract_perks_from_perk_message(
    bot: discord.Client,
    message: discord.Message,
):
    """Extract perks from a ;perks command message and updates the member's perks in the database."""

    if not message.embeds:
        return

    embed = message.embeds[0]
    author_text = getattr(embed.author, "name", "") if embed.author else ""

    # Ignore messages with banned phrases
    if author_text in BANNED_PHRASES:
        return

    author_name = embed.author.name if embed.author else ""
    author_name = author_name.replace("'s perks", "")
    cleaned_name = re.sub(r"[^\w\d.]", "", author_name)

    # Get the member info by user name or pokemeow name
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    # Fetch member ID from cache
    member_id = fetch_vna_member_id_by_username_or_pokemeow_name(cleaned_name)
    if not member_id:
        pretty_log(
            message=f"Could not find member ID for username/pokemeow_name '{cleaned_name}'.",
            tag="info",
            label=";Perks Extraction",
        )
        return

    member_info = vna_members_cache.get(member_id)
    if not member_info:
        pretty_log(
            message=f"Member info not found in cache for member ID '{member_id}'.",
            tag="info",
            label=";Perks Extraction",
        )
        return

    # Extract perks from embed description
    description = embed.description or ""
    rank_found = None

    for rank in RANK_PRIORITY:
        for emoji, name in CLAN_EMOJI_MAP.items():
            if rank == name.lower() and emoji in description:
                rank_found = name
                break
        if rank_found:
            break

    if not rank_found:
        pretty_log(
            message=f"No clan rank found in embed description for member ID '{member_id}'.",
            tag="info",
            label=";Perks Extraction",
        )
        return

    # Update member perks in the database
    old_perks = member_info.get("perks", "")
    guild = message.guild
    member = guild.get_member(member_id)
    if member and old_perks != rank_found:
        try:
            await update_member_perks(bot, member, rank_found)
            pretty_log(
                message=(
                    f"Updated perks for member '{member.display_name}' "
                    f"from '{old_perks}' to '{rank_found}'."
                ),
                tag="info",
                label=";Perks Extraction",
            )
        except Exception as e:
            pretty_log(
                message=(
                    f"Failed to update perks for member '{member.display_name}'. "
                    f"Error: {e}"
                ),
                tag="error",
                label=";Perks Extraction",
            )


async def extract_perks_from_profile_message(
    bot: discord.Client,
    message: discord.Message,
):
    """Extract perks from ;profile command message and updates the member's perks in the database."""

    if not message.embeds:
        return

    embed = message.embeds[0]
    title = embed.title or ""
    guild = bot.get_guild(VNA_SERVER_ID)
    cleaned_name = extract_username_from_title(title)

    # Get the member info by user name or pokemeow name
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    member_id = fetch_vna_member_id_by_username_or_pokemeow_name(cleaned_name)
    if not member_id:
        pretty_log(
            message=f"Could not find member ID for username/pokemeow_name '{cleaned_name}'.",
            tag="info",
            label=";Profile Extraction",
        )
        return

    member_info = vna_members_cache.get(member_id)
    if not member_info:
        pretty_log(
            message=f"Member info not found in cache for member ID '{member_id}'.",
            tag="info",
            label=";Profile Extraction",
        )
        return

    member = guild.get_member(member_id)
    if not member:
        pretty_log(
            message=f"Member with ID '{member_id}' not found in guild.",
            tag="info",
            label=";Profile Extraction",
        )
        return

    # Extract perks from embed
    description = embed.description or ""
    rank_found = None

    for emoji, name in CLAN_EMOJI_MAP.items():
        if emoji in description:
            rank_found = name
            break

    if not rank_found:
        pretty_log(
            message=f"No clan rank found in embed description for member ID '{member_id}'.",
            tag="info",
            label=";Profile Extraction",
        )
        return

    # Update member perks in the database
    old_perks = member_info.get("perks", "")
    if old_perks != rank_found:
        try:
            await update_member_perks(bot, member, rank_found)
            pretty_log(
                message=(
                    f"Updated perks for member '{member.display_name}' "
                    f"from '{old_perks}' to '{rank_found}'."
                ),
                tag="info",
                label=";Profile Extraction",
            )
        except Exception as e:
            pretty_log(
                message=(
                    f"Failed to update perks for member '{member.display_name}'. "
                    f"Error: {e}"
                ),
                tag="error",
                label=";Profile Extraction",
            )

    # Extract faction
    member_faction = member_info.get("faction")
    from utils.listener_func.faction_listener import (
        FACTION_LOGO_EMOJIS,
        get_faction_by_emoji,
    )

    for faction, emoji in FACTION_LOGO_EMOJIS.items():
        if emoji in description:
            if member_faction != faction:
                await update_member_faction(bot, member, faction)
                pretty_log(
                    message=(
                        f"Updated faction for member '{member.display_name}' "
                        f"from '{member_faction}' to '{faction}'."
                    ),
                    tag="info",
                    label=";Profile Extraction",
                )
                break

async def update_perks_via_perks_purchase(
        bot: discord.Client,
        message: discord.Message,
):
    """Extracts perks from a perks purchase confirmation message and updates the member's perks in the database."""

    if not message.content:
        return

    member = await get_pokemeow_reply_member(message)
    if not member:
        return

    cleaned_name = member.display_name
    member_id = member.id
    member_info = vna_members_cache.get(member_id)
    if not member_info:
        pretty_log(
            message=f"Member info not found in cache for member ID '{member_id}'.",
            tag="info",
            label="Perks Purchase Extraction",
        )
        return

    # ✅ Regex pattern to extract the perk tier
    match = re.search(
        r"Successfully purchased the .*?\*\*(\w+)\*\* perks",
        message.content,
        re.IGNORECASE,
    )
    if match:
        rank_found = match.group(1)
        rank_found = rank_found.lower()

    else:
        return

    # Update member perks in the database
    old_perks = member_info.get("perks", "")
    if old_perks != rank_found:
        try:
            await update_member_perks(bot, member, rank_found)
            pretty_log(
                message=(
                    f"Updated perks for member '{member.display_name}' "
                    f"from '{old_perks}' to '{rank_found}'."
                ),
                tag="info",
                label="Perks Purchase Extraction",
            )
            replied_message = message.reference.resolved
            if replied_message:
                await replied_message.add_reaction(Emojis.orange_check)
        except Exception as e:
            pretty_log(
                message=(
                    f"Failed to update perks for member '{member.display_name}'. "
                    f"Error: {e}"
                ),
                tag="error",
                label="Perks Purchase Extraction",
            )
