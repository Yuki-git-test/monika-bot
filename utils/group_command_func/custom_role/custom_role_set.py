from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.custom_roles_db_func import (
    fetch_custom_role_id,
    get_role_by_id,
    remove_role,
    remove_role_by_role_id,
    update_gradient_role,
    upsert_role,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Slash Command: Set Custom Role
# 🍭──────────────────────────────
async def custom_role_set_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role,
):
    """Set a member's custom role to the specified role."""
    guild = interaction.guild

    # Check if user is a staff member
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
    if staff_role not in user.roles:
        await interaction.response.send_message(
            "Only staff members can set custom roles.", ephemeral=True
        )
        return
    # Check if member has a custom role
    custom_role_id = await fetch_custom_role_id(bot, member)
    if custom_role_id:
        custom_role = guild.get_role(custom_role_id)
        if custom_role_id and custom_role:
            await interaction.response.send_message(
                f"{member.display_name} already has a custom role: {custom_role.mention}.",
                ephemeral=True,
            )
            return
        if custom_role_id and not custom_role:
            # Delete the old role from the database
            await remove_role(bot, member)
            pretty_log(
                "success",
                f"Removed non-existent role from database for user {member.display_name}.",
            )

    # Check if the inputted role already belongs to another user
    user_id_with_role = await get_role_by_id(bot, role.id)
    if user_id_with_role:
        user_with_role = guild.get_member(user_id_with_role["user_id"])
        if user_with_role:
            await interaction.response.send_message(
                f"The role {role.name} is already assigned to another {user_with_role.mention}.",
                ephemeral=True,
            )
            return
        else:
            # The role is in the database but the user is not found in the guild
            await remove_role_by_role_id(bot, role_id=role.id)
            # Log the cleanup action
            pretty_log(
                "success",
                f"Removed role {role.name} from database as it was assigned to a non-existent user.",
            )
    # Assign the role to the member
    try:
        await member.add_roles(role, reason="Custom role assigned by staff.")
        pretty_log("success", f"Assigned role {role.name} to {member.display_name}.")
        await upsert_role(bot, member, role.id)
        await interaction.response.send_message(
            f"Successfully assigned the role {role.mention} to {member.mention}.",
            ephemeral=False,
        )

        # Send a log embed to your server log channel
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Custom Role Assigned",
                description=f"{user.mention} has assigned the role {role.mention} to {member.mention}.",
                color=0x00FF00,  # Green
                timestamp=datetime.utcnow(),
            )
            log_embed.add_field(name="Staff Member", value=user.mention, inline=True)
            log_embed.add_field(name="Member", value=member.mention, inline=True)
            log_embed.add_field(name="Role", value=role.mention, inline=True)
            await log_channel.send(embed=log_embed)
    except discord.Forbidden:
        await interaction.response.send_message(
            "I don't have permission to assign that role.", ephemeral=True
        )
        return
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to assign role due to an error: {e}", ephemeral=True
        )
        return
