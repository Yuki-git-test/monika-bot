import discord
from discord.ext import commands

from constants.vn_allstars_constants import VNA_SERVER_ID
from utils.logs.pretty_log import pretty_log

# 🍭──────────────────────────────
#   🎀 Event: On Member Update
# 🍭──────────────────────────────
class OnMemberUpdateCog(commands.Cog):
    """Cog to handle member update events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ):
        """Handle member updates."""
        # Only log updates in VNA server
        guild = self.bot.get_guild(VNA_SERVER_ID)
        if guild is None:
            return

        if after.guild.id != VNA_SERVER_ID:
            return

        # 🍭──────────────────────────────
        #   🎀 Role Events
        # 🍭──────────────────────────────
        # Detect added roles
        added_roles = [role for role in after.roles if role not in before.roles]
        # Detect removed roles
        removed_roles = [role for role in before.roles if role not in after.roles]

        