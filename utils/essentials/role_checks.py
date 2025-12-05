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
    dot_role = guild.get_role(VN_ALLSTARS_ROLES.dot_role)
    if staff_role in user.roles or dot_role in user.roles:
        return True
    return False

# ╭───────────────────────────────╮
#   🌊 Check if User is Clan Member
# ╰───────────────────────────────╯
async def is_clan_member(interaction: discord.Interaction) -> bool:
    """Check if the user is a clan member."""
    guild = interaction.guild
    user = interaction.user
    clan_member_role = guild.get_role(VN_ALLSTARS_ROLES.clan_member)
    if clan_member_role in user.roles:
        return True
    return False