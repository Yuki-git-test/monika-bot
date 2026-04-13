import discord
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

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log
from datetime import datetime

from .update_leaderboard import format_trophy_amount, update_leaderboard_func


# 🍭──────────────────────────────
#   🎀 Trophies Multi Command Function
# 🍭──────────────────────────────
async def trophy_multi_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    action: str,
    amount: int,
    team1: discord.Role,
    team2: discord.Role = None,
    team3: discord.Role = None,
    team4: discord.Role = None,
    team5: discord.Role = None,
    team6: discord.Role = None,
    team7: discord.Role = None,
    team8: discord.Role = None,
    team9: discord.Role = None,
    team10: discord.Role = None,
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
        content=f"{action.capitalize()}ing trophies...",
        ephemeral=False,
    )

    # Validate amount
    if amount <= 0:
        await loader.error("Invalid amount provided for trophies.")
        return

    # Get list of teams
    teams = [team1, team2, team3, team4, team5, team6, team7, team8, team9, team10]

    # Fetch all trophies for comparison
    """all_trophies = await fetch_all_team_wars_trophies(bot)
    if not all_trophies:
        await loader.error("No team wars trophies data available in the database.")
        return"""

    summary_lines = []
    # Process each team
    for team in teams:
        if team is None:
            continue

        # Fetch current trophy count for the team
        trophy_record = await fetch_team_trophy(bot, team.id)
        current_amount = trophy_record["amount"] if trophy_record else 0
        current_amount_formatted = format_trophy_amount(current_amount)

        # Calculate new amount based on action
        if action == "add":
            new_amount = current_amount + amount
            new_amount_formatted = format_trophy_amount(new_amount)

            desc_line = (
                f"> - {team.name}: {current_amount_formatted} ➔ {new_amount_formatted}"
            )
            summary_lines.append(desc_line)
        elif action == "remove":
            new_amount = max(current_amount - amount, 0)  # Prevent negative trophies
            new_amount_formatted = format_trophy_amount(new_amount)
            desc_line = (
                f"> - {team.name}: {current_amount_formatted} ➔ {new_amount_formatted}"
            )
            summary_lines.append(desc_line)
        else:
            await loader.error("Invalid action. Use 'add' or 'remove'.")
            return

        # Upsert the new trophy count in the database
        await upsert_team_trophy(bot, team.id, team.name, new_amount)
        pretty_log(
            "info",
            f"{action.capitalize()}ed {amount} trophies for '{team.name}' (Role ID: {team.id}). New total: {new_amount}",
            label="Trophy Update",
        )
    # Build confirmation embed
    action_str = "Added" if action == "add" else "Removed"
    title = f"🏆 {action_str} Trophies Summary"
    desc = f"**{amount} Amount {action_str.lower()} for each team:**\n" + "\n".join(
        summary_lines
    )
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url,
    )
    await loader.success(embed=embed, content="Trophies updated successfully!")

    # Log the update in the server logs channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await send_webhook(bot, log_channel, embed=embed)

    # Update the leaderboard after processing all teams
    await update_leaderboard_func(bot, guild)
