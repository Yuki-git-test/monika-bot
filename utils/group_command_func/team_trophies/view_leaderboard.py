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
    fetch_team_trophy,
    upsert_team_trophy,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

TROPHY_THUMBNAIL_URL = Thumbnails.trophy
from .update_leaderboard import create_leaderboard_embed


# 🍭──────────────────────────────
#   🎀 View Leaderboard Command Function
# 🍭──────────────────────────────
async def view_leaderboard_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    guild = interaction.guild

    if interaction.guild_id != VNA_SERVER_ID:
        await interaction.response.send_message(
            "This command can only be used in the VNA server.", ephemeral=True
        )
        return

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching leaderboard...",
        ephemeral=False,
    )

    embed = await create_leaderboard_embed(bot, guild)

    await loader.success(embed=embed, content="")
