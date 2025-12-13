from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
    KHY_USER_ID
)
from utils.db.custom_roles_db_func import (
    fetch_custom_role_id,
    remove_role,
    update_gradient_role,
    upsert_role,
)
from utils.logs.pretty_log import pretty_log
from utils.visuals.colors import get_random_monika_color

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log
REFERENCE_ROLE_ID = VN_ALLSTARS_ROLES.personal_roles_divider
TEST_CUSTOM_ROLE_ID = 1449136348228485293


async def debug_role_move(message: discord.Message):
    """Debug function to move a custom role to below the reference role."""
    if message.author.id != KHY_USER_ID:
        return  # Only allow Khy to use this debug command
    
    guild = message.guild
    role = guild.get_role(TEST_CUSTOM_ROLE_ID)
    reference_role = guild.get_role(REFERENCE_ROLE_ID)
    reply_msg = await message.reply(
        f"{Emojis.orange_loading} Starting role move debug..."
    )

    if not role:
        await reply_msg.edit(
            content=f"{Emojis.error} Role with ID {TEST_CUSTOM_ROLE_ID} not found in guild."
        )
        pretty_log(
            message=f"Role with ID {TEST_CUSTOM_ROLE_ID} not found in guild.",
            tag="error",
            label="Debug Role Move",
        )
        return

    if not reference_role:
        await reply_msg.edit(
            content=f"{Emojis.error} Reference role with ID {REFERENCE_ROLE_ID} not found in guild."
        )
        pretty_log(
            message=f"Reference role with ID {REFERENCE_ROLE_ID} not found in guild.",
            tag="error",
            label="Debug Role Move",
        )
        return

    try:
        await role.edit(
            position=reference_role.position - 1, reason="Debugging role move."
        )
        await reply_msg.edit(
            content=f"{Emojis.orange_check} Successfully moved role '{role.name}' below reference role '{reference_role.name}'."
        )
        pretty_log(
            message=f"Moved role '{role.name}' to below reference role '{reference_role.name}'.",
            tag="success",
            label="Debug Role Move",
        )
    except Exception as e:
        await reply_msg.edit(
            content=f"{Emojis.error} Failed to move role '{role.name}': {e}"
        )
        pretty_log(
            message=f"Failed to move role '{role.name}': {e}",
            tag="error",
            label="Debug Role Move",
        )
