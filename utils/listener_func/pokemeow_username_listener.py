import re

import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_user_name, update_member_pokemeow_name
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.logs.pretty_log import pretty_log

async def update_pokemeow_username_by_command(
        bot: discord.Client,
        message: discord.Message,
):
    member = await get_pokemeow_reply_member(message=message)
    if not member:
        return

    member_id = member.id
    # Check if member is in cache
    member_info = vna_members_cache.get(member_id)
    if not member_info:
        return

    old_pokemeow_name = member_info.get("pokemeow_name", "")
    new_pokemeow_name = member.name

    if old_pokemeow_name != new_pokemeow_name:
        try:
            await update_member_pokemeow_name(bot, member, new_pokemeow_name)
            pretty_log(
                message=(
                    f"Updated Pokemeow username for member '{member.display_name}' "
                    f"from '{old_pokemeow_name}' to '{new_pokemeow_name}'."
                ),
                tag="info",
                label=";Pokemeow Username Update",
            )
        except Exception as e:
            pretty_log(
                message=(
                    f"Failed to update Pokemeow username for member '{member.display_name}'. "
                    f"Error: {e}"
                ),
                tag="error",
                label=";Pokemeow Username Update",
            )