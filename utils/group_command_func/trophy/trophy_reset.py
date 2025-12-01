from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.trophy import reset_leaderboard, reset_trophies
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log
from utils.functions.webhook_func import send_webhook

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 trophies Reset Command Function
# 🍭──────────────────────────────
async def trophy_reset_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    guild = interaction.guild
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can reset trophies.", ephemeral=True
        )
        return

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Resetting all trophies...",
        ephemeral=False,
    )
    # Reset trophies in the database
    try:
        await reset_trophies(bot)
        await reset_leaderboard(bot)
        await loader.success(content="All trophies have been reset.")

        # Send log embed to log channel
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="Trophies Reset",
                description=f"All trophies have been reset by {interaction.user.mention}.",
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )
        pretty_log(
            message=f"All trophies have been reset by {interaction.user}.",
            tag="info",
        )

    except Exception as e:
        await loader.error(content="An error occurred while resetting trophies.")
        pretty_log(
            message=f"Error resetting trophies: {e}",
            tag="error",
        )
        return
