from datetime import datetime

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import (
    DAILY_CATCH_REQUIREMENT,
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
)
from utils.cache.cache_list import probation_list_cache, vna_members_cache
from utils.db.probation_list_db import update_all_probation_member_catch_requirements
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_clan_member, is_staff_member
from utils.logs.pretty_log import pretty_log


def get_est_day_number():
    est = pytz.timezone("US/Eastern")
    now_est = datetime.now(est)
    return now_est.day  # Returns the day of the month as int


class CatchRequirements(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="catch-requirements",
        description="Shows your catch requirements if you are on probation.",
    )
    @app_commands.describe(member="The member to check catch requirements for. (Staff only)")
    async def catch_requirements(self, interaction: discord.Interaction, member: discord.Member = None):
        """Shows a user's catch requirements"""
        # Defer response
        loader = await pretty_defer(
            interaction=interaction,
            content="Checking catch requirements...",
            ephemeral=False,
        )
        try:
            seafoam_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.seafoam)
            if (
                not await is_clan_member(interaction)
                and seafoam_role not in interaction.user.roles
            ):
                await loader.error("You must be a clan member to use this command.")
                return
            if member and not await is_staff_member(interaction):
                await loader.error("You do not have permission to check other members' catch requirements.")
                return
            if member:
                target_member = member
            else:
                target_member = interaction.user

            probation_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.probation)

            if probation_role not in target_member.roles:
                if target_member.id == interaction.user.id:
                    error_msg = "You are not currently on probation."
                else:
                    error_msg = f"{target_member.display_name} is not currently on probation."

                await loader.error(content=error_msg)
                return

            # Update all probation member catch requirements first
            current_day = get_est_day_number()
            new_catch_requirement = current_day * DAILY_CATCH_REQUIREMENT
            await update_all_probation_member_catch_requirements(
                bot=self.bot, catch_requirement=new_catch_requirement
            )

            # Get member info
            member_info = vna_members_cache.get(target_member.id)
            if not member_info:
                await loader.error("Member information not found in VNA members cache.")
                pretty_log(
                    "error",
                    f"Member {target_member.display_name} not found in VNA members cache.",
                    label="Catch Requirements Command",
                )
                return

            probation_member_info = probation_list_cache.get(target_member.id)
            if not probation_member_info:
                await loader.error("Probation information not found.")
                pretty_log(
                    "error",
                    f"Probation info for member {target_member.display_name} not found in probation cache.",
                    label="Catch Requirements Command",
                )
                return
            catch_requirement = probation_member_info.get("catch_requirement", 1500)
            stacking_requirements = probation_member_info.get(
                "stacking_requirements", 0
            )
            catch_req_str = (
                f"- **Catch Requirement:** {catch_requirement:,} catches\n\n"
            )
            if stacking_requirements and stacking_requirements > 0:
                total_requirement = catch_requirement + stacking_requirements
                catch_req_str = (
                    f"- **Catch Requirement:** {catch_requirement:,} catches\n"
                    f"- **Catch Debt:** {stacking_requirements:,} catches\n"
                    f"- **Total Requirement:** {total_requirement:,} catches\n\n"
                )

            # Create embed
            desc = (
                f"{catch_req_str}"
                f"Notes:\n"
                f"> - Daily Requirement: {DAILY_CATCH_REQUIREMENT:,} catches\n"
                f"> - Current Day of Month (EST): {current_day}\n"
                f"> - To remove your probation role, you need to meet or exceed the catch requirement then do `;clan stats m` or contact a staff member.\n"
            )
            embed = discord.Embed(
                title="\U0001f4d6 Catch Requirements",
                color=MONIKA_EMBED_COLOR,
                description=desc,
                timestamp=datetime.now(),
            )
            embed.set_thumbnail(url=target_member.display_avatar.url)
            embed.set_author(
                name=target_member.display_name,
                icon_url=target_member.display_avatar.url,
            )

            await loader.success(embed=embed, content="")
        except Exception as e:
            await loader.error(
                "An error occurred while fetching your catch requirements."
            )
            pretty_log(
                "error",
                f"Error in catch requirements command for user {target_member.display_name}: {e}",
                label="Catch Requirements Command",
            )

    catch_requirements.extras = {"category": "Public"}


async def setup(bot: commands.Bot):
    await bot.add_cog(CatchRequirements(bot))
