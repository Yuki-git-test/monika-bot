import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
    KHY_USER_ID
)
from utils.logs.pretty_log import pretty_log
from utils.quick_codes.clan_info import post_clan_info
from utils.quick_codes.cleanup import clean_graveyard_channels_func
from utils.schedule.custom_role_checker import custom_role_checker
from .debug_role_move import debug_role_move
from  utils.listener_func.clan_members_listener import clan_members_command_listener

async def quick_codes_handler(bot, message: discord.Message):
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

    # ————————————————————————————————
    # 🐞 Debug Role Move Quick Code Handler
    # ————————————————————————————————
    if message.content.lower() == "!debug_role_move":
        await debug_role_move(message)
        return
    # ————————————————————————————————
    # 🛡️ Custom Role Checker Quick Code Handler
    # ————————————————————————————————
    if message.content.lower() == "!custom_role_check":
        await custom_role_checker(bot, message)
        return
    # ————————————————————————————————
    # 🏰 Clan Members Command Quick Code Handler
    # ————————————————————————————————
    if message.content.lower().startswith("!sort_channels") and message.author.id == KHY_USER_ID:
        pretty_log(
            "info",
            "Clan members command listener triggered via quick code.",
        )
        await clan_members_command_listener(bot, message, msg_context="reply")
        return
