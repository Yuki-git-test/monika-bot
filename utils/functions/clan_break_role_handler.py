import time
from datetime import datetime

import discord

from constants.vn_allstars_constants import (
    MONIKA_APP_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
    KHY_USER_ID
)
from utils.cache.cache_list import vna_members_cache
from utils.db.clan_break_members_db import (
    fetch_all_clan_break_members,
    remove_clan_break_member,
    upsert_clan_break_member,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log


async def handle_clan_break_add_role(bot: discord.Client, member: discord.Member):
    """Handle clan break role assignment."""
    # Add to clan break members db
    ends_on = await upsert_clan_break_member(bot, member)
    pretty_log(
        "info",
        f"Added '{member.display_name}' to clan break members database.",
        label="Clan Break Role Handler",
    )
    # Log to clan break log channel
    guild = bot.get_guild(VNA_SERVER_ID)
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)
    assigned_on = int(time.time())
    ends_on_dt = f"<t:{ends_on}:f> <t:{ends_on}:R>" if ends_on else "Unknown"
    assigned_on_dt = f"<t:{assigned_on}:f>"
    if log_channel:
        embed = discord.Embed(
            title="🛡️ Clan Break Role Assigned",
            color=MONIKA_EMBED_COLOR,
            description=f"**Member:** {member.mention}",
            timestamp=datetime.now(),
        )
        embed.add_field(
            name="Assigned On",
            value=assigned_on_dt,
            inline=False,
        )
        embed.add_field(
            name="Ends On",
            value=ends_on_dt,
            inline=False,
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        embed.set_thumbnail(
            url=clan_break_role.icon.url if clan_break_role.icon else None
        )
        embed.set_footer(
            text=f"User ID: {member.id}",
            icon_url=guild.icon.url if guild.icon else None,
        )

        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )


async def handle_clan_break_remove_role(
    bot: discord.Client, member: discord.Member, remover: discord.Member = None
):
    """Handle clan break removal assignment."""
    # Get personal channel
    guild = bot.get_guild(VNA_SERVER_ID)
    clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    member_info = vna_members_cache.get(member.id)
    if not member_info:
        pretty_log(
            "error",
            f"Member {member.display_name} not found in VNA members cache.",
            label="Clan Break Role Handler",
        )
        return
    channel_id = member_info.get("channel_id")
    if not channel_id:
        pretty_log(
            "error",
            f"Personal channel for member {member.display_name} not found in VNA members cache.",
            label="Clan Break Role Handler",
        )
        return
    personal_channel = guild.get_channel(channel_id)

    # Remove from clan break members db
    await remove_clan_break_member(bot, member.id)
    if remover and remover.id == KHY_USER_ID:
        return # Early return for Khy's manual removals, testing purposes only

    if remover and remover.id == MONIKA_APP_ID:
        dm_msg = (
            "Your **Clan Break** role has been automatically removed as your break period has ended.\n"
            "If you wish to extend your break, please request the role again from a staff member.\n\n"
            "If you choose not to reapply and you fail to meet this week’s activity requirements, "
            "you may receive a **Probation** role."
        )
        dm_embed = discord.Embed(
            title="🛡️ Clan Break Role Expired",
            description=dm_msg,
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        dm_embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        dm_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        try:
            await member.send(embed=dm_embed, content=f"{member.mention}")
            pretty_log(
                "info",
                f"Sent DM to {member.display_name} about Clan Break role expiration.",
                label="Clan Break Role Handler",
            )
        except Exception as e:
            pretty_log(
                "info",
                f"Failed to send DM to {member.display_name} about Clan Break role expiration: {e}",
                label="Clan Break Role Handler",
            )
            # Fall back to sending message in personal channel
            if personal_channel:
                await personal_channel.send(embed=dm_embed, content=f"{member.mention}")
            else:
                # Send to clan general channel if personal channel not found
                general_channel = bot.get_channel(
                    VN_ALLSTARS_TEXT_CHANNELS.clan_general
                )
                if general_channel:
                    await general_channel.send(f"{member.mention}", embed=dm_embed)
                    pretty_log(
                        "info",
                        f"Sent Clan Break expiration message to {member.display_name} in clan general channel.",
                        label="Clan Break Role Handler",
                    )
        log_embed = discord.Embed(
            title="🛡️ Clan Break Role Expired",
            color=MONIKA_EMBED_COLOR,
            description=f"**Member:** {member.mention}",
            timestamp=datetime.now(),
        )
        log_embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        log_embed.set_thumbnail(
            url=clan_break_role.icon.url if clan_break_role.icon else None
        )
        log_embed.set_footer(
            text=f"User ID: {member.id}",
            icon_url=guild.icon.url if guild.icon else None,
        )
    else:
        # Early Return
        dm_msg = (
            "Welcome back! Your **Clan Break** role has been removed as you’ve returned early.\n"
            "Your standing in the clan has been restored, and you may resume your activities as normal.\n\n"
            "A quick reminder: weekly catch requirement of 1,500 (Catchbot not included) still apply, so please make sure to meet them "
            "to avoid receiving a **Probation** role."
        )
        dm_embed = discord.Embed(
            title="🛡️ Clan Break Role Removed",
            description=dm_msg,
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        dm_embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        dm_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        try:
            await member.send(embed=dm_embed, content=f"{member.mention}")
            pretty_log(
                "info",
                f"Sent DM to {member.display_name} about Clan Break role removal.",
                label="Clan Break Role Handler",
            )
        except Exception as e:
            pretty_log(
                "info",
                f"Failed to send DM to {member.display_name} about Clan Break role removal: {e}",
                label="Clan Break Role Handler",
            )
            # Fall back to sending message in personal channel
            if personal_channel:
                await personal_channel.send(embed=dm_embed, content=f"{member.mention}")
            else:
                # Send to clan general channel if personal channel not found
                general_channel = bot.get_channel(
                    VN_ALLSTARS_TEXT_CHANNELS.clan_general
                )
                if general_channel:
                    await general_channel.send(f"{member.mention}", embed=dm_embed)
                    pretty_log(
                        "info",
                        f"Sent Clan Break removal message to {member.display_name} in clan general channel.",
                        label="Clan Break Role Handler",
                    )
        removed_by_str = ""
        if remover:
            removed_by_str = f"**Removed By:** {remover.mention} - {remover.display_name}"
        log_embed = discord.Embed(
            title="🛡️ Clan Break Role Removed Early",
            color=MONIKA_EMBED_COLOR,
            description=(
                f"**Member:** {member.mention}\n"
                f"{removed_by_str}"
            ),
            timestamp=datetime.now(),
        )
        log_embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        log_embed.set_thumbnail(
            url=clan_break_role.icon.url if clan_break_role.icon else None
        )
        log_embed.set_footer(
            text=f"User ID: {member.id}",
            icon_url=guild.icon.url if guild.icon else None,
        )
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=log_embed,
        )
