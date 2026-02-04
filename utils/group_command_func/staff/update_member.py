from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
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
    member: discord.Member = None,
    member_id: int = None,
    pokemeow_name: str = None,
    channel: discord.TextChannel = None,
    perks: str = None,
    faction: str = None,
    clan_joined_date: str = None,
):
    """Update a clan member's information."""
    if not member and not member_id:
        await interaction.response.send_message(
            "Please provide either a member or member ID to update.", ephemeral=True
        )
        return

    used_member = True if member else False
    # Resolve member by ID if necessary
    if not member and member_id:
        member = interaction.guild.get_member(member_id)
        if not member:
            # Use discord user fetch as fallback
            try:
                member = await bot.fetch_user(member_id)
            except discord.NotFound:
                await interaction.response.send_message(
                    f"Could not find a member with ID {member_id}.", ephemeral=True
                )
                return
    vna_member_id = member.id

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Updating {member.name} information...",
        ephemeral=False,
    )

    # Verify staff
    if not await is_staff_member(interaction=interaction):
        await loader.error("Only staff members can update clan member information.")
        return

    # Normalize inputs
    clan_joined_date = int(clan_joined_date) if clan_joined_date else None
    channel_id = channel.id if channel else None
    perks = perks.strip().lower() if perks else None
    faction = faction.strip().lower() if faction else None
    pokemeow_name = pokemeow_name.strip().lower() if pokemeow_name else None

    guild = interaction.guild
    vna_clan_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    # Get cached record
    old = vna_members_cache.get(member.id)

    if used_member and vna_clan_member_role not in member.roles:
        await loader.error(
            f"{member.display_name} doesn't have the {vna_clan_member_role.name} Role."
        )
        return

    if not used_member and not old:
        await loader.error(
            f"{member.name} is not in the database. Please provide a valid member with the clan member role."
        )
        return

    # Make sure at least 1 field was provided
    if not any([pokemeow_name, channel, perks, faction, clan_joined_date]):
        await loader.error("Please provide at least one field to update.")
        return

    # Base embed
    embed = discord.Embed(
        color=MONIKA_EMBED_COLOR,
        timestamp=datetime.now(),
        description=f"**Member:** {member.mention}\n",
    )
    embed.set_author(name=member.name, icon_url=member.avatar.url)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(
        text=f"User ID: {member.id}",
        icon_url=guild.icon.url if guild.icon else None,
    )

    # ╔═══════════════════════════════╗
    #   CASE 1: Member not in cache
    # ╚═══════════════════════════════╝
    if not old:
        success = await upsert_member(
            bot,
            user=member,
            channel_id=channel_id,
            perks=perks,
            faction=faction,
            pokemeow_name=pokemeow_name,
            clan_joined_date=clan_joined_date,
        )

        if not success:
            await loader.error(
                f"Failed to upsert {member.name} into the database."
            )
            return

        embed.title = "✅ Member Information Upserted"

        field_value_lines = []
        if pokemeow_name is not None:
            field_value_lines.append(f"**PokéMeow Name:** {pokemeow_name}")
        if channel_id is not None:
            field_value_lines.append(f"**Channel:** <#{channel_id}>")
        if perks is not None:
            field_value_lines.append(f"**Perks:** {perks}")
        if faction is not None:
            field_value_lines.append(f"**Faction:** {faction}")
        if clan_joined_date is not None:
            field_value_lines.append(f"**Clan Joined Date:** <t:{clan_joined_date}:D>")

        embed.add_field(
            name="Details", value="\n".join(field_value_lines) or "None", inline=False
        )

    # ╔═══════════════════════════════╗
    #   CASE 2: Member exists → UPDATE
    # ╚═══════════════════════════════╝
    else:
        success = await update_member_fields(
            bot,
            user=member,
            channel_id=channel_id,
            perks=perks,
            faction=faction,
            pokemeow_name=pokemeow_name,
            clan_joined_date=clan_joined_date,
        )
        if not success:
            await loader.error(
                f"Failed to update {member.display_name} in the database."
            )
            return

        embed.title = "✅ Member Information Updated"

        # Extract old values
        old_pname = old.get("pokemeow_name")
        old_channel = old.get("channel_id")
        old_perks = old.get("perks")
        old_faction = old.get("faction")
        old_join = old.get("clan_joined_date")

        # Show ONLY fields the user manually provided
        # AND only show changed values (otherwise "no change")
        field_value_lines = []

        if pokemeow_name is not None:
            if pokemeow_name != old_pname:
                field_value_lines.append(
                    f"**PokéMeow Name:** {old_pname or 'N/A'} ➔ {pokemeow_name}"
                )
            else:
                field_value_lines.append(
                    f"**PokéMeow Name:** {pokemeow_name} "
                )

        if channel_id is not None:
            old_mention = f"<#{old_channel}>" if old_channel else "N/A"
            if channel_id != old_channel:
                field_value_lines.append(
                    f"**Channel:** {old_mention} ➔ <#{channel_id}>"
                )
            else:
                field_value_lines.append(f"**Channel:** <#{channel_id}> ")

        if perks is not None:
            if perks != old_perks:
                field_value_lines.append(f"**Perks:** {old_perks} ➔ {perks}")
            else:
                field_value_lines.append(f"**Perks:** {perks} ")

        if faction is not None:
            if faction != old_faction:
                field_value_lines.append(f"**Faction:** {old_faction} ➔ {faction}")
            else:
                field_value_lines.append(f"**Faction:** {faction} ")

        if clan_joined_date is not None:
            if clan_joined_date != old_join:
                old_date = f"<t:{old_join}:D>" if isinstance(old_join, int) else "N/A"
                field_value_lines.append(
                    f"**Clan Joined Date:** {old_date} ➔ <t:{clan_joined_date}:D>"
                )
            else:
                field_value_lines.append(
                    f"**Clan Joined Date:** <t:{clan_joined_date}:D> "
                )

        embed.add_field(
            name="Details", value="\n".join(field_value_lines), inline=False
        )

    # Finalize
    await loader.success(embed=embed, content="")
    pretty_log(
        "success",
        f"Updated member {member.display_name} ({member.id}) information successfully.",
    )

    # Send webhook log
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.member_logs)
    if log_channel:
        await send_webhook(bot=bot, channel=log_channel, embed=embed)
