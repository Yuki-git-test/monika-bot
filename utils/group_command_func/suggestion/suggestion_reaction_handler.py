import discord

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.suggestions_db_func import fetch_suggestion_by_message_id
from utils.logs.pretty_log import pretty_log

UPVOTE_EMOJI = "✅"
DOWNVOTE_EMOJI = "❌"
TEST_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.khys_chamber
REAL_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.suggestions
SUGGESTION_CHANNEL_ID = (
    REAL_SUGGESTION_CHANNEL_ID  # Change to REAL_SUGGESTION_CHANNEL_ID when ready
)


# 🍭──────────────────────────────
#   🎀 Function: Suggestion Reaction Handler
# 🍭──────────────────────────────
async def suggestion_reaction_handler_func(
    bot: discord.Client,
    reaction: discord.Reaction,
    message: discord.Message,
):
    """Handle reactions added to suggestion messages."""
    message_id = message.id
    suggestion_info = await fetch_suggestion_by_message_id(bot, message_id)
    if not suggestion_info:
        return  # Not a suggestion message

    embed = message.embeds[0]
    if not embed:
        return

    # Handle upvote reaction
    if str(reaction.emoji) == UPVOTE_EMOJI or str(reaction.emoji) == DOWNVOTE_EMOJI:
        # Get current upvotes and downvotes reactions
        upvote_reaction = discord.utils.get(message.reactions, emoji=UPVOTE_EMOJI)
        downvote_reaction = discord.utils.get(message.reactions, emoji=DOWNVOTE_EMOJI)
        upvotes = upvote_reaction.count - 1 if upvote_reaction else 0
        downvotes = downvote_reaction.count - 1 if downvote_reaction else 0

        total_votes = upvotes + downvotes
        upvote_reaction_percentage = (
            (upvotes / total_votes) * 100 if total_votes > 0 else 0
        )
        downvote_reaction_percentage = (
            (downvotes / total_votes) * 100 if total_votes > 0 else 0
        )
        # Update the embed with new counts

        # Check if first field is "Votes" then update it
        if embed.fields and embed.fields[0].name == "Votes":
            embed.set_field_at(
                0,
                name="Votes",
                value=(
                    f"✅ Upvotes: {upvotes} ({upvote_reaction_percentage:.2f}%)\n"
                    f"❌ Downvotes: {downvotes} ({downvote_reaction_percentage:.2f}%)"
                ),
                inline=False,
            )
            await message.edit(embed=embed)
            pretty_log(
                "info",
                f"Updated suggestion message ID {message_id} with {upvotes} upvotes and {downvotes} downvotes.",
            )
