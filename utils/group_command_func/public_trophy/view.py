from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from constants.aesthetic import Thumbnails
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_EMBED_COLOR,
    VNA_SERVER_ID,
)
from utils.db.public_trophy_db import (
    fetch_all_public_trophies,
    fetch_current_public_leaderboard_info,
    fetch_user_place_and_public_trophies,
    get_public_first_place,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log

from .trophy_update_leaderboard import create_public_leaderboard_embed

TROPHY_THUMBNAIL_URL = Thumbnails.trophy

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


# 🍭──────────────────────────────
#   🎀 trophies View Command Function
# 🍭──────────────────────────────
async def public_trophies_view_func(
    bot: commands.Bot, interaction: discord.Interaction, member: discord.Member = None
):
    guild = interaction.guild
    user = interaction.user
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Fetching public trophies...",
        ephemeral=False,
    )

    # Check if member field has a value
    if member is not None:
        # Check if staff role is in user's roles
        is_staff = await is_staff_member(interaction=interaction)
        if not is_staff:
            await loader.error(
                f"{user.mention}, you do not have permission to view other members' trophies."
            )
            return

        target_member = member

        target_member_info = await fetch_user_place_and_public_trophies(
            bot, target_member
        )
        if not target_member_info:
            await loader.error(
                f"{target_member.display_name} has no public trophies record."
            )
            return
        target_member_trophies = target_member_info["amount"]
        target_member_rank = target_member_info["place"]
        first_place_user = await get_public_first_place(bot)
        if first_place_user and first_place_user["user_id"] == target_member.id:
            crown_emoji = "👑"
        else:
            crown_emoji = ""

        embed = discord.Embed(
            title=f"{crown_emoji} {target_member.display_name}'s Public trophies",
            description=f"**Rank:**{target_member_rank}\n**Trophies:** 🏆 {target_member_trophies}",
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=target_member.display_name, icon_url=target_member.display_avatar.url
        )
        embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
        await loader.success(embed=embed, content="")
        return

    # If no member specified, show own trophies
    target_member = user
    target_member_trophies_info = await fetch_user_place_and_public_trophies(
        bot, target_member
    )
    if not target_member_trophies_info:
        await loader.error("No trophies record found for user.")
        return
    target_member_trophies = target_member_trophies_info["amount"]
    target_member_rank = target_member_trophies_info["place"]

    first_place_user = await get_public_first_place(bot)
    if first_place_user and first_place_user["user_id"] == target_member.id:
        crown_emoji = "👑"
    else:
        crown_emoji = ""
    embed = discord.Embed(
        title=f"{crown_emoji} Your Trophies",
        description=f"**Rank:**{target_member_rank}\n**Trophies:** 🏆 {target_member_trophies}",
        color=MONIKA_EMBED_COLOR,
    )
    embed.set_author(
        name=target_member.display_name, icon_url=target_member.display_avatar.url
    )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    await loader.success(embed=embed, content="")


# 🍭──────────────────────────────
#   🎀 Trophy Leaderboard Paginator View
# 🍭──────────────────────────────
class Trophy_Leaderboard_Paginator(View):
    def __init__(self, bot, user: discord.Member, trophy_members, per_page=25):
        super().__init__(timeout=120)
        self.bot = bot
        self.user = user
        self.trophy_members = trophy_members
        self.per_page = per_page
        self.page = 0
        self.max_page = (len(trophy_members) - 1) // per_page
        self.message = None  # store the message object

        # If there's only one page, remove buttons
        if self.max_page == 0:
            self.clear_items()

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You cannot interact with this paginator.", ephemeral=True
            )
            return
        if self.page > 0:
            self.page -= 1
            embed = await self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You cannot interact with this paginator.", ephemeral=True
            )
            return
        if self.page < self.max_page:
            self.page += 1
            embed = await self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    async def get_embed(self):
        total_trophy_members = len(self.trophy_members)
        start = self.page * self.per_page
        end = start + self.per_page
        page_trophy_members = self.trophy_members[start:end]
        guild: discord.Guild = self.bot.get_guild(VNA_SERVER_ID)

        first_place_user_id = None
        current_leaderboard_info = await fetch_current_public_leaderboard_info(self.bot)
        first_place_user_id = (
            current_leaderboard_info.get("first_place_id")
            if current_leaderboard_info
            else None
        )
        # Get user place info
        user_place_info = await fetch_user_place_and_public_trophies(
            self.bot, self.user
        )
        if not user_place_info or user_place_info["amount"] == 0:
            desc = "You have no trophies yet."
        else:
            desc = f"You are currently in #{user_place_info['place']} with \U0001f3c6 {user_place_info['amount']}"
        embed = discord.Embed(
            title=f"🏆 {guild.name} Public Trophy Leaderboard",
            description=desc,
            color=VNA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        for index, trophy_info in enumerate(page_trophy_members, start=start + 1):
            user_id = trophy_info["user_id"]
            amount = trophy_info["amount"]
            user = guild.get_member(user_id)
            if not user:
                continue
            if user_id == first_place_user_id:
                crown_emoji = "👑 "
            else:
                crown_emoji = ""
            embed.add_field(
                name=f"{index}. {crown_emoji}{user.display_name}",
                value=f"> - 🏆 {amount}",
                inline=False,
            )

        embed.set_footer(
            text=f"Page {self.page + 1} of {self.max_page + 1} | Total Members: {total_trophy_members}",
            icon_url=guild.icon.url if guild.icon else None,
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        return embed

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception as e:
                pass  # Message was deleted, nothing to do


# 🍭──────────────────────────────
#   🎀 View Leaderboard
# 🍭──────────────────────────────
async def view_public_leaderboard_func(
    bot: commands.Bot, interaction: discord.Interaction
):
    guild = interaction.guild
    user = interaction.user

    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching the trophy leaderboard...",
        ephemeral=False,
    )
    # Fetch member trophies and create embed
    member_trophies = await fetch_all_public_trophies(bot=bot)
    if not member_trophies:
        await loader.error("No trophies have been awarded yet.")
        return
    sorted_trophies = sorted(member_trophies, key=lambda x: x["amount"], reverse=True)
    paginator = Trophy_Leaderboard_Paginator(
        bot=bot, user=user, trophy_members=sorted_trophies
    )
    embed = await paginator.get_embed()
    sent_msg = await loader.success(embed=embed, content="", view=paginator)
    paginator.message = sent_msg
