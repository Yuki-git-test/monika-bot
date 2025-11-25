import re

import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_faction, update_member_perks
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.logs.pretty_log import pretty_log


FACTION_LOGO_EMOJIS = {
    "aqua": "<:team_logo:1276285308794835139>",
    "magma": "<:team_logo:1276300583300759623>",
    "flare": "<:team_logo:1276340625725329491>",
    "rocket": "<:team_logo:1276285077701263432>",
    "plasma": "<:team_logo:1276335185499000915>",
    "galactic": "<:team_logo:1276325626055491705>",
    "skull": "<:team_logo:1276346100848132106>",
    "yell": "<:team_logo:1276346491975372871>",
}


def get_faction_by_emoji(emoji: str) -> str | None:
    """
    Given an emoji string, return the faction key if found, else None.
    """
    for faction, emj in FACTION_LOGO_EMOJIS.items():
        if emoji == emj:
            return faction
    return None


def extract_faction_emoji(description: str) -> str | None:
    """
    Extracts the emoji string next to '**Faction**:' in the embed description.
    Returns the emoji string if found, else None.
    """
    match = re.search(r"\*\*Faction\*\*:\s*(<a?:\w+:\d+>)", description)
    if match:
        return match.group(1)
    return None

async def extract_faction_from_faction_command(
        bot:discord.Client,
        message: discord.Message,
):
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    faction = None
    if not embed.author or not embed.author.name:
        return

    author_match = re.search(r"Team (\w+)", embed.author.name)
    if not author_match:
        return

    faction = author_match.group(1)
    faction = faction.lower()

    member = await get_pokemeow_reply_member(message)
    if not member:
        return

    member_id = member.id
    member_info = vna_members_cache.get(member_id)
    if not member_info:
        pretty_log(
            message=f"Member info not found in cache for member ID '{member_id}'.",
            tag="info",
            label="Faction Command Extraction",
        )
        return

    member_faction = member_info.get("faction")
    if member_faction != faction:
        await update_member_faction(bot, member, faction)
        pretty_log(
            message=(
                f"Updated faction for member '{member.display_name}' "
                f"from '{member_faction}' to '{faction}'."
            ),
            tag="info",
            label=";Faction Command Extraction",
        )

    # Get faction ball for future use
    ball_match = re.search(
        r"<:([a-zA-Z0-9_]+):\d+>\s+\*\*Today's target Pokemon are\*\*",
        embed.description,
    )
    if not ball_match:
        return
    daily_ball = ball_match.group(1)
