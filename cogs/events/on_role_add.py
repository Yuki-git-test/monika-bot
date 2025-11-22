import discord
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VNA_SERVER_ID
from utils.functions.server_booster_handler import handle_server_booster_role_add
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Event: On Role Add
# 🍭──────────────────────────────
async def handle_role_add(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role,
):
    """Handle role addition events."""
    role_id = role.id

    # ————————————————————————————————
    # 🩵 VNA Server Role Add Logic
    # ————————————————————————————————
    if role_id == VN_ALLSTARS_ROLES.server_booster:
        # Handle server booster role addition
        pretty_log(
            message=f"Detected server booster role addition for member '{member.display_name}'.",
            tag="info",
            label="Role Add Event",
        )
        await handle_server_booster_role_add(bot, member)
