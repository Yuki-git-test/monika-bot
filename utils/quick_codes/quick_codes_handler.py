import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log
from utils.quick_codes.clan_info import post_clan_info
from utils.quick_codes.cleanup import clean_graveyard_channels_func


async def quick_codes_handler(message: discord.Message):
    """Handles quick codes based on message content."""

    # ————————————————————————————————
    # 🧹 Cleanup Graveyard Channels Quick Code Handler
    # ————————————————————————————————
    if message.content.lower() == "!clean_graveyard":
        await clean_graveyard_channels_func(message)
        return

    # ————————————————————————————————
    # 🔄 Clan Info Quick Code Handler
    # ————————————————————————————————
    if message.content.lower() == "!post_info":
        await post_clan_info(message)
        return
