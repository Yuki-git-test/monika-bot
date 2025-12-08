from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
)
from utils.cache.cache_list import probation_list_cache, vna_members_cache
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_clan_member
from utils.logs.pretty_log import pretty_log


class CatchRequirements(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="catch-requirements",
        description="Shows your catch requirements if you are on probation.",
    )
    async def catch_requirements(self, interaction: discord.Interaction):
        """Shows a user's catch requirements"""
        # Defer response
        loader = await pretty_defer(
            interaction=interaction,
            content="Checking catch requirements...",
            ephemeral=False,
        )

        seafoam_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.seafoam)
        if (
            not is_clan_member(interaction)
            and seafoam_role not in interaction.user.roles
        ):
            await loader.error("You must be a clan member to use this command.")
            return

        probation_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.probation)

        if probation_role not in interaction.user.roles:
            await loader.error("You are not currently on probation.")
            return

        # Get member info
        member_info = vna_members_cache.get(interaction.user.id)
        if not member_info:
            await loader.error("Member information not found in VNA members cache.")
            pretty_log(
                "error",
                f"Member {interaction.user.display_name} not found in VNA members cache.",
                label="Catch Requirements Command",
            )
            return

        probation_member_info = probation_list_cache.get(interaction.user.id)
        if not probation_member_info:
            await loader.error("Probation information not found.")
            pretty_log(
                "error",
                f"Probation info for member {interaction.user.display_name} not found in probation cache.",
                label="Catch Requirements Command",
            )
            return
        catch_requirement = probation_member_info.get("catch_requirement", 1500)

        # Create embed
        desc = (
            f"**Catch Requirement:** {catch_requirement} catches\n\n"
            f"To remove your probation role, you need to meet or exceed the catch requirement then do `;clan stats m` or contact a staff member.\n"
        )
        embed = discord.Embed(
            title="\U0001f4d6 Catch Requirements",
            color=MONIKA_EMBED_COLOR,
            description=desc,
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )

        await loader.success(embed=embed, content="")

    catch_requirements.extras = {"category": "Public"}

async def setup(bot: commands.Bot):
    await bot.add_cog(CatchRequirements(bot))
