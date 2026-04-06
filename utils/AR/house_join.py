import random

import discord

from constants.aesthetic import Emojis
from constants.vn_allstars_constants import (
    KHY_USER_ID,
    MONIKA_EMBED_COLOR,
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.vna_members_cache import (
    get_house_role_id_by_user_id,
    get_members_from_house_role_id,
)
from utils.db.vna_members_db_func import update_house_role_id
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

processing_house_join = False
MEWTWO_USER_ID_ONE = 902135337353109554
MEWTWO_USER_ID_TWO = 1423566874435915776
LIMIT_PER_HOUSE = 6
HOUSE_ROLE_LIST = [
    VN_ALLSTARS_ROLES.world_government,
    VN_ALLSTARS_ROLES.heavenly_demon_sect,
    VN_ALLSTARS_ROLES.gojo_clan,
    VN_ALLSTARS_ROLES.fatty_house_racoon_cult,
]
HOUSE_MAP = {
    VN_ALLSTARS_ROLES.world_government: {
        "name": "World Government",
        "messages": [
            "Hmm… discipline, structure, a mind that seeks order in disorder… You understand what it means to lead and to control. You belong with the World Government!",
            "I see calculation… patience… a strategist who values stability above all. Power maintained, not wasted—yes… the World Government awaits you.",
            "Rules are not chains to you, but tools. Authority suits you far too well… You will thrive within the World Government!",
        ],
    },
    VN_ALLSTARS_ROLES.gojo_clan: {
        "name": "Gojo Clan",
        "messages": [
            "Oh? Effortless brilliance… talent that bends the world itself. You walk a path others can’t even see. Yes… the Gojo Clan is where you belong.",
            "Confidence, skill, and just a hint of arrogance… you already know you’re different. Perhaps even… the honored one. The Gojo Clan awaits you!",
            "Interesting… you don’t chase victory, it comes to you. A natural prodigy… There’s no doubt—the Gojo Clan!",
        ],
    },
    VN_ALLSTARS_ROLES.fatty_house_racoon_cult: {
        "name": "Fatty House Racoon Cult",
        "messages": [
            "Wait… what is this chaos? No plan, no structure… and yet somehow, it works?! Hah! You belong with the Fatty Raccoon Cult!",
            "Mischief, unpredictability, absolute nonsense… and strangely effective. You are either a genius or a disaster—perhaps both. The Fatty Raccoon Cult welcomes you!",
            "You follow no logic, no rules… only vibes. And yet fate seems to favor you. Hehehe… go on, join the Fatty Raccoon Cult!",
        ],
    },
    VN_ALLSTARS_ROLES.heavenly_demon_sect: {
        "name": "Heavenly Demon Sect",
        "messages": [
            "Ah… such ambition. You burn with the desire to rise above all others. Rules mean nothing to you… Only power matters. The Heavenly Demon Sect calls your name!",
            "Ruthless… fearless… and unwilling to bow. You would rather conquer than follow. Yes… you belong with the Heavenly Demon Sect!",
            "I sense it clearly—an emperor in the making. You don’t seek permission… you take what is yours. Go now, to the Heavenly Demon Sect!",
        ],
    },
}


async def join_house(bot: discord.Client, message: discord.Message):
    global processing_house_join
    member = message.author
    member_id = member.id
    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log("error", f"Guild with ID {VNA_SERVER_ID} not found.")
        return

    # Check if user has vna role except for khy
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_member_role not in member.roles and member_id != KHY_USER_ID:
        return

    # Check if user is already in a house
    current_house_role_id = get_house_role_id_by_user_id(member_id)
    if current_house_role_id:
        current_house_name = HOUSE_MAP.get(current_house_role_id, {}).get(
            "name", "Unknown House"
        )
        await message.channel.send(
            f"{Emojis.error} You are already in **{current_house_name}**! You cannot join another house."
        )
        return

    if processing_house_join:
        pretty_log(
            "info", f"Processing house join for user {member_id} ({member.name})..."
        )
        await message.reply(
            "Currently processing a house join request. Please try again in a few seconds."
        )
        return
    processing_house_join = True

    # Always start with all houses available
    # Only include houses that are not full
    available_houses = [
        house
        for house in HOUSE_ROLE_LIST
        if len(get_members_from_house_role_id(house)) < LIMIT_PER_HOUSE
    ]

    # Check if user id is one of the mewtwo ids, if yes dont assign them in the same house
    if member_id in [MEWTWO_USER_ID_ONE, MEWTWO_USER_ID_TWO]:
        # Check if the other mewtwo is already in a house
        other_mewtwo_id = (
            MEWTWO_USER_ID_TWO
            if member_id == MEWTWO_USER_ID_ONE
            else MEWTWO_USER_ID_ONE
        )
        other_mewtwo_house_role_id = get_house_role_id_by_user_id(other_mewtwo_id)
        # if the other mewtwo is in a house, remove that house from the options for the current mewtwo
        if other_mewtwo_house_role_id:
            available_houses = [
                house
                for house in available_houses
                if house != other_mewtwo_house_role_id
            ]

    if not available_houses:
        await message.channel.send(
            f"{Emojis.error} All houses are currently full. Please try again later."
        )
        processing_house_join = False
        return

    # Choose a random house for the user from available (not full) houses
    chosen_house_role_id = random.choice(available_houses)

    # Assign the house role to the user
    house_role = guild.get_role(chosen_house_role_id)

    if not house_role:
        pretty_log("error", f"House role with ID {chosen_house_role_id} not found.")
        processing_house_join = False
        await message.reply(
            "An error occurred while assigning you to a house. Please contact an admin."
        )
        return
    try:
        team_war_role = guild.get_role(VN_ALLSTARS_ROLES.team_war)
        await member.add_roles(house_role, reason="Joined a house")
        if team_war_role and team_war_role not in member.roles:
            await member.add_roles(
                team_war_role, reason="Joined a house - team war role"
            )

        await update_house_role_id(
            bot=bot,
            user_id=member_id,
            house_role_id=chosen_house_role_id,
            house_name=HOUSE_MAP[chosen_house_role_id]["name"],
        )

        pretty_log(
            "info",
            f"Assigned house role {house_role.name} to user {member_id} ({member.name}).",
        )
        welcome_message = random.choice(HOUSE_MAP[house_role.id]["messages"])
        await message.reply(f"{welcome_message}")
        processing_house_join = False
    except Exception as e:
        pretty_log(
            "error",
            f"Error assigning house role to user {member_id} ({member.name}): {e}",
        )
        await message.reply(
            "An error occurred while assigning you to a house. Please contact an admin."
        )
        processing_house_join = False
