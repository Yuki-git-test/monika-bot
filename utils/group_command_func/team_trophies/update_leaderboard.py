from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from constants.aesthetic import Thumbnails
from constants.vn_allstars_constants import (
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.team_trophies_db import (
    fetch_all_team_trophies,
    fetch_current_leaderboard_info,
    fetch_team_trophy,
    upsert_leaderboard_msg_id,
    upsert_team_trophy,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

TROPHY_THUMBNAIL_URL = Thumbnails.trophy


def format_trophy_amount(amount: int) -> str:
    """Formats the trophy amount with commas."""
    return f"🏆 **{amount:,}**"


async def create_leaderboard_embed(
    bot: commands.Bot,
    guild: discord.Guild,
):
    """Creates a team trophies leaderboard embed."""

    embed = discord.Embed(
        title="🏆 Team Trophies Leaderboard 🏆",
        color=discord.Color.gold(),
    )
    trophies_dict = await fetch_all_team_trophies(bot)
    if not trophies_dict:
        embed.description = "No team trophies data available."
        return embed
    # Convert dict to list of dicts for sorting
    all_trophies = [
        {"role_id": role_id, "role_name": data["role_name"], "amount": data["amount"]}
        for role_id, data in trophies_dict.items()
    ]
    # Sort trophies by amount in descending order
    sorted_trophies = sorted(all_trophies, key=lambda x: x["amount"], reverse=True)
    pretty_log(
        tag="info",
        message="Creating trophy leaderboard embed with trophies data.",
        label="Trophy Leaderboard Embed",
    )
    for index, trophy_info in enumerate(sorted_trophies[:25], start=1):
        role_id = trophy_info["role_id"]
        role_name = trophy_info["role_name"]
        amount = trophy_info["amount"]
        amount = format_trophy_amount(amount)
        role = guild.get_role(role_id)
        if role:
            embed.add_field(
                name=f"{index}. {role_name}",
                value=f"> - {amount}",
                inline=False,
            )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.timestamp = datetime.now()
    embed.set_footer(text="Updated on", icon_url=guild.icon.url if guild.icon else None)
    return embed


async def update_leaderboard_func(
    bot: commands.Bot, guild: discord.Guild, user: discord.Member = None
):
    """Updates the team trophies leaderboard in the designated channel."""
    leaderboard_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.clan_leaderboard)
    if not leaderboard_channel:
        pretty_log(
            tag="error",
            message=f"Leaderboard channel with ID {VN_ALLSTARS_TEXT_CHANNELS.clan_leaderboard} not found in guild '{guild.name}' (ID: {guild.id})",
        )
        return

    # Get message id
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
            await upsert_leaderboard_msg_id(
                bot, leaderboard_message.id, leaderboard_channel
            )
