import discord
from discord.ext import commands

from constants.vn_allstars_constants import VNA_SERVER_ID
from utils.functions.on_role_add import handle_role_add
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Event: On Member Update
# 🍭──────────────────────────────
class OnMemberUpdateCog(commands.Cog):
    """Cog to handle member update events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
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

        # Handle added roles
        if added_roles:
            for role in added_roles:
                pretty_log(
                    message=f"Role '{role.name}' added to member '{after.display_name}'.",
                    tag="info",
                    label="Member Update Event",
                )
                await handle_role_add(self.bot, after, role)


async def setup(bot: commands.Bot):
    """Setup the OnMemberUpdateCog."""
    await bot.add_cog(OnMemberUpdateCog(bot))
