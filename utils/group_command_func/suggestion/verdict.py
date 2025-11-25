import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.suggestions_db_func import fetch_suggestion_by_id, remove_suggestion_by_id
from utils.essentials.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log

UPVOTE_EMOJI = "✅"
DOWNVOTE_EMOJI = "❌"
TEST_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.khys_chamber
REAL_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.suggestions
SUGGESTION_CHANNEL_ID = (
    REAL_SUGGESTION_CHANNEL_ID  # Change to REAL_SUGGESTION_CHANNEL_ID when ready
)
from utils.essentials.role_checks import is_staff_member


# 🍭──────────────────────────────
#   🎀 Function: Suggestion Verdict
# 🍭──────────────────────────────
async def suggestion_verdict_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    suggestion_id: int,
    verdict: str,
    reason: str = None,
):
    """Handle the verdict of a suggestion."""
    guild = interaction.guild
    user = interaction.user

    # Check if user is a staff member
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can give verdicts on suggestions.", ephemeral=True
        )
        return

    if verdict.lower() not in ["approved", "denied"]:
        await interaction.response.send_message(
            "Verdict must be either 'approved' or 'denied'.", ephemeral=True
        )
        return

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Processing the suggestion verdict...",
        ephemeral=True,
    )

    # Check if suggestion id exists in db

    suggestion_info = await fetch_suggestion_by_id(bot, suggestion_id)
    if not suggestion_info:
        await loader.error(content=f"Suggestion ID {suggestion_id} does not exist.")
        return
    suggestion_message_id = suggestion_info["message_id"]
    suggestion_channel = guild.get_channel(SUGGESTION_CHANNEL_ID)

    try:
        suggestion_message = await suggestion_channel.fetch_message(suggestion_message_id)
    except discord.NotFound:
        suggestion_message = None

    if not suggestion_message:
        await loader.error(
            content=f"Suggestion message for ID {suggestion_id} was not found."
        )
        return

    # Update embed with verdict
    embed = suggestion_message.embeds[0]
    if verdict.lower() =="approved":
        color = 0x00FF00  # Green
    elif verdict.lower() == "denied":
        color = 0xFF0000  # Red
    embed.color = color
    embed.add_field(name="Verdict", value=verdict, inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    # Get upvote and downvote counts
    upvote_count = 0
    downvote_count = 0
    for reaction in suggestion_message.reactions:
        if str(reaction.emoji) == UPVOTE_EMOJI:
            upvote_count = reaction.count - 1  # Exclude bot's own reaction
        elif str(reaction.emoji) == DOWNVOTE_EMOJI:
            downvote_count = reaction.count - 1  # Exclude bot's own reaction

    total_votes = upvote_count + downvote_count
    upvote_percentage = (upvote_count / total_votes) * 100 if total_votes > 0 else 0
    downvote_percentage = (downvote_count / total_votes) * 100 if total_votes > 0 else 0
    # Check if first field name is "Votes" and update it
    if suggestion_message.embeds[0].fields and suggestion_message.embeds[0].fields[0].name == "Votes":
        embed.set_field_at(
            0,
            name="Votes",
            value=(
                f"{UPVOTE_EMOJI} {upvote_count} Upvotes ({upvote_percentage:.2f}%)\n"
                f"{DOWNVOTE_EMOJI} {downvote_count} Downvotes ({downvote_percentage:.2f}%)"
            ),
            inline=False,
        )
    else:
        embed.insert_field_at(
            0,
            name="Votes",
            value=(
                f"{UPVOTE_EMOJI} {upvote_count} Upvotes ({upvote_percentage:.2f}%)\n"
                f"{DOWNVOTE_EMOJI} {downvote_count} Downvotes ({downvote_percentage:.2f}%)"
            ),
            inline=False,
        )
    await suggestion_message.edit(embed=embed)

    # Remove from database
    await remove_suggestion_by_id(bot, suggestion_id)

    # Send confirmation
    await loader.success(
        content=f"Suggestion ID {suggestion_id} has been {verdict.lower()} successfully."
    )
