from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.public_trophy_db import *
from utils.db.trophy import upsert_leaderboard_msg_id
from utils.logs.pretty_log import pretty_log


LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log

COLOR = MONIKA_EMBED_COLOR


async def filter_members_public(
    bot: commands.Bot, guild: discord.Guild, member_trophies
):
    """Filter out members who are not eligible for the trophy leaderboard."""
    filtered_trophies = []
    for trophy_info in member_trophies:
        user_id = trophy_info["user_id"]
        user = guild.get_member(user_id)
        if user:
            # Check if trophy is zero
            if trophy_info["amount"] == 0:
                # Remove from db if trophy is zero
                await remove_public_trophy_info_user(bot, user_id)
                pretty_log(
                    tag="info",
                    message=f"Removed public trophy entry for user ID {user_id} as their trophy count is zero.",
                    label="Trophy Leaderboard Embed",
                )
                continue

            filtered_trophies.append(trophy_info)
        else:
            # Remove trophy entry for users no longer in the guild
            await remove_public_trophy_info_user(bot, user_id)
            pretty_log(
                tag="info",
                message=f"Removed public trophy info for user ID {user_id} not found in guild.",
                label="Trophy Leaderboard Embed",
            )
    return filtered_trophies


async def create_public_leaderboard_embed(
    bot: commands.Bot,
    guild: discord.Guild,
    command_user: discord.Member = None,
    context: str = None,
):
    """Create the trophy leaderboard embed."""
    all_trophies = await fetch_all_public_trophies(bot)
    embed = discord.Embed(
        title=f"🏆 {guild.name} Public Trophy Leaderboard",
        color=COLOR,
    )
    footer_text = "Updated Public Trophy Leaderboard at"
    if all_trophies:
        sorted_trophies = sorted(all_trophies, key=lambda x: x["amount"], reverse=True)
        pretty_log(
            tag="info",
            message="Creating trophy leaderboard embed with trophies data.",
            label="Trophy Leaderboard Embed",
        )
        # Filter out members who have left the guild
        sorted_trophies = await filter_members_public(bot, guild, sorted_trophies)
        first_place_user_id = None
        current_leaderboard_info = await fetch_current_public_leaderboard_info(bot)
        first_place_user_id = (
            current_leaderboard_info.get("first_place_id")
            if current_leaderboard_info
            else None
        )

        for index, trophy_info in enumerate(sorted_trophies[:25], start=1):
            user_id = trophy_info["user_id"]
            amount = trophy_info["amount"]
            user = guild.get_member(user_id)
            if user:
                field_name_str = f"{index}. {user.display_name}"
                if first_place_user_id and user_id == first_place_user_id:
                    field_name_str = f"👑 {field_name_str}"
                embed.add_field(
                    name=field_name_str,
                    value=f"> - 🏆 {amount}",
                    inline=False,
                )
        if command_user and context == "view leaderboard":
            user_place_info = await fetch_user_place_and_public_trophies(
                bot, command_user
            )
            if not user_place_info or user_place_info["amount"] == 0:
                embed.add_field(
                    name="\u200b",
                    value="You have no trophies yet.",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="\u200b",
                    value=f"You are currently in #{user_place_info['place']} with \U0001f3c6 {user_place_info['amount']}",
                    inline=False,
                )

    else:
        embed.description = "No trophies have been awarded yet."
        pretty_log(
            tag="info",
            message="No trophies found when creating leaderboard embed.",
            label="Trophy Leaderboard Embed",
        )

    embed.timestamp = datetime.now()
    embed.set_footer(
        text=footer_text,
        icon_url=guild.icon.url if guild.icon else None,
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    return embed


# 🍭──────────────────────────────
#   🎀 New First Place Announcement Function
# 🍭──────────────────────────────
async def new_public_first_place_announcement(
    bot: commands.Bot, guild: discord.Guild, member: discord.Member, trophy_amount: int
):
    """Announce new first place in the designated channel."""

    # Update in db first
    leaderboard_info = await fetch_current_public_leaderboard_info(bot)
    message_id = leaderboard_info["message_id"] if leaderboard_info else None

    await update_first_place_in_public_leaderboard(
        bot=bot,
        message_id=message_id,
        first_place_id=member.id,
        first_place_name=member.name,
        first_place_trophy=trophy_amount,
    )
    pretty_log(
        tag="info",
        message=f"Updating new first place: {member.display_name} with {trophy_amount} trophies.",
        label="First Place Announcement",
    )


# 🍭──────────────────────────────
#   🎀 trophies Update Leaderboard Command Function
# 🍭──────────────────────────────
async def trophy_update_public_leaderboard_func(
    bot: commands.Bot, guild: discord.Guild, user: discord.Member = None
):
    """Update the trophy leaderboard message in the designated channel."""
    leaderboard_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.leaderboard)
    if not leaderboard_channel:
        pretty_log(
            tag="error",
            message="Leaderboard channel not found.",
            label="Trophy Leaderboard Update",
        )
        return
    # Get message ID
    current_leader_board_info = await fetch_current_public_leaderboard_info(bot)
    message_id = (
        current_leader_board_info["message_id"] if current_leader_board_info else None
    )

    if not message_id:
        pretty_log(
            tag="info",
            message="No existing leaderboard message ID found. Creating a new message.",
            label="Trophy Leaderboard Update",
        )
        leaderboard_embed = await create_public_leaderboard_embed(bot, guild)
        leaderboard_message = await leaderboard_channel.send(embed=leaderboard_embed)
        await upsert_leaderboard_msg_id(
            bot, leaderboard_message.id, leaderboard_channel
        )
        pretty_log(
            tag="success",
            message="Created new trophy leaderboard message.",
            label="Trophy Leaderboard Update",
        )
        return
    elif message_id:
        pretty_log(
            tag="info",
            message="Existing leaderboard message ID found. Updating the message.",
            label="Trophy Leaderboard Update",
        )
        try:
            leaderboard_message = await leaderboard_channel.fetch_message(message_id)
            leaderboard_embed = await create_public_leaderboard_embed(bot, guild)
            await leaderboard_message.edit(embed=leaderboard_embed)
            pretty_log(
                tag="success",
                message="Updated trophy leaderboard message.",
                label="Trophy Leaderboard Update",
            )
        except discord.NotFound:
            pretty_log(
                tag="error",
                message="Leaderboard message not found. Creating a new one.",
                label="Trophy Leaderboard Update",
            )
            leaderboard_embed = await create_public_leaderboard_embed(bot, guild)
            leaderboard_message = await leaderboard_channel.send(
                embed=leaderboard_embed
            )
            await upsert_leaderboard_msg_id(
                bot, leaderboard_message.id, leaderboard_channel
            )
