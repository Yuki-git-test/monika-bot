import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.trophy import (
    fetch_all_trophies,
    fetch_user_place_and_trophies,
    get_first_place,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log

from .trophy_update_leaderboard import create_leaderboard_embed

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 trophies View Command Function
# 🍭──────────────────────────────
async def trophies_view_func(
    bot: commands.Bot, interaction: discord.Interaction, member: discord.Member = None
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Check if member field has a value
    if member is not None:
        # Check if staff role is in user's roles
        is_staff = await is_staff_member(interaction=interaction)
        if not is_staff:
            await interaction.response.send_message(
                "Only staff members can view other members' trophies.", ephemeral=True
            )
            return

        target_member = member

        # Initialize loader
        loader = await pretty_defer(
            interaction=interaction,
            content=f"Fetching {target_member.display_name}'s trophies...",
            ephemeral=False,
        )

        target_member_info = await fetch_user_place_and_trophies(bot, target_member)
        if not target_member_info:
            await interaction.response.send_message(
                f"{target_member.display_name} has no trophies record.", ephemeral=True
            )
            return
        target_member_trophies = target_member_info["amount"]
        target_member_rank = target_member_info["rank"]
        first_place_user = await get_first_place(bot)
        if first_place_user and first_place_user["user_id"] == target_member.id:
            crown_emoji = "👑"
        else:
            crown_emoji = ""

        embed = discord.Embed(
            title=f"{crown_emoji} {target_member.display_name}'s trophies",
            description=f"**Rank:**{target_member_rank}\n**Trophies:** 🏆 {target_member_trophies}",
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=target_member.display_name, icon_url=target_member.display_avatar.url
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)
        return

    # If no member specified, show own trophies
    target_member = user
    target_member_trophies_info = await fetch_user_trophies(bot, target_member)
    if not target_member_trophies_info:
        await interaction.response.send_message(
            "You have no trophies record.", ephemeral=True
        )
        return
    target_member_trophies = target_member_trophies_info["amount"]
    first_place_user = await get_first_place(bot)
    if first_place_user and first_place_user["user_id"] == target_member.id:
        crown_emoji = "👑"
    else:
        crown_emoji = ""
    embed = discord.Embed(
        title=f"{crown_emoji} Your trophies",
        description=f"**trophies:** {target_member_trophies}",
        color=discord.Color.blue(),
    )
    embed.set_author(
        name=target_member.display_name, icon_url=target_member.display_avatar.url
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)


# 🍭──────────────────────────────
#   🎀 View Leaderboard
# 🍭──────────────────────────────
async def view_leaderboard_func(bot: commands.Bot, interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching the trophy leaderboard...",
        ephemeral=False,
    )

    embed = await create_leaderboard_embed(bot, guild, user)
    await loader.success(embed=embed, content="")
