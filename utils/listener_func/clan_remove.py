import re
from datetime import datetime

import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import remove_member
from utils.essentials.pokemeow_member_reply import get_pokemeow_reply_member
from utils.logs.pretty_log import pretty_log
from utils.functions.webhook_func import send_webhook

FORMER_MEMBERS_CATEGORY_ID = 927658364618571776
LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 Auto Remove Member Handler
# 🍭──────────────────────────────
async def auto_clan_remove_handler(
    bot: discord.Client,
    member: discord.Member,
    replied_message: discord.Message,
    context: str,
):
    """Auto remove member from VNA members DB and move to Former Members category"""
    # Check if member has VNA Member role
    vna_member_role = member.guild.get_role(VN_ALLSTARS_ROLES.vna_member)

    # Get member channel id
    member_info = vna_members_cache.get(member.id)
    if not member_info:
        pretty_log(f"No member info found in cache for member ID: {member.id}")
        return

    member_channel_id = member_info["channel_id"] if member_info else None

    channel_line = ""
    if vna_member_role and vna_member_role in member.roles:
        # Remove member from VNA members database
        await remove_member(bot, member)

    # Check if Former members category exists and category doesnt have 50 channels
    former_members_category = discord.utils.get(
        member.guild.categories, id=FORMER_MEMBERS_CATEGORY_ID
    )
    # Check how many channels are in the Former Members category
    if (
        former_members_category
        and len(former_members_category.channels) < 50
        and member_channel_id
    ):
        # Fetch member channel
        member_channel = member.guild.get_channel(member_channel_id)
        if member_channel:
            # Move member channel to Former Members category
            try:
                await member_channel.edit(category=former_members_category)
                pretty_log(
                    f"Moved channel '{member_channel.name}' to Former Members category."
                )
                channel_line = f"\n• Moved channel {member_channel.mention} - {member_channel.name} to Former Members category."
            except Exception as e:
                pretty_log(
                    f"Failed to move channel '{member_channel.name}' to Former Members category. Error: {e}"
                )
    # Find another former members category with less than 50 channels
    elif former_members_category and len(former_members_category.channels) >= 50:
        for category in member.guild.categories:
            if (
                category.id != FORMER_MEMBERS_CATEGORY_ID
                and "former members" in category.name
            ):
                if len(category.channels) < 50:
                    # Fetch member channel
                    member_channel = member.guild.get_channel(member_channel_id)
                    if member_channel:
                        # Move member channel to this category
                        try:
                            await member_channel.edit(category=category)
                            pretty_log(
                                f"Moved channel '{member_channel.name}' to former members category '{category.name}'."
                            )
                            channel_line = f"\n• Moved channel {member_channel.mention} - {member_channel.name} to Former Members category '{category.name}'."
                            break
                        except Exception as e:
                            pretty_log(
                                f"Failed to move channel '{member_channel.name}' to Former Members category '{category.name}'. Error: {e}"
                            )
    # Log the clan leave event
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    message_link = None
    if log_channel:
        if context == "clan_leave_command":
            title = "Clan Member Left via Command"
            message_link = replied_message.jump_url if replied_message else None
        else:
            title = "Clan Member Removed"

        embed = discord.Embed(
            title=title,
            url = message_link if message_link else None,
            color=discord.Color.red(),
            description=(
                f"{message_link}"
                f"**Member:** {member.mention} ({member.display_name})\n"
                f"{channel_line}"
            ),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_footer(
            text=f"Member ID: {member.id}",
            icon_url=member.guild.icon.url if member.guild.icon else None,
        )
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )


# 🍭──────────────────────────────
#   🎀 Handle Clan Leave Command
# 🍭──────────────────────────────
async def handle_clan_leave_command(bot: discord.Client, message: discord.Message):
    """Handle clan leave command"""

    member = await get_pokemeow_reply_member(message)
    if not member:
        return

    replied_message = message.reference.resolved
    if replied_message:
        await replied_message.add_reaction(VN_ALLSTARS_EMOJIS.vna_sadcat)
        await auto_clan_remove_handler(
            bot, member, replied_message, context="clan_leave_command"
        )


async def handle_clan_kick_command(
    bot: discord.Client, member: discord.Member, message: discord.Message
):
    """Handle clan kick command"""
    content = message.content
    if not content:
        return

    match = re.search(r"\(ID:\s*(\d+)\)", content)
    if not match:
        pretty_log("error", "Could not find user ID in the kick command message.")
        return

    user_id = int(match.group(1))
    guild = message.guild

    member = guild.get_member(user_id)
    if not member:
        pretty_log("error", f"Member with ID {user_id} not found in the guild.")
        return

    replied_message = message.reference.resolved
    if replied_message:
        await replied_message.add_reaction(Emojis.orange_check)
        await auto_clan_remove_handler(
            bot, member, replied_message, context="clan_kick_command"
        )
