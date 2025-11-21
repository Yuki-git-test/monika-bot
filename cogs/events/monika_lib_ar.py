import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log
from utils.monika_library.battle_mons import (
    send_battle_mon_embed,
    send_battle_mon_embed_with_buttons,
)
from utils.monika_library.explore import send_main_explore_embed
from utils.monika_library.library import (
    send_battle_guide_commands_embed,
    send_beginner_guide_embed,
    send_coin_guide_embed,
    send_library_embed,
    send_research_guide_embed,
)
from utils.monika_library.monika_rouge import (
    send_monika_rogue_challenges_embed,
    send_monika_rouge_main_embed,
)
from utils.monika_library.wb import (
    get_regdex_key_by_value,
    send_wb_embed,
    send_wb_info_embed,
)

battle_triggers_no_buttons = [
    "!bmchomp",
    "!b 7034",
    "!bsha",
    "!b 802",
    "!bxern",
    "!b 716",
    "!bkyo",
    "!b 382",
    "!bgrd",
    "!b 383",
    "!bZC",
    "!b 7891",
    "!byve",
    "!b 717",
    "!bresh",
    "!b 643",
    "!bslak",
    "!b 289",
    "!bray",
    "!b 384",
    "!barc",
    "!b 493",
    "!bzek",
    "!b 644",
    "!bhoh",
    "!b 250",
    "!bcaly",
    "!b 7873",
]
battle_triggers_with_buttons = [
    "!bmmx",
    "!b 7109",
    "!bmewtwo",
    "!b 150",
    "!bmmy",
    "!b 7121",
    "!bmew",
    "!b 151",
    "!bned",
    "!b 7669",
    "!bneu",
    "!b 7693",
    "!bnem",
    "!b 7687",
    "!bkyu",
    "!bkyu",
    "!bkyub",
    "!bkyuw",
    "!b 646",
    "!b 7510",
    "!b 7513",
]

wb_ar_triggers = [
    "alc",
    "app",
    "fla",
    "but",
    "cop",
    "mel",
    "cor",
    "gri",
    "hat",
    "orb",
    "ven",
    "cen",
    "bla",
    "cha",
    "cin",
    "gar",
    "gen",
    "int",
    "kin",
    "lap",
    "mac",
    "meo",
    "ril",
    "san",
    "sno",
    "tox",
    "urs",
    "eev",
    "dur",
    "eet",
]
explore_ar_triggers = [
    "!exsg",
    "!exsu",
    "!exsf",
    "!exsw",
]


# 🐾────────────────────────────────────────────
#        🌸 Monika Library AR Event Handler
# 🐾────────────────────────────────────────────
async def monika_lib_ar_handler(message: discord.Message):
    content = message.content.lower() if message.content else None
    if not content:
        return

    if content == "!library" or content == "!help":
        await send_library_embed(message)

    elif content == "!begin":
        await send_beginner_guide_embed(message)

    elif content == "!coin" or content == "!coins":
        await send_coin_guide_embed(message)

    elif content == "!res":
        await send_research_guide_embed(message)

    elif content == "!battle" or content == "!b" or content == "!library battle":
        await send_battle_guide_commands_embed(message)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   ⚔️ Monika's Library Battle Mons ⚔️
    #   "Looking for strong battle mons? I've got you covered~"
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif content in battle_triggers_no_buttons:
        await send_battle_mon_embed(message)

    elif content in battle_triggers_with_buttons:
        await send_battle_mon_embed_with_buttons(message)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🩸 Monika Rouge 🩸
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif content == "!mr":
        await send_monika_rouge_main_embed(message)

    elif content == "!mrch" or content == "!chmr":
        await send_monika_rogue_challenges_embed(message)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🐲 Monika Library WB
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif content == "!wb" or content == "! wb" or content == "!world boss":
        await send_wb_info_embed(message)

    elif content[3:] in wb_ar_triggers:  # To match after the "!wb"
        await send_wb_embed(message)

    elif content.startswith("!7"):
        dex = content.strip("!")
        pokemon = None
        pokemon = get_regdex_key_by_value(dex)
        if pokemon:
            await send_wb_embed(message)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🌟 Monika Library Explore
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif content in explore_ar_triggers:
        await send_main_explore_embed(message)