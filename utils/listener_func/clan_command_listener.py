import re
from datetime import datetime

import discord

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

from .clan_members_listener import move_to_members_category


async def clan_command_listener(bot: discord.Client, message: discord.Message):
    """
    Listens for clan command messages and processes them accordingly.
    """

    if not message.embeds:
        return
    embed = message.embeds[0]
    embed_description = embed.description or ""

    member = await get_pokemeow_reply_member(message)
    if member is None:
        pretty_log(
            "info",
            "No member found in the replied message.",
            label="clan_command_listener",
        )
        return

    vna_guild = bot.get_guild(VNA_SERVER_ID)
    if vna_guild is None:
        pretty_log(
            "error",
            f"VNA guild with ID {VNA_SERVER_ID} not found.",
            label="clan_command_listener",
        )
        return
    # Check if member is a VNA Member
    vna_member_role = vna_guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_member_role not in member.roles:
        pretty_log(
            "info",
            f"Member {member.name} does not have the VNA Member role.",
            label="clan_command_listener",
        )
        return

    # Get info
    user_id = member.id
    user_name = member.name
    member_info = vna_members_cache.get(user_id)
    if not member_info:
        pretty_log(
            "info",
            f"No member info found in cache for user ID {user_id}.",
            label="clan_command_listener",
        )
        return
    member_channel_id = member_info.get("channel_id")
    channel = bot.get_channel(member_channel_id)
    if channel is None:
        pretty_log(
            "info",
            f"Channel with ID {member_channel_id} not found for member {member.name}.",
            label="clan_command_listener",
        )
        return

    catches_match = re.search(r"<:dexcaught:\d+>\s*([\d,]+)", embed_description)
    if not catches_match:
        pretty_log(
            "info",
            f"No catches info found in embed description for member {member.name}.",
            label="clan_command_listener",
        )
        return

    catches = int(catches_match.group(1).replace(",", "")) if catches_match else 0
    pretty_log(
        "info",
        f"Member {member.name} has {catches} catches.",
        label="clan_command_listener",
    )
    # Move channel to appropriate category based on catches
    context = None
    if catches >= 100000:
        context = "Pro Members"
    elif 50000 <= catches < 100000:
        context = "Clan Members 1"
    elif catches < 50000:
        context = "Clan Members 2"
    if context:
        await move_to_members_category(bot, member, channel, context=context)

    pretty_log(
        "info",
        "Clan command listener processing completed.",
        label="clan_command_listener",
    )
