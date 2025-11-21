import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.point_db_func import (
    add_points,
    update_points,
    fetch_all_points,
    fetch_user_points,
    get_first_place,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Points Add Command Function
# 🍭──────────────────────────────
async def points_add_func(
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
            "Only staff members can add points.", ephemeral=True
        )
        return

    # Validate amount
    if amount <= 0:
        await interaction.response.send_message(
            "Amount must be a positive integer.", ephemeral=True
        )
        return

    # Get current points
    current_points_info = await fetch_user_points(bot, member)
    current_points = current_points_info["amount"] if current_points_info else 0
    new_amount = current_points + amount
    # Add points to the member
    await update_points(bot, member, new_amount)

    # Check if the member is now in first place
    new_first_place = False
    first_place_user = await get_first_place(bot)
    if first_place_user and first_place_user["user_id"] == member.id:
        crown_emoji = "👑"
        new_first_place = True
    else:
        crown_emoji = ""

    # Create and send the embed message
    embed = discord.Embed(
        title=f"{crown_emoji} {member.display_name}'s Points Updated",
        description=f"**Added Points:** {amount}\n**Total Points:** {new_amount}",
        color=discord.Color.green(),
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=False)

    # Log the action in the log channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        if new_first_place:
            crown_emoji = "👑"
            pretty_log(
                "info", f"🏆 {member} has taken the lead with {new_amount} points!"
            )
        else:
            crown_emoji = ""
        embed = discord.Embed(
            title=f"{crown_emoji} Points Added",
            description=f"**Member:** {member.mention}\n**Added By:** {user.mention}\n**Points Added:** {amount}\n**Total Points:** {new_amount}",
            color=discord.Color.blue(),
        )
        await log_channel.send(embed=embed)
        pretty_log(
            "info",
            f"📝 {user} added {amount} points to {member}. Total points: {new_amount}",
        )
