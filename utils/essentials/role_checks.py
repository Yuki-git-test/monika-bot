import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.logs.pretty_log import pretty_log

# 🍭──────────────────────────────
#   🎀 Role Checks Utility
# 🍭──────────────────────────────

# ╭───────────────────────────────╮
#   🌊 Check if User is Staff Member
# ╰───────────────────────────────╯
async def is_staff_member(interaction: discord.Interaction) -> bool:
    """Check if the user is a staff member."""
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
    if staff_role in user.roles:
        return True
    return False