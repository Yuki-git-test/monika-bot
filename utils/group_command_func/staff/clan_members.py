from datetime import datetime

import discord
from discord.ext import commands
from discord.ui import Button, View

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


class Clan_Members_Paginator(View):
    def __init__(self, bot, user: discord.Member, members, per_page=10):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.members = members
        self.per_page = per_page
        self.per_page = per_page
        self.page = 0
        self.max_page = (len(members) - 1) // per_page
        self.message = None  # store the message object

        # If there's only one page, remove buttons
        if self.max_page == 0:
            self.clear_items()

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
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

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
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
        start = self.page * self.per_page
        end = start + self.per_page
        page_members = self.members[start:end]

        embed = discord.Embed(
            title="📜 VNA Clan Members",
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        guild: discord.Guild = self.bot.get_guild(VNA_SERVER_ID)
        for member in page_members:
            member_id = member.get("user_id")
            discord_member = guild.get_member(member_id)
            if not discord_member:
                continue
            member_name = member.get("user_name", "Unknown")
            pokemeow_name = member.get("pokemeow_name", "Unknown")
            perks = member.get("perks", "None")
            channel_id = member.get("channel_id")
            channel_mention = f"<#{channel_id}>" if channel_id else "No channel set"
            faction = member.get("faction", "None")
            clan_joined_date = member.get("clan_joined_date", "Unknown")
            joined_date_str = "N/A"
            if clan_joined_date:
                joined_date_str= f"<t:{clan_joined_date}:D>"
            embed.add_field(
                name=f"👤 {member_name}",
                value=(
                    f"**Discord Member:** {discord_member.mention}\n"
                    f"**Channel:** {channel_mention}\n"
                    f"**PokéMeow Name:** {pokemeow_name}\n"
                    f"**Perks:** {perks.title()}\n"
                    f"**Faction:** {faction.title()}\n"
                    f"**Joined Date:** {joined_date_str}"
                ),
                inline=False,
            )
        embed.set_footer(
            text=f"Page {self.page + 1} of {self.max_page + 1}",
            icon_url=guild.icon.url if guild.icon else None,
        )
        return embed

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass  # Message was deleted, nothing to do


async def clan_members_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    """List all members of the VNA Clan."""

    # Check if user is a staff member
    user = interaction.user
    is_staff = await is_staff_member(interaction=interaction)
    if not is_staff:
        await interaction.response.send_message(
            "Only staff members can view clan members.", ephemeral=True
        )
        return
    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching VNA Clan members...",
        ephemeral=False,
    )

    # Fetch all VNA members from the database
    try:
        members = await fetch_all_members(bot)
        if not members:
            await loader.error(content="No VNA Clan members found in the database.")
            return
        # Create and send the paginator
        paginator = Clan_Members_Paginator(bot, user, members, per_page=10)
        embed = await paginator.get_embed()
        sent_message = await loader.success(embed=embed, view=paginator, content="")
        paginator.message = sent_message  # store the message object

    except Exception as e:
        pretty_log(
            message=f"Failed to fetch VNA members from database: {e}",
            tag="error",
            label="Clan Members Fetch Error",
        )
        await loader.error(
            content="Failed to fetch VNA Clan members from the database."
        )
        return
