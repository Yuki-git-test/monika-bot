from datetime import datetime
import re

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import (
    update_member_pokemeow_name,
    update_member_user_name,
)
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.logs.pretty_log import pretty_log


class OnUserUpdateCog(discord.ext.commands.Cog):
    """Cog to handle user profile update events."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        # Only log updates for users in the VNA server
        for guild in self.bot.guilds:
            if guild.id == VNA_SERVER_ID:
                member = guild.get_member(after.id)
                if not member:
                    continue
                log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.member_logs)
                if not log_channel:
                    continue
                changes = []
                if before.name != after.name:
                    changes.append(f"**Username:** `{before.name}` → `{after.name}`")
                    # Update in database
                    member_id = after.id
                    member_info = vna_members_cache.get(member_id)
                    if member_info:
                        old_username = member_info.get("user_name", "")
                        if old_username != after.name:
                            try:
                                await update_member_user_name(self.bot, member, after.name)
                                pretty_log(
                                    message=(
                                        f"Updated username for member '{member.display_name}' "
                                        f"from '{old_username}' to '{after.name}'."
                                    ),
                                    tag="info",
                                    label="Username Update",
                                )
                            except Exception as e:
                                pretty_log(
                                    message=(
                                        f"Failed to update username for member '{member.display_name}'. "
                                        f"Error: {e}"
                                    ),
                                    tag="error",
                                    label="Username Update",
                                )
                if before.discriminator != after.discriminator:
                    changes.append(
                        f"**Discriminator:** `{before.discriminator}` → `{after.discriminator}`"
                    )
                if before.avatar != after.avatar:
                    changes.append(f"**Avatar changed**")
                if not changes:
                    return
                embed = discord.Embed(
                    title="📝 User Profile Updated",
                    color=discord.Color.blurple(),
                    description=f"{after.mention} ({after.id})\n" + "\n".join(changes),
                    timestamp=datetime.now(),
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                await log_channel.send(embed=embed)


async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(OnUserUpdateCog(bot))
