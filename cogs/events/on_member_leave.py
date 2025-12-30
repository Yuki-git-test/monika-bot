from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_EMBED_COLOR,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.clan_break_members_db import remove_clan_break_member
from utils.db.custom_roles_db_func import fetch_custom_role_id, remove_role
from utils.db.kick_list_db import remove_kick_list_member
from utils.db.personal_channels_db import delete_personal_channel
from utils.db.probation_list_db import remove_probation_member
from utils.db.top_monthly_grinders_db import delete_top_monthly_grinder
from utils.db.vna_members_db_func import remove_member
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
from utils.functions.webhook_func import send_webhook

GRAVEYARD_CATEGORY_ID = 1329157603573633126


async def db_cleanup_on_member_leave(bot, member: discord.Member):
    """Clean up database entries when a member leaves."""
    await remove_member(bot, member)
    await remove_probation_member(bot, member.id)
    await remove_kick_list_member(bot, member.id)
    await delete_top_monthly_grinder(bot, member.id)
    await remove_clan_break_member(bot, member.id)
    await delete_personal_channel(bot, member.id)
    pretty_log(
        message=f"Cleaned up database entries for member '{member.display_name}' ({member.id}) who left the server.",
        tag="info",
    )


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
        member_info = vna_members_cache.get(member.id)
        personal_channel = None
        if member_info:
            title_str = "💔 Clan Member Left Server"
            channel_id = member_info.get("channel_id")
            if channel_id:
                personal_channel = member.guild.get_channel(channel_id)
                # Move personal channel to Graveyard category
                if personal_channel:
                    graveyard_category = discord.utils.get(
                        member.guild.categories, id=GRAVEYARD_CATEGORY_ID
                    )
                    if graveyard_category:
                        await personal_channel.edit(
                            category=graveyard_category,
                            reason=f"Member {member} ({member.id}) left the server.",
                        )
                        # Sync permissions to the new category
                        await personal_channel.edit(sync_permissions=True)

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
        # Remove custom role if exists
        custom_role_id = await fetch_custom_role_id(self.bot, member.id)
        if custom_role_id:
            # Delete the role from the server
            role = member.guild.get_role(custom_role_id)
            if role:
                try:
                    await role.delete(
                        reason=f"Removing custom role for member {member} ({member.id}) who left the server."
                    )
                    pretty_log(
                        message=f"Deleted custom role '{role.name}' ({role.id}) for member '{member.display_name}' who left the server.",
                        tag="info",
                        label="Custom Role Removal",
                    )
                except Exception as e:
                    pretty_log(
                        message=f"Error deleting custom role '{role.name}' ({role.id}): {e}",
                        tag="error",
                        label="Custom Role Removal",
                    )
            # Remove from database
            await remove_role(self.bot, member.id)
            
        # Clean up other database entries
        await db_cleanup_on_member_leave(self.bot, member)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberLeaveCog(bot))
