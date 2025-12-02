from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import update_member_fields, upsert_member
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Slash Command: Update Clan Member
# 🍭──────────────────────────────
async def update_member_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    pokemeow_name: str = None,
    channel: discord.TextChannel = None,
    perks: str = None,
    faction: str = None,
):
    """Update a clan member's information."""

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Updating {member.display_name} information...",
        ephemeral=False,
    )

    # Check if user is a staff member
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await loader.error(
            content="Only staff members can update clan member information."
        )
        return

    # Normalize input fields
    channel_id = channel.id if channel else None
    perks = perks.strip().lower() if perks else None
    faction = faction.strip().lower() if faction else None
    username = member.name
    pokemeow_name = pokemeow_name.strip().lower() if pokemeow_name else None

    # Get vna clan member role
    guild = interaction.guild
    vna_clan_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_clan_member_role not in member.roles:
        await loader.error(
            content=f"{member.display_name} doesn't have the {vna_clan_member_role.name} Role."
        )
        return

    # Check if they have inputted at least one field to update
    if not any([username, pokemeow_name, channel, perks, faction]):
        await loader.error(content="Please provide at least one field to update.")
        return

    # Make base embed
    embed = discord.Embed(
        color=MONIKA_EMBED_COLOR,
        timestamp=datetime.now(),
        description=f"**Member:** {member.mention}\n",
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"User ID: {member.id}", icon_url=guild.icon.url if guild.icon else None
    )

    # Get old values for logging
    old_member_info = vna_members_cache.get(member.id)
    if not old_member_info:
        # Upsert member info if not found in cache
        try:
            success = await upsert_member(
                bot,
                user=member,
                channel_id=channel_id,
                perks=perks,
                faction=faction,
                pokemeow_name=pokemeow_name,
            )
            if not success:
                await loader.error(
                    content=f"Failed to upsert {member.display_name} information in the database."
                )
                return
            
            embed.title = "✅ Member Information Upserted"
            field_value_lines = []
            if pokemeow_name:
                field_value_lines.append(f"**PokéMeow Name:** {pokemeow_name}")
            if channel_id:
                field_value_lines.append(f"**Channel:** <#{channel_id}>")
            if perks:
                field_value_lines.append(f"**Perks:** {perks}")
            if faction:
                field_value_lines.append(f"**Faction:** {faction}")
            embed.add_field(name="Details", value="\n".join(field_value_lines))

        except Exception as e:
            pretty_log(
                "error",
                f"Failed to upsert member {member.display_name} ({member.id}) before update: {e}",
            )
            await loader.error(
                content=f"Failed to upsert {member.display_name} information before update."
            )
            return
    # Update member in the database
    elif old_member_info:
        success = await update_member_fields(
            bot=bot,
            user=member,
            user_name=username,
            pokemeow_name=pokemeow_name,
            channel_id=channel_id,
            perks=perks,
            faction=faction,
        )
        if not success:
            await loader.error(
                content=f"Failed to update {member.display_name} information in the database."
            )
            return
        # Old values for logging
        old_pokemeow_name = old_member_info.get("pokemeow_name", "N/A")
        old_channel_id = old_member_info.get("channel_id", None)
        old_perks = old_member_info.get("perks", "N/A")
        old_faction = old_member_info.get("faction", "N/A")
        # Build embed fields for updated values
        field_value_lines = []
        if pokemeow_name and pokemeow_name != old_pokemeow_name:
            field_value_lines.append(
                f"**PokéMeow Name:** {old_pokemeow_name} ➔ {pokemeow_name}"
            )
        if channel_id and channel_id != old_channel_id:
            old_channel_mention = f"<#{old_channel_id}>" if old_channel_id else "N/A"
            field_value_lines.append(
                f"**Channel:** {old_channel_mention} ➔ <#{channel_id}>"
            )
        if perks and perks != old_perks:
            field_value_lines.append(f"**Perks:** {old_perks} ➔ {perks}")
        if faction and faction != old_faction:
            field_value_lines.append(f"**Faction:** {old_faction} ➔ {faction}")
        if field_value_lines:
            embed.title = "✅ Member Information Updated"
            embed.add_field(name="Updated Details", value="\n".join(field_value_lines))

    # Send confirmation embed
    await loader.success(embed=embed, content="")
    pretty_log(
        "success",
        f"Updated member {member.display_name} ({member.id}) information successfully.",
    )

    # Send a log embed to your server log channel
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.member_logs)
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
