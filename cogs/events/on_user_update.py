import re
from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
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
                change_list = []
                clan_member = False
                if before.name != after.name:
                    changes.append(f"**Username:** `{before.name}` → `{after.name}`")
                    change_list.append("username")
                    # Update in database
                    member_id = after.id
                    member_info = vna_members_cache.get(member_id)
                    if member_info:
                        old_username = member_info.get("user_name", "")
                        clan_member = True
                        if old_username != after.name:
                            try:
                                await update_member_user_name(
                                    self.bot, member, after.name
                                )
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

                if before.avatar != after.avatar:
                    change_list.append("avatar")
                if not changes:
                    return

                user_str = "Clan Member" if clan_member else "User"
                description = f"**{user_str}:** {after.mention} - {after.display_name}"
                log_embed = discord.Embed(
                    description=description,
                    color=MONIKA_EMBED_COLOR,
                    timestamp=datetime.now(),
                )
                log_embed.set_author(
                    name=after.display_name,
                    icon_url=after.display_avatar.url,
                )
                log_embed.set_thumbnail(url=after.display_avatar.url)
                log_embed.set_footer(
                    text=f"User ID: {after.id}",
                    icon_url=guild.icon.url if guild.icon else None,
                )
                if "username" in change_list and "avatar" not in change_list:
                    log_embed.title = f"📝 {user_str} Username Updated"
                    value_str = f"**Username:** `{before.name}` → `{after.name}`"

                elif "avatar" in change_list and "username" not in change_list:
                    log_embed.title = f"🖼️ {user_str} Avatar Updated"
                    value_str = f"**Avatar:** [Before]({before.display_avatar.url}) → [After]({after.display_avatar.url})"
                elif "username" in change_list and "avatar" in change_list:
                    log_embed.title = f"🧡 {user_str} Profile Updated"
                    value_str = (
                        f"**Username:** `{before.name}` → `{after.name}`\n"
                        f"**Avatar:** [Before]({before.display_avatar.url}) → [After]({after.display_avatar.url})"
                    )
                log_embed.add_field(name="Changes", value=value_str, inline=False)
                await log_channel.send(embed=log_embed)


async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(OnUserUpdateCog(bot))
