import re
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import fetch_all_members, upsert_member
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log
from utils.visuals.colors import get_random_monika_color


async def list_vna_members_func(
    bot: commands.Bot, interaction: discord.Interaction, message_link: str
):
    """
    List all vna_members in the server.
    """
    guild = interaction.guild

    if guild.id != VNA_SERVER_ID:
        await interaction.response.send_message(
            "This command can only be used in the VNA server.", ephemeral=True
        )
        return

    # Check if user is staff
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return

    # Intialize loader
    loader = await pretty_defer(
        interaction=interaction, content="Listing vna members...", ephemeral=False
    )

    # Fetch message object from link
    # Parse message link
    try:
        parts = message_link.strip().split("/")
        guild_id = int(parts[4])
        channel_id = int(parts[5])
        message_id = int(parts[6])
        pretty_log(
            "info",
            f"Parsed message link: guild={guild_id}, channel={channel_id}, message={message_id}",
        )
    except (IndexError, ValueError):
        await loader.error("Invalid message link format.")
        return

    # Fetch the message
    try:
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        pretty_log("info", f"Fetched message: {message.id} in channel: {channel.id}")

    except discord.NotFound:
        await loader.error("Message not found. Please check the link and try again.")
        return

    except discord.Forbidden:
        await loader.error("I do not have permission to access the specified message.")
        return

    except Exception as e:
        pretty_log("error", f"Error fetching message: {e}")
        await loader.error(
            "Failed to fetch the message. Please check the link and try again."
        )
        return

    embed = message.embeds[0] if message.embeds else None
    if not embed:
        await loader.error("The specified message does not contain an embed.")
        return
    description = embed.description or ""
    first_field = embed.fields[0] if embed.fields else None
    if not first_field:
        await loader.error("The specified embed does not contain any fields.")
        return
    first_field_value = first_field.value
    # Extract user ids from first field value
    members = []
    description_lines = description.split("\n")
    for line in first_field_value.split("\n"):
        match = re.search(r"<@!?(\d+)>", line)
        if match:
            user_id = int(match.group(1))
            # Check if its in cache first
            member_info = vna_members_cache.get(user_id)
            if member_info:
                # skip
                continue

            # Fetch member object then upsert to DB
            member = guild.get_member(user_id)
            if member:
                member_id = member.id
                try:
                    await upsert_member(
                        bot,
                        user=member,
                    )
                    members.append(member)
                    pretty_log(
                        "success",
                        f"Upserted vna_member {member.display_name} ({member.id}) into database.",
                    )
                    description_lines.append(
                        f"✅ {member.mention} - {member.display_name}"
                    )
                except Exception as e:
                    pretty_log(
                        "error",
                        f"Error upserting vna_member {member.display_name} ({member.id}): {e}",
                    )
                    continue

    # Build confirmation embed after processing all members
    embed = discord.Embed(
        title="✅ VNA Members Listed!",
        description=f"Listed {len(members)} vna_members into the database.",
        color=get_random_monika_color(),
        timestamp=datetime.now(),
    )
    embed.add_field(
        name="Members Processed",
        value="\n".join(description_lines),
        inline=False,
    )
    await loader.success(embed=embed, content="")
