from datetime import datetime

import discord
import pytz
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from constants.vn_allstars_constants import (
    DAILY_CATCH_REQUIREMENT,
    MONIKA_APP_ID,
    MONIKA_EMBED_COLOR,
    MONTHLY_CATCH_REQUIREMENT,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.probation_list_db import (
    fetch_all_probation_members,
    update_all_probation_member_catch_requirements,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log


def get_est_day_number():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day  # Returns the day of the month as int


class Probation_Members_Paginator(View):
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
        start_index = self.page * self.per_page
        end_index = start_index + self.per_page
        page_members = self.members[start_index:end_index]

        embed = discord.Embed(
            title=f"⚠️ Probation Members List",
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        guild = self.bot.get_guild(VNA_SERVER_ID)
        double_probation_role = (
            guild.get_role(VN_ALLSTARS_ROLES.kick_list) if guild else None
        )
        embed.set_thumbnail(url=guild.icon.url if guild and guild.icon else None)
        for idx, member_info in enumerate(page_members, start=1):
            member_id = member_info[0]
            member = guild.get_member(member_id) if guild else None
            member_name = (
                member.display_name
                if member
                else member_info[1] if len(member_info) > 1 else "Unknown User"
            )
            catch_requirement = member_info[3] if len(member_info) > 3 else 0
            assigned_on_timestamp = member_info[4] if len(member_info) > 4 else None
            stacking_requirements = (
                int(member_info[6])
                if len(member_info) > 6 and member_info[6] is not None
                else 0
            )
            assigned_on_str = (
                f"**Assigned On:** <t:{assigned_on_timestamp}:D>"
                if assigned_on_timestamp
                else "**Assigned On:** Unknown"
            )
            title_prefix = (
                "🚨 "
                if double_probation_role
                and member
                and double_probation_role in member.roles
                else ""
            )
            if stacking_requirements > 0:
                total_requirement = catch_requirement + stacking_requirements
                catch_req_str = (
                    f"> - **Catch Requirement:** {catch_requirement:,} catches\n"
                    f"> - **Catch Debt:** {stacking_requirements:,} catches\n"
                    f"> - **Total Requirement:** {total_requirement:,} catches\n"
                )
            else:
                catch_req_str = (
                    f"> - **Catch Requirement:** {catch_requirement:,} catches\n"
                )
            embed.add_field(
                name=f"{idx}. {title_prefix}{member_name}",
                value=(
                    f"> - **Mention:** {member.mention if member else 'N/A'}\n"
                    f"{catch_req_str}"
                    f"> - {assigned_on_str}"
                ),
                inline=False,
            )
        embed.set_footer(
            text=f"Page {self.page + 1} of {self.max_page +
    1} | Total Members: {total_members}",
            icon_url=guild.icon.url if guild and guild.icon else None,
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


async def probation_members_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    """Fetch and display a list of all probation members."""
    # Defer
    loader = await pretty_defer(
        interaction=interaction,
        content="Fetching probation members...",
        ephemeral=False,
    )

    # Check if staff member
    if not await is_staff_member(interaction=interaction):
        await loader.error(
            content="You do not have permission to use this command.",
        )
        return

    # Update all probation member catch requirements first
    current_day = get_est_day_number()
    new_catch_requirement = current_day * DAILY_CATCH_REQUIREMENT
    await update_all_probation_member_catch_requirements(
        bot=bot, catch_requirement=new_catch_requirement
    )

    # Fetch probation members
    probation_members = await fetch_all_probation_members(bot)
    if not probation_members:
        await loader.error(
            content="No probation members found.",
        )
        return

    # Sort by amount of catch requirements required
    sorted_members = sorted(
        probation_members,
        key=lambda x: x[3] if x[3] is not None else 1500,  # Treat None as 0
        reverse=True,
    )

    # Create paginator
    paginator = Probation_Members_Paginator(
        bot=bot,
        user=interaction.user,
        members=sorted_members,
        per_page=10,
    )
    embed = await paginator.get_embed()
    sent_message = await loader.success(
        embed=embed,
        view=paginator,
        content="",
    )
    paginator.message = sent_message  # store the message object
