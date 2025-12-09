from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.aesthetic import Thumbnails
from constants.vn_allstars_constants import (
    KHY_USER_ID,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    MONIKA_EMBED_COLOR
)
from utils.db.trophy import (
    update_leaderboard_first_place,
    add_trophies,
    fetch_all_trophies,
    fetch_current_leaderboard_info,
    fetch_user_trophies,
    get_first_place,
    remove_trophies,
    update_trophies,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

from .trophy_update_leaderboard import (
    trophy_update_leaderboard_func,
)

TROPHY_THUMBNAIL_URL = Thumbnails.trophy

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log

# 🍭──────────────────────────────
#   🎀 Trophies Multi Command Function
# 🍭──────────────────────────────
async def trophy_multi_func(
    bot:commands.Bot,
    interaction:discord.Interaction,
    action:str,
    amount:int,
    member1:discord.Member,
    member2:discord.Member = None,
    member3:discord.Member = None,
    member4:discord.Member = None,
    member5:discord.Member = None,
    member6:discord.Member = None,
    member7:discord.Member = None,
    member8:discord.Member = None,
    member9:discord.Member = None,
    member10:discord.Member = None,
):

    guild = interaction.guild
    user = interaction.user

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content=f"{action.capitalize()}ing trophies...",
        ephemeral=False,
    )
    # Check if staff role is in user's roles
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await loader.error("You do not have permission to manage trophies.")
        return

    # Validate amount
    if amount <= 0:
        await loader.error("Invalid amount provided for trophies.")
        return

    # Get list of members
    members = [
        member1,
        member2,
        member3,
        member4,
        member5,
        member6,
        member7,
        member8,
        member9,
        member10,
    ]
    # Get member IDs for logging
    member_ids = [member.id for member in members if member is not None]

    # Fetch all trophies for comparison
    all_trophies = await fetch_all_trophies(bot)
    member_trophy_map = {trophy["user_id"]: trophy["amount"] for trophy in all_trophies}

    processed_members = []
    skipped_members = []
    # Process each member
    for member in members:
        # Check if member has db row
        if member is None:

            continue
        member_info = await fetch_user_trophies(bot, member)
        if not member_info:
            # Skip members without trophy data
            desc_line = f"{member.mention} - {member.display_name} skipped (no trophy data)."
            skipped_members.append(desc_line)
            pretty_log(
                "info",
                f"{user} attempted to {action} trophies to {member}, but they have no trophy data. Skipping.",
            )
            continue

        # Get current trophies
        current_trophies = member_trophy_map.get(member.id, 0)
        if action == "add":
            new_amount = current_trophies + amount
            title = f"🏆 Trophies Added Summary"
            await update_trophies(bot, member, new_amount)
            desc_line = f"{member.mention} - {member.display_name} now has 🏆 {new_amount}."
            processed_members.append(desc_line)
            pretty_log(
                "info",
                f"{user} added {amount} trophies to {member}. New total: {new_amount}",
            )
        elif action == "remove":
            title = f"🏆 Trophies Removed Summary"
            if amount > current_trophies:
                msg = (
                    f"{member.display_name} only has 🏆 {current_trophies}. Skipping removal.",
                )
                desc_line = f"{member.mention} - {member.display_name} skipped (only has {current_trophies} trophies)."
                skipped_members.append(desc_line)
                pretty_log(
                    "info",
                    f"{user} attempted to remove {amount} trophies from {member}, but they only have {current_trophies}. Skipping.",
                )
                continue
            new_amount = current_trophies - amount
            await update_trophies(bot, member, new_amount)
            desc_line = f"{member.mention} - {member.display_name} now has 🏆 {new_amount}."
            processed_members.append(desc_line)

    # Build confirmation embed
    action_str = "Added" if action == "add" else "Removed"
    embed = discord.Embed(
        title=title,
        description=f"**Amount {action_str}:** 🏆 {amount}\n",
        color=MONIKA_EMBED_COLOR,
    )
    if processed_members:
        processed_members_count = len(processed_members)
        embed.add_field(
            name=f"Processed Members ({processed_members_count})",
            value="\n".join(processed_members),
            inline=False,
        )
    if skipped_members:
        skipped_members_count = len(skipped_members)
        embed.add_field(
            name=f"Skipped Members ({skipped_members_count})",
            value="\n".join(skipped_members),
            inline=False,
        )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.set_author(
        name=user.display_name,
        icon_url=user.display_avatar.url,
    )
    await loader.success(embed=embed, content="")

    # Log the action in the log channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )

    # Update the first place first
    await update_leaderboard_first_place(bot)

    # Update the trophy leaderboard
    await trophy_update_leaderboard_func(bot, guild)
