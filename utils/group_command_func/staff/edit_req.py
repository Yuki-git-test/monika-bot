from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.cache.cache_list import probation_list_cache
from utils.db.probation_list_db import update_probation_catch_requirement
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log


async def edit_catch_requirement_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    new_catch_requirement: int,
):
    """Updates the catch requirement for a probation member."""
    loader = await pretty_defer(
        interaction=interaction,
        content="Updating catch requirement...",
        ephemeral=False,
    )

    # Check if staff member
    is_staff = await is_staff_member(interaction)
    if not is_staff:
        await loader.error("You do not have permission to use this command.")
        return

    # Check if member is on probation
    guild = interaction.guild
    probation_role = guild.get_role(VN_ALLSTARS_ROLES.probation)
    if probation_role not in member.roles:
        await loader.error(f"{member.mention} is not on probation.")
        return

    # Update catch requirement in DB and cache
    probation_info = probation_list_cache.get(member.id)
    if not probation_info:
        await loader.error(f"Probation information for {member.mention} not found.")
        return
    old_probation_requirements = probation_info.get("catch_requirement", 0)
    try:
        await update_probation_catch_requirement(bot, member, new_catch_requirement)
        desc = (
            f"**Member:** {member.mention} ({member.id})\n"
            f"**Old Catch Requirement:** {old_probation_requirements}\n"
            f"**New Catch Requirement:** {new_catch_requirement}\n"
            f"**Updated By:** {interaction.user.mention} ({interaction.user.id})"
        )
        embed = discord.Embed(
            title="✅ Catch Requirement Updated",
            description=desc,
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await loader.success(embed=embed)

        # Send webhook notification
        server_log = interaction.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
        if server_log:
            await send_webhook(
                bot,
                server_log,
                embed=embed,
            )
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to update catch requirement for {member} ({member.id}): {e}",
            label="Edit Req Func",
        )
        await loader.error(f"Failed to update catch requirement for {member.mention}.")
        return
