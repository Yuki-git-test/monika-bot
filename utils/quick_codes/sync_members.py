import asyncio
import discord

from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import fetch_all_members
from utils.logs.pretty_log import pretty_log
from constants.vn_allstars_constants import VNA_SERVER_ID, VN_ALLSTARS_ROLES
from constants.aesthetic import Emojis

async def sync_members_func(bot:discord.Client, message: discord.Message):
    """ Removes vna member role from members not in vna_members_cache and adds role to those who are missing it."""

    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log("error", "Guild not found for VNA_SERVER_ID")
        return

    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if not vna_member_role:
        pretty_log("error", "VNA Member role not found")
        return

    # Send processing message
    processing_msg = await message.reply(f"{Emojis.orange_loading} Syncing VNA Member roles, please wait...")

    # Fetch all guild members
    guild_members = [member async for member in guild.fetch_members()]
    members_with_role = [member for member in guild_members if vna_member_role in member.roles]
    # Sync roles
    to_add = []
    to_remove = []
    for member in guild_members:
        in_cache = member.id in vna_members_cache
        has_role = vna_member_role in member.roles

        if in_cache and not has_role:
            to_add.append(member)
        elif not in_cache and has_role:
            to_remove.append(member)

    # Add role to members missing it
    for member in to_add:
        try:
            await member.add_roles(vna_member_role, reason="Syncing VNA Member role - added")
            pretty_log("info", f"Added VNA Member role to {member.display_name} ({member.id})")
            await asyncio.sleep(0.5)  # Add a 0.5 second delay

        except Exception as e:
            pretty_log("error", f"Failed to add VNA Member role to {member.display_name} ({member.id}): {e}")
    # Remove role from members who shouldn't have it
    for member in to_remove:
        try:
            await member.remove_roles(vna_member_role, reason="Syncing VNA Member role - removed")
            pretty_log("info", f"Removed VNA Member role from {member.display_name} ({member.id})")
            await asyncio.sleep(0.5)  # Add a 0.5 second delay
        except Exception as e:
            pretty_log("error", f"Failed to remove VNA Member role from {member.display_name} ({member.id}): {e}")

    # Summary embed
    embed = discord.Embed(
        title="VNA Member Role Sync Summary",
        color=discord.Color.green(),
    )
    added_str = "\n".join([f"{member.display_name} ({member.id})" for member in to_add]) or "None"
    removed_str = "\n".join([f"{member.display_name} ({member.id})" for member in to_remove]) or "None"
    embed.add_field(name="Roles Added To", value=added_str, inline=False)
    embed.add_field(name="Roles Removed From", value=removed_str, inline=False)

    # Edit processing message with summary
    await processing_msg.edit(content=f"{Emojis.orange_check} VNA Member role sync complete!", embed=embed)
