import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.point_db_func import (
    fetch_all_points,
    fetch_user_points,
    get_first_place,
    remove_points,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Points Remove Command Function
# 🍭──────────────────────────────
async def points_remove_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int,
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Check if staff role is in user's roles
    if staff_role not in user.roles:
        await interaction.response.send_message(
            "Only staff members can remove points.", ephemeral=True
        )
        return

    # Validate amount
    if amount <= 0:
        await interaction.response.send_message(
            "Amount must be a positive integer.", ephemeral=True
        )
        return

    # Fetch current points
    current_points_info = await fetch_user_points(bot, member)
    current_points = current_points_info["amount"] if current_points_info else 0

    if amount > current_points:
        await interaction.response.send_message(
            f"{member.display_name} only has {current_points} points.", ephemeral=True
        )
        return
    # Remove points from the member
    await remove_points(bot, member, amount)
