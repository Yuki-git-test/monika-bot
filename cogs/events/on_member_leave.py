from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_EMBED_COLOR,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log
from utils.cache.cache_list import vna_members_cache
LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
from utils.functions.webhook_func import send_webhook

# 🍭──────────────────────────────
#   🎀 Event: On Member Leave
# 🍭──────────────────────────────
class OnMemberLeaveCog(commands.Cog):
    """Cog to handle member leave events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave events."""
        # Only log leaves in VNA server
        guild = self.bot.get_guild(VNA_SERVER_ID)
        if guild is None:
            return

        if member.guild.id != VNA_SERVER_ID:
            return

        # Log member leave
        log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
        title_str = "👋 Member Left Server"
        # Check if its a clan member
        member_info  = vna_members_cache.get(member.id)
        if member_info:
            title_str = "💔 Clan Member Left Server"
        if log_channel:
            embed = discord.Embed(
                title=title_str,
                color=discord.Color.red(),
                description=(
                    f"**Member:** {member.mention} - {member.name}\n"
                    f"**Joined At:** {'<t:' + str(int(member.joined_at.timestamp())) + ':D>' if member.joined_at else 'Unknown'}\n"
                    f"**Account Created:** {'<t:' + str(int(member.created_at.timestamp())) + ':D>'}"
                ),
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )
            embed.set_footer(
                text=f"User ID: {member.id}",
                icon_url=member.guild.icon.url if member.guild.icon else None,
            )
            await send_webhook(
                bot=self.bot,
                channel=log_channel,
                embed=embed,
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberLeaveCog(bot))
