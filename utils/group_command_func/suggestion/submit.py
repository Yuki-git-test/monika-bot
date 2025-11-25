import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.suggestions_db_func import get_latest_suggestion_id, insert_suggestion
from utils.essentials.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log

UPVOTE_EMOJI = "✅"
DOWNVOTE_EMOJI = "❌"
TEST_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.khys_chamber
REAL_SUGGESTION_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.suggestions
SUGGESTION_CHANNEL_ID = (
    REAL_SUGGESTION_CHANNEL_ID  # Change to REAL_SUGGESTION_CHANNEL_ID when ready
)


# 🍭──────────────────────────────
#   🎀 Modal: Suggestion Submit
# 🍭──────────────────────────────
class Suggestion_Submit_Modal(Modal):
    def __init__(self, bot: commands.Bot, user: discord.Member):
        super().__init__(title="Submit a Suggestion")
        self.bot = bot
        self.user = user

        self.suggestion_title = TextInput(
            required=True,
            label="Suggestion Title",
            placeholder="Enter the title of your suggestion",
            max_length=100,
        )
        self.suggestion_text = TextInput(
            style=discord.TextStyle.paragraph,
            required=True,
            label="Suggestion Text",
            placeholder="Describe your suggestion in detail",
            max_length=2000,
        )
        self.add_item(self.suggestion_title)
        self.add_item(self.suggestion_text)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Defer response
            loader = await pretty_defer(
                interaction=interaction,
                content="Submitting your suggestion...",
                ephemeral=True,
            )
            # Send message to suggestions channel
            suggestion_channel = interaction.guild.get_channel(SUGGESTION_CHANNEL_ID)
            latest_suggestion_id = await get_latest_suggestion_id(self.bot) or 0
            suggestion_number = latest_suggestion_id + 1
            embed = discord.Embed(
                title=self.suggestion_title.value,
                description=self.suggestion_text.value,
                color=MONIKA_EMBED_COLOR,
            )
            embed.add_field(
                name="Votes",
                value=f"{UPVOTE_EMOJI} 0 Upvotes (0%)\n{DOWNVOTE_EMOJI} 0 Downvotes (0%)",
                inline=False,
            )

            embed.set_thumbnail(url=Thumbnails.suggestions)
            embed.set_author(
                name=self.user.display_name, icon_url=self.user.display_avatar.url
            )
            embed.set_footer(
                text=f"Suggestion #{suggestion_number} | Submitted by {self.user.name}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
            )
            suggested_message = await suggestion_channel.send(embed=embed)
            await suggested_message.add_reaction(UPVOTE_EMOJI)
            await suggested_message.add_reaction(DOWNVOTE_EMOJI)

            thread_name = f"Suggestion #{suggestion_number} Discussion"
            thread = await suggested_message.create_thread(
                name=thread_name,
                reason="Discussion thread for suggestion",
            )

            # Insert suggestion into the database
            await insert_suggestion(
                bot=self.bot,
                message_id=suggested_message.id,
                user=self.user,
                suggestion_text=self.suggestion_text.value,
                suggestion_title=self.suggestion_title.value,
                thread_id=thread.id,
            )
            await loader.success(
                content=f"Your suggestion has been submitted to {suggestion_channel.mention} successfully!"
            )
            footer_text = f"{interaction.guild.name} Sticky Message"

            # Delete old sticky messages in the channel
            async for msg in suggestion_channel.history(limit=20):
                if msg.author == self.bot.user and msg.embeds:
                    old_embed = msg.embeds[0]
                    if (
                        old_embed.title == "💡 Suggestion Channel Guidelines"
                        and old_embed.footer
                        and old_embed.footer.text == footer_text
                    ):
                        await msg.delete()

            # Send sticky message embed in the channel
            desc = (
                f"# 💡 Suggestion Channel Guidelines"
                f"- Use `/suggestion submit` by Monika, to submit a new suggestion.\n"
                f"- React with {UPVOTE_EMOJI} to upvote and {DOWNVOTE_EMOJI} to downvote suggestions.\n"
                f"- Discuss suggestions in their respective threads.\n"
                f"- Staff will review and provide verdicts on suggestions."
            )

            sticky_embed = discord.Embed(
                description=desc,
                color=MONIKA_EMBED_COLOR,
            )
            sticky_embed.set_footer(
                text=footer_text,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
            )
            sticky_embed.set_thumbnail(
                url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            await suggestion_channel.send(embed=sticky_embed)
            pretty_log(
                "success",
                f"User {self.user.display_name} submitted suggestion ID {suggestion_number}.",
            )
        except Exception as e:
            pretty_log("error", f"Failed to submit suggestion: {e}")
            await loader.error(
                content="An error occurred while submitting your suggestion."
            )


# 🍭──────────────────────────────
#   🎀 Function: Suggestion Submit
# 🍭──────────────────────────────
async def submit_suggestion_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    """Function to handle suggestion submission."""
    user = interaction.user
    modal = Suggestion_Submit_Modal(bot, user)
    await interaction.response.send_modal(modal)
