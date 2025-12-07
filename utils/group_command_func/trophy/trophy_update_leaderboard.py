from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.trophy import (
    fetch_all_trophies,
    fetch_current_leaderboard_info,
    fetch_leaderboard_message_id,
    fetch_user_place_and_trophies,
    get_first_place,
    update_first_place_in_db,
    upsert_leaderboard_msg_id,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


async def create_leaderboard_embed(
    bot: commands.Bot, guild: discord.Guild, command_user: discord.Member = None, context: str = None
):
    """Create the trophy leaderboard embed."""
    all_trophies = await fetch_all_trophies(bot)
    embed = discord.Embed(
        title=f"🏆 {guild.name} Trophy Leaderboard",
        color=0x135CC0,
    )
    footer_text = "Updated Trophy Leaderboard at"
    if all_trophies:
        sorted_trophies = sorted(all_trophies, key=lambda x: x["amount"], reverse=True)
        pretty_log(
            tag="info",
            message="Creating trophy leaderboard embed with trophies data.",
            label="Trophy Leaderboard Embed",
        )

        first_place_user_id = None
        current_leaderboard_info = await fetch_current_leaderboard_info(bot)
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
            user_place_info = await fetch_user_place_and_trophies(bot, command_user)
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
async def new_first_place_announcement(
    bot: commands.Bot, guild: discord.Guild, member: discord.Member, trophy_amount: int
):
    """Announce new first place in the designated channel."""

    # Update in db first
    message_id = await fetch_leaderboard_message_id(bot)
    await update_first_place_in_db(
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

    """announcement_channel = guild.get_channel(
        VN_ALLSTARS_TEXT_CHANNELS.khys_chamber
    )  # Testing channel for now
    if not announcement_channel:
        pretty_log(
            tag="error",
            message="First place announcement channel not found.",
            label="First Place Announcement",
        )
        return
    embed = discord.Embed(
        title="👑 New First Place! 👑",
        description=f"Congratulations to {member.mention} for achieving first place on the trophy leaderboard!\n\nThey have a total of 🏆 {trophy_amount}!",
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    await announcement_channel.send(
        embed=embed,
        content=f"🎉 {member.mention} is now in first place on the trophy leaderboard! 🎉",
    )"""


# 🍭──────────────────────────────
#   🎀 trophies Update Leaderboard Command Function
# 🍭──────────────────────────────
async def trophy_update_leaderboard_func(
    bot: commands.Bot, guild: discord.Guild, user: discord.Member = None
):
    """Update the trophy leaderboard message in the designated channel."""
    leaderboard_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.clan_leaderboard)
    if not leaderboard_channel:
        pretty_log(
            tag="error",
            message="Leaderboard channel not found.",
            label="Trophy Leaderboard Update",
        )
        return
    # Get message ID
    current_leader_board_info = await fetch_current_leaderboard_info(bot)
    message_id = (
        current_leader_board_info["message_id"] if current_leader_board_info else None
    )

    if not message_id:
        pretty_log(
            tag="info",
            message="No existing leaderboard message ID found. Creating a new message.",
            label="Trophy Leaderboard Update",
        )
        leaderboard_embed = await create_leaderboard_embed(bot, guild)
        leaderboard_message = await leaderboard_channel.send(embed=leaderboard_embed)
        await upsert_leaderboard_msg_id(bot, leaderboard_message.id)
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
            leaderboard_embed = await create_leaderboard_embed(bot, guild)
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
            leaderboard_embed = await create_leaderboard_embed(bot, guild)
            leaderboard_message = await leaderboard_channel.send(
                embed=leaderboard_embed
            )
            await upsert_leaderboard_msg_id(bot, leaderboard_message.id)
