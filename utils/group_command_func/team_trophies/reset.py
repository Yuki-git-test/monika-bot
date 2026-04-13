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
    KHY_USER_ID
)
from utils.db.team_trophies_db import delete_all_team_trophies
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.essentials.pretty_defer import pretty_defer

TROPHY_THUMBNAIL_URL = Thumbnails.trophy


async def reset_trophies_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    guild = interaction.guild

    if interaction.guild_id != VNA_SERVER_ID:
        await interaction.response.send_message(
            "This command can only be used in VNA server.", ephemeral=True
        )
        return

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content="Resetting all team trophies...",
        ephemeral=False,
    )

    # Delete all trophies from the database
    await delete_all_team_trophies(bot)

    pretty_log(
        tag="info",
        message="All team trophies have been reset.",
        label="Trophy Reset",
    )

    await loader.success(content="All team trophies have been successfully reset.")
    embed = discord.Embed(
        title="🏆 Team Trophies Reset 🏆",
        description=f"All team trophies have been reset by {interaction.user.mention}.",
        color=discord.Color.red(),
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url,
    )
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    if log_channel:
        await send_webhook(
            bot,
            log_channel,
            embed=embed,
        )

