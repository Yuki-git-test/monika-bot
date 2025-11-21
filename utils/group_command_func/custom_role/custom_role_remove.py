from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.custom_roles_db_func import fetch_custom_role_id, remove_role_by_role_id
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Slash Command: Remove Custom Role
# 🍭──────────────────────────────
async def custom_role_remove_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
):
    """Remove a member's custom role."""
    guild = interaction.guild

    # Check if user is a staff member
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
    if staff_role not in user.roles:
        await interaction.response.send_message(
            "Only staff members can remove custom roles.", ephemeral=True
        )
        return
    # Check if member has a custom role
    custom_role_id = await fetch_custom_role_id(bot, member)
    if not custom_role_id:
        await interaction.response.send_message(
            f"{member.display_name} does not have a custom role.", ephemeral=True
        )
        return

    custom_role = guild.get_role(custom_role_id)
    if custom_role:
        try:
            await custom_role.delete(
                reason=f"Custom role removed by {user.display_name}"
            )
            pretty_log(
                "success",
                f"Deleted role {custom_role.name} for user {member.display_name}.",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to delete role {custom_role.name} for user {member.display_name}: {e}",
            )
            await interaction.response.send_message(
                f"Failed to delete the role. Please check my permissions.",
                ephemeral=True,
            )
            return
    else:
        pretty_log(
            "warning",
            f"Role ID {custom_role_id} for user {member.display_name} does not exist in guild.",
        )

    # Remove the role from the database
    await remove_role_by_role_id(bot, custom_role_id)
    pretty_log(
        "success",
        f"Removed role ID {custom_role_id} from database for user {member.display_name}.",
    )

    await interaction.response.send_message(
        f"Successfully removed {member.display_name}'s custom role.", ephemeral=True
    )

    # Log the action in the log channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="Custom Role Removed",
            description=(
                f"**Member:** {member.mention} (`{member.id}`)\n"
                f"**Removed by:** {user.mention} (`{user.id}`)\n"
                f"**Role ID:** `{custom_role_id}`"
            ),
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        await log_channel.send(embed=embed)
