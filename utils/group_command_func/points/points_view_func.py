import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.point_db_func import fetch_all_points, fetch_user_points, get_first_place
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Points View Command Function
# 🍭──────────────────────────────
async def points_view_func(
    bot: commands.Bot, interaction: discord.Interaction, member: discord.Member = None
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Check if member field has a value
    if member is not None:
        # Check if staff role is in user's roles
        if staff_role not in user.roles:
            await interaction.response.send_message(
                "Only staff members can view other members' points.", ephemeral=True
            )
            return
        target_member = member
        target_member_points_info = await fetch_user_points(bot, target_member)
        if not target_member_points_info:
            await interaction.response.send_message(
                f"{target_member.display_name} has no points record.", ephemeral=True
            )
            return
        target_member_points = target_member_points_info["amount"]
        first_place_user = await get_first_place(bot)
        if first_place_user and first_place_user["user_id"] == target_member.id:
            crown_emoji = "👑"
        else:
            crown_emoji = ""
        embed = discord.Embed(
            title=f"{crown_emoji} {target_member.display_name}'s Points",
            description=f"**Points:** {target_member_points}",
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=target_member.display_name, icon_url=target_member.display_avatar.url
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)
        return

    # If no member specified, show own points
    target_member = user
    target_member_points_info = await fetch_user_points(bot, target_member)
    if not target_member_points_info:
        await interaction.response.send_message(
            "You have no points record.", ephemeral=True
        )
        return
    target_member_points = target_member_points_info["amount"]
    first_place_user = await get_first_place(bot)
    if first_place_user and first_place_user["user_id"] == target_member.id:
        crown_emoji = "👑"
    else:
        crown_emoji = ""
    embed = discord.Embed(
        title=f"{crown_emoji} Your Points",
        description=f"**Points:** {target_member_points}",
        color=discord.Color.blue(),
    )
    embed.set_author(
        name=target_member.display_name, icon_url=target_member.display_avatar.url
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)
