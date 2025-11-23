import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_EMBED_COLOR,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
WELCOME_IMAGE_URL = "https://media.discordapp.net/attachments/1380367804804497448/1442017447585775636/Untitled10_20230430230329.png?ex=6923e6e6&is=69229566&hm=6034d945d49319aedbaa26014588fb7a7ef9a9b63d5e8a0a080a71c30d8b1538&=&format=webp&quality=lossless"


# 🍭──────────────────────────────
#   🎀 Event: On Member Join
# 🍭──────────────────────────────
class OnMemberJoinCog(commands.Cog):
    """Cog to handle member join events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join events."""
        # Only log joins in VNA server
        guild = self.bot.get_guild(VNA_SERVER_ID)
        if guild is None:
            return

        if member.guild.id != VNA_SERVER_ID:
            return

        # Send welcome message
        welcome_channel = member.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.welcome)

        if welcome_channel:
            title = "👋 Welcome to VN Allstars!"
            desc = (
                f"Make sure to read <#{VN_ALLSTARS_TEXT_CHANNELS.rules}>\n"
                f"Annoucements are made in <#{VN_ALLSTARS_TEXT_CHANNELS.announcement}>\n"
                f"Get roles in <#{VN_ALLSTARS_TEXT_CHANNELS.roles}>\n"
            )
            embed = discord.Embed(
                title=title,
                description=desc,
                color=VNA_EMBED_COLOR,
            )
            member_count = len([m for m in member.guild.members if not m.bot])
            footer_text = f"{guild.name} Member #{member_count}"
            embed.set_footer(
                text=footer_text, icon_url=guild.icon.url if guild.icon else None
            )
            embed.set_author(
                name=member.display_name,
                icon_url=member.avatar.url if member.avatar else None,
            )
            embed.set_image(url=WELCOME_IMAGE_URL)
            await welcome_channel.send(content=member.mention, embed=embed)
        # Log member join
        log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="👋 Member Joined",
                color=discord.Color.green(),
                description=f"**Member:** {member.mention}\n**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            )
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            embed.set_footer(
                text=f"User ID: {member.id}",
                icon_url=member.guild.icon.url if member.guild.icon else None,
            )
            await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    """Setup the OnMemberJoinCog."""
    await bot.add_cog(OnMemberJoinCog(bot))
