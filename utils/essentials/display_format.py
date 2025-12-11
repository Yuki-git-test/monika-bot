import discord

from constants.aesthetic import *

PERKS_EMOJI_MAP = {
    "bronze": Emojis.bronze,
    "silver": Emojis.silver,
    "gold": Emojis.gold,
    "diamond": Emojis.diamond,
    "amethyst": Emojis.amethyst,
    "onyx": Emojis.onyx,
}

FACTION_EMOJI_MAP = {
    "aqua": Emojis.aqua,
    "flare": Emojis.flare,
    "galactic": Emojis.galactic,
    "magma": Emojis.magma,
    "rocket": Emojis.rocket,
    "skull": Emojis.skull,
    "yell": Emojis.yell,
    "plasma": Emojis.plasma,
}

# 🌸────────────────────────────────────────────
#       🎐 Format Display Perks
# 🌸────────────────────────────────────────────
def format_display_perks(perks: str) -> str:
    """Format the display of member perks."""
    if perks == "No Perks" or perks is None:
        return "N/A"
    perks = perks.lower()
    perks_emoji = PERKS_EMOJI_MAP.get(perks, "")
    return f"{perks_emoji} {perks.title()}"


# 🌸────────────────────────────────────────────
#       🎐 Format Display Faction
# 🌸────────────────────────────────────────────
def format_display_faction(faction: str) -> str:
    """Format the display of member faction."""
    if faction == "No Faction" or faction is None:
        return "N/A"
    faction = faction.lower()
    faction_emoji = FACTION_EMOJI_MAP.get(faction, "")
    return f"{faction_emoji} {faction.title()}"