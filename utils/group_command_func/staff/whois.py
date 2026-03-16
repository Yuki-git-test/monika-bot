from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import fetch_all_members
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log
from utils.db.custom_roles_db_func import fetch_custom_role_id
from utils.db.personal_channels_db import fetch_personal_channel_id
from utils.essentials.display_format import format_display_perks, format_display_faction
async def whois_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member = None,
    member_id: str = None,
):
    """Fetch and display detailed information about a server member."""
    # Defer
    loader = await pretty_defer(
        interaction=interaction, content="Fetching member info...", ephemeral=False
    )

    # Check if staff member
    if not await is_staff_member(interaction=interaction):
        await loader.error(
            content="You do not have permission to use this command.",
        )
        return

    # Check if there is input
    if not member and not member_id:
        await loader.error(
            content="Please provide a member or member ID to look up.",
        )
        return
    # Fetch member by ID if member_id is provided
    guild = bot.get_guild(VNA_SERVER_ID)

    if member_id and not member:
        member_id = int(member_id)
        try:
            member = await guild.fetch_member(member_id)
        except discord.NotFound:
            await loader.error(
                content=f"No member found with ID {member_id}.",
            )
            return
        except discord.HTTPException as e:
            await loader.error(
                content=f"Failed to fetch member with ID {member_id}: {e}",
            )
            return

    if not member:
        await loader.error(
            content="Member not found.",
        )
        return
    # Get roles
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    wsg_member_role = guild.get_role(VN_ALLSTARS_ROLES.wsg_members)
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
    owner_role = guild.get_role(VN_ALLSTARS_ROLES.owner)
    former_member_role = guild.get_role(VN_ALLSTARS_ROLES._former_members)

    # Default values
    member_id = member.id if member else member_id
    member_mention = member.mention
    server_joined_at_ts = (
        int(member.joined_at.timestamp()) if member.joined_at else None
    )
    server_joined_at_str = f"<t:{server_joined_at_ts}:D>"
    account_created_at_ts = int(member.created_at.timestamp())
    account_created_at_str = f"<t:{account_created_at_ts}:D>"
    channel_id = await fetch_personal_channel_id(bot, member.id)
    if channel_id:
        channel_mention = f"<#{channel_id}>"
    else:
        channel_id = None
    color = MONIKA_EMBED_COLOR
    custom_role = None
    custom_role_id = await fetch_custom_role_id(bot, member)
    if custom_role_id:
        custom_role = guild.get_role(custom_role_id)
        if custom_role:
            color = custom_role.color

    # Get joined clan date
    member_info = vna_members_cache.get(member.id)
    clan_joined_date = None
    if member_info:
        clan_joined_date = member_info.get("clan_joined_date")
        if clan_joined_date:
            clan_joined_date_str = f"<t:{clan_joined_date}:D>"
    perks = None
    if member_info:
        perks = member_info.get("perks")
        if perks:
            perks = format_display_perks(perks)
    faction = None
    if member_info:
        faction = member_info.get("faction")
        if faction:
            faction = format_display_faction(faction)

    pokemeow_name = None
    if member_info:
        pokemeow_name = member_info.get("pokemeow_name")

    # Create embed
    embed = discord.Embed(
        color=color,
        timestamp=datetime.now(),
    )

    if owner_role in member.roles:
        title_str = "VNA Clan Owner"

    elif staff_role in member.roles:
        title_str = "VNA Staff Member"

    elif vna_member_role in member.roles:
        title_str = "VNA Clan Member"

    elif wsg_member_role in member.roles:
        title_str = "WSG Clan Member"
    elif former_member_role in member.roles:
        title_str = "Former VNA Clan Member"
    else:
        title_str = "Server Member"

    embed.add_field(
        name="Title", value=title_str, inline=True
    )
    embed.add_field(
        name="Member", value=member_mention, inline=True
    )
    embed.add_field(
        name="Member ID", value=member_id, inline=True
    )
    if pokemeow_name:
        embed.add_field(
            name="PokéMeow Name", value=pokemeow_name, inline=True
        )
    if custom_role:
        embed.add_field(
            name="Custom Role", value=custom_role.mention, inline=True
        )
    if channel_id:
        embed.add_field(
            name="Personal Channel", value=channel_mention, inline=True
        )
    if perks:
        embed.add_field(
            name="Perks", value=perks, inline=True
        )
    if faction:
        embed.add_field(
            name="Faction", value=faction, inline=True
        )

    if clan_joined_date:
        embed.add_field(
            name="Joined Clan On", value=clan_joined_date_str, inline=True
        )
    embed.add_field(
        name="Account Created",
        value=account_created_at_str,
        inline=True,
    )
    embed.add_field(
        name="Joined Server",
        value=server_joined_at_str,
        inline=True,
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url,
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await loader.success(
        embed=embed,
        content="",
    )