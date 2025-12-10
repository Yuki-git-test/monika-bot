from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from constants.vn_allstars_constants import (
    MONIKA_APP_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.clan_break_members_db import fetch_all_clan_break_members
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log


class Clan_Break_Paginator(View):
    def __init__(self, bot, user: discord.Member, members, per_page=10):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.members = members
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
        total_members = len(self.members)
        start = self.page * self.per_page
        end = start + self.per_page
        page_members = self.members[start:end]
        guild = self.bot.get_guild(VNA_SERVER_ID)
        clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)

        embed = discord.Embed(
            title="🛡️ Clan Break Members",
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        for member_info in page_members:
            member_id = member_info["user_id"]
            member_name = member_info["user_name"]
            ends_on = member_info["ends_on"]
            assigned_on = member_info["assigned_on"]
            member = guild.get_member(member_id)
            if member:
                member_str = f"> - {member.mention}"
                ends_on_str = f"> - **Ends On:** <t:{ends_on}:f> in <t:{ends_on}:R>"
                assigned_on_str = f"> - **Assigned On:** <t:{assigned_on}:f>"
                embed.add_field(
                    name=f"👤 {member.display_name}",
                    value=f"{member_str}\n{assigned_on_str}\n{ends_on_str}",
                    inline=False,
                )
        embed.set_footer(
            text=f"Page {self.page + 1} of {self.max_page + 1} | Total Members: {total_members}",
            icon_url=guild.icon.url if guild.icon else None,
        )
        embed.thumbnail(
            url=(
                clan_break_role.icon.url
                if clan_break_role and clan_break_role.icon
                else None
            )
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


async def clan_break_members_func(bot: commands.Bot, interaction: discord.Interaction):
    """Slash command to list all clan break members."""
    # Check if user is staff
    if not await is_staff_member(interaction):
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return
    # Defer
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching clan break members...",
        ephemeral=False,
    )
    clan_break_members = await fetch_all_clan_break_members(bot)
    if not clan_break_members:
        await loader.error("There are currently no members on clan break.")
        return
    try:
        paginator = Clan_Break_Paginator(bot, interaction.user, clan_break_members)
        embed = await paginator.get_embed()
        sent_message = await loader.success(embed=embed, view=paginator, content="")

        paginator.message = sent_message
    except Exception as e:
        await loader.error(f"An error occurred while creating the paginator: {e}")
        pretty_log(
            "error",
            f"Error creating clan break members paginator: {e}",
            label="Clan Break Members Command",
        )
