from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.trophy import (
    fetch_all_trophies,
    fetch_current_leaderboard_info,
    fetch_user_trophies,
    get_first_place,
    remove_trophies,
    update_trophies,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log

from .trophy_update_leaderboard import (
    new_first_place_announcement,
    trophy_update_leaderboard_func,
)

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 trophies Remove Command Function
# 🍭──────────────────────────────
async def trophy_remove_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int,
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Check if staff role is in user's roles
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can remove trophies.", ephemeral=True
        )
        return

    # Validate amount
    if amount <= 0:
        await interaction.response.send_message(
            "Amount must be a positive integer.", ephemeral=True
        )
        return
    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Removing the trophies from {member.display_name}...",
        ephemeral=False,
    )
    # Fetch current trophies
    current_trophies_info = await fetch_user_trophies(bot, member)
    current_trophies = current_trophies_info["amount"] if current_trophies_info else 0

    if amount > current_trophies:
        msg = (f"{member.display_name} only has {current_trophies} trophies.",)
        await loader.error(content=msg)
        return

    # Remove trophies from the member
    new_amount = current_trophies - amount
    await update_trophies(bot, member, new_amount)

    # Update the trophy leaderboard
    await trophy_update_leaderboard_func(bot, guild)

    # Build embed
    embed = discord.Embed(
        title="Trophies Removed",
        description=(
            f"Removed 🏆 {amount} from {member.mention}.\n"
            f"New total: {new_amount} trophies."
        ),
        color=discord.Color.red(),
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    await loader.success(embed=embed, content="")

    # Send log embed to log channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title="Trophies Removed",
            description=(
                f"**Member:** {member.mention}\n"
                f"**Amount Removed:** {amount}\n"
                f"**New Total:** {new_amount}\n"
                f"**Removed by:** {user.mention}"
            ),
            color=discord.Color.dark_red(),
            timestamp=datetime.now(),
        )
        log_embed.set_author(
            name=member.display_name, icon_url=member.display_avatar.url
        )
        await log_channel.send(embed=log_embed)

    # Check if there is a new first place
    old_first_place_info = await fetch_current_leaderboard_info(bot)
    old_first_place_id = (
        old_first_place_info.get("first_place_user_id")
        if old_first_place_info
        else None
    )
    current_first_place = await get_first_place(bot)
    if current_first_place:
        current_first_place_id = current_first_place["user_id"]
        current_first_place_trophy = current_first_place["amount"]
        if current_first_place_id != old_first_place_id:
            await new_first_place_announcement(
                bot=bot,
                guild=guild,
                member=guild.get_member(current_first_place_id),
                trophy_amount=current_first_place_trophy,
            )
