import discord
from discord.ext import commands

from utils.group_command_func.suggestion.suggestion_reaction_handler import (
    suggestion_reaction_handler_func,
)
from constants.vn_allstars_constants import VNA_SERVER_ID
UPVOTE_EMOJI = "✅"
DOWNVOTE_EMOJI = "❌"
class OnReactionAddCog(commands.Cog):
    """Cog to handle reaction add events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # Only handle reactions added to messages in guilds
        if not reaction.message.guild:
            return

        # Only handle reactions in the VNA server
        if reaction.message.guild.id != VNA_SERVER_ID:
            return

        # Call the suggestion reaction handler
        if str(reaction.emoji) in [UPVOTE_EMOJI, DOWNVOTE_EMOJI]:
            await suggestion_reaction_handler_func(self.bot, reaction, reaction.message)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnReactionAddCog(bot))
