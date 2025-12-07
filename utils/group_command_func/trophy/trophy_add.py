import discord
from discord import app_commands
from discord.ext import commands
from utils.essentials.pretty_defer import pretty_defer
from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS, KHY_USER_ID
from utils.db.trophy import (
    add_trophies,
    fetch_all_trophies,
    fetch_current_leaderboard_info,
    fetch_user_trophies,
    get_first_place,
    update_trophies,
)
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log

from .trophy_update_leaderboard import (
    new_first_place_announcement,
    trophy_update_leaderboard_func,
)
from utils.functions.webhook_func import send_webhook
from constants.aesthetic import Thumbnails
TROPHY_THUMBNAIL_URL = Thumbnails.trophy

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 trophies Add Command Function
# 🍭──────────────────────────────
async def trophy_add_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int,
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content="Adding trophies...",
        ephemeral=False,
    )

    # Check if staff role is in user's roles
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await loader.error("You do not have permission to add trophies.")
        return

    # Validate amount
    if amount <= 0:
        await loader.error("Invalid amount provided for trophies addition.")
        return

    # Get current trophies
    current_trophies_info = await fetch_user_trophies(bot, member)
    current_trophies = current_trophies_info["amount"] if current_trophies_info else 0
    new_amount = current_trophies + amount
    # Add trophies to the member
    try:
        await update_trophies(bot, member, new_amount)
        pretty_log(
            "info",
            f"{user} added {amount} trophies to {member}. New total: {new_amount}",
        )
    except Exception as e:
        await loader.error("An error occurred while adding trophies.")
        pretty_log(
            "error",
            f"Error adding trophies: {e}",
        )
        return

    # Update the trophy leaderboard
    await trophy_update_leaderboard_func(bot, guild)

    # Check if the member is now in first place
    new_first_place = False
    first_place_user = await get_first_place(bot)
    if first_place_user and first_place_user["user_id"] == member.id:
        crown_emoji = "👑"
        new_first_place = True
        # Check if this is a new first place
        current_leaderboard_info = await fetch_current_leaderboard_info(bot)
        first_place_user_id = (
            current_leaderboard_info.get("first_place_id")
            if current_leaderboard_info
            else None
        )
        if first_place_user_id != member.id:
            # Announce new first place
            await new_first_place_announcement(
                bot=bot,
                guild=guild,
                member=member,
                trophy_amount=new_amount,
            )
    else:
        crown_emoji = ""

    # Create and send the embed message
    embed = discord.Embed(
        title=f"{crown_emoji} {member.display_name}'s trophies Updated",
        description=f"**Added Trophies:** 🏆 {amount}\n**Total Trophies:**  🏆 {new_amount}",
        color=discord.Color.green(),
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    await loader.success(embed=embed, content="")

    # Log the action in the log channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel and member.id != KHY_USER_ID:
        if new_first_place:
            crown_emoji = "👑"
            pretty_log(
                "info", f"🏆 {member} has taken the lead with {new_amount} trophies!"
            )
        else:
            crown_emoji = ""
        embed = discord.Embed(
            title=f"{crown_emoji} Trophies Added",
            description=f"**Member:** {member.mention}\n**Added By:** {user.mention}\n**Trophies Added:** {amount}\n**Total Trophies:** {new_amount}",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=embed,
        )
        pretty_log(
            "info",
            f"📝 {user} added {amount} trophies to {member}. Total trophies: {new_amount}",
        )
