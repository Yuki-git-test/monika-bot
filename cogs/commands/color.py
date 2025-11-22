import asyncio
import base64
from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord.http import Route

from constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.db.custom_roles_db_func import fetch_custom_role_id
from utils.essentials.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log


async def get_gradient_role_colors(bot, guild_id: int, role_id: int):
    url = f"/guilds/{guild_id}/roles/{role_id}"
    try:
        data = await bot.http.request(discord.http.Route("GET", url))
        colors = data.get("colors", {})
        primary = colors.get("primary_color")
        secondary = colors.get("secondary_color")
        return {
            "primary_color": f"#{primary:06x}" if primary is not None else None,
            "secondary_color": f"#{secondary:06x}" if secondary is not None else None,
        }
    except Exception as e:
        pretty_log("error", f"Failed to fetch gradient role colors: {e}")
        return None


class ColorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="color", description="Displays your custom role color."
    )
    async def color(self, interaction: discord.Interaction):
        """Displays your custom role color."""
        guild = interaction.guild
        user = interaction.user

        # Initialize loader
        loader = await pretty_defer(
            interaction=interaction,
            content="Fetching your custom role color...",
            ephemeral=False,
        )

        # Check if user has a custom role
        custom_role_id = await fetch_custom_role_id(self.bot, user)
        if not custom_role_id:
            await loader.error(content="You don't have a custom role.")
            return
        custom_role = guild.get_role(custom_role_id)
        if not custom_role:
            await loader.error(content="Your custom role was not found in the server.")
            return

        # Get primary and secondary color of the custom role from API
        colors = await get_gradient_role_colors(self.bot, guild.id, custom_role.id)
        if not colors:
            await loader.error(content="Failed to fetch your custom role colors.")
            return
        primary_color = colors.get("primary_color")
        secondary_color = colors.get("secondary_color")
        embed = discord.Embed(
            title="🎨 Your Custom Role Colors",
            description=f"**Role:** {custom_role.mention}\n"
            f"**Primary Color:** {primary_color}\n"
            f"**Secondary Color:** {secondary_color}",
            color=int(primary_color[1:], 16) if primary_color else None,
            timestamp=datetime.now(),
        )
        if custom_role.icon:
            embed.set_thumbnail(url=custom_role.icon.url)
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        await loader.success(embed=embed, content="")


async def setup(bot: commands.Bot):
    await bot.add_cog(ColorCog(bot))
