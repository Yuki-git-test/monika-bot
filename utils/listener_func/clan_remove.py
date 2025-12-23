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
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

FORMER_MEMBERS_CATEGORY_ID = 927658364618571776
LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log
enable_debug(f"{__name__}.auto_clan_remove_handler")


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
    debug_log(
        f"Auto removing member {member.display_name} ({member.id})", highlight=True
    )
    # Get Roles
    guild = bot.get_guild(VNA_SERVER_ID)
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)
    former_member_role = guild.get_role(VN_ALLSTARS_ROLES._former_members)
    double_probation_role = guild.get_role(VN_ALLSTARS_ROLES.kick_list)
    
    # Check if member has VNA Member role
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)

    # Get member channel id
    member_info = vna_members_cache.get(member.id)
    if not member_info:
        pretty_log(f"No member info found in cache for member ID: {member.id}")
        return

    member_channel_id = member_info["channel_id"] if member_info else None
    pretty_log(
        "info",
        f"Member {member.display_name} ({member.id}) channel ID: {member_channel_id}",
    )

    channel_line = ""
    # Remove probation roles and clan role and add former member role
    roles_to_remove = []
    if probation_role and probation_role in member.roles:
        roles_to_remove.append(probation_role)
    if double_probation_role and double_probation_role in member.roles:
        roles_to_remove.append(double_probation_role)
    if vna_member_role and vna_member_role in member.roles:
        roles_to_remove.append(vna_member_role)
    if former_member_role and former_member_role not in member.roles:
        await member.add_roles(former_member_role, reason="Member removed from clan")
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove, reason="Member removed from clan")

    # Remove member from VNA members database
    await remove_member(bot, member)

    # Check if Former members category exists and category doesnt have 50 channels
    former_members_category = discord.utils.get(
        guild.categories, id=FORMER_MEMBERS_CATEGORY_ID
    )
    # Check how many channels are in the Former Members category
    if (
        former_members_category
        and len(former_members_category.channels) < 50
        and member_channel_id
    ):
        # Fetch member channel
        member_channel = guild.get_channel(member_channel_id)
        if member_channel:
            debug_log(
                f"Found member channel: {member_channel.name} ({member_channel.id})"
            )
            # Move member channel to Former Members category
            try:
                debug_log(
                    f"Moving channel ID {member_channel.id} to Former Members category"
                )
                await member_channel.edit(category=former_members_category)
                pretty_log(
                    f"Moved channel '{member_channel.name}' to Former Members category."
                )
                channel_line = f"\n• Moved channel {member_channel.mention} - {member_channel.name} to Former Members category."
            except Exception as e:
                pretty_log(
                    f"Failed to move channel '{member_channel.name}' to Former Members category. Error: {e}"
                )
        else:
            debug_log(f"Member channel with ID {member_channel_id} not found in guild.")
    # Find another former members category with less than 50 channels
    elif former_members_category and len(former_members_category.channels) >= 50:
        found_category = False
        for category in member.guild.categories:
            if (
                category.id != FORMER_MEMBERS_CATEGORY_ID
                and "former members" in category.name
            ):
                if len(category.channels) < 50:
                    found_category = True
                    # Fetch member channel
                    member_channel = member.guild.get_channel(member_channel_id)
                    if member_channel:
                        debug_log(
                            f"Found member channel: {member_channel.name} ({member_channel.id})"
                        )
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
                    else:
                        debug_log(
                            f"Member channel with ID {member_channel_id} not found in guild."
                        )
        if not found_category:
            debug_log(
                "No suitable 'former members' category found with less than 50 channels."
            )
    # Log the clan leave event
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    message_link = None
    if log_channel:
        if context == "clan_leave_command":
            title = "Clan Member Left via Command"
            message_link = replied_message.jump_url if replied_message else ""
        else:
            title = "Clan Member Removed"

        embed = discord.Embed(
            title=title,
            url=message_link if message_link else None,
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


async def handle_clan_kick_command(bot: discord.Client, message: discord.Message):
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
