import discord
from discord import app_commands
from discord.ext import commands

from constants.aesthetic import Dividers
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log
from utils.ping_me_roles.general_roles_embed import General_Roles_Button
from utils.ping_me_roles.market_snipe_roles_embed import Market_Snipe_Role_Button
from utils.visuals.colors import get_random_monika_color

EMBED_COLOR = 0xFF9999

TEST_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.khys_chamber
REAL_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.roles
ROLES_CHANNEL_ID = REAL_CHANNEL_ID


class Main_Ping_Me_Roles_Embed_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add General Roles Button
        self.add_item(General_Roles_Button())
        # Add Market Snipe Roles Button
        self.add_item(Market_Snipe_Role_Button())


class Ping_Me_Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Register persistent views for reboot survival
        bot.add_view(Main_Ping_Me_Roles_Embed_View())

    @app_commands.command(
        name="ping-me-roles",
        description="Sends the Ping Me Roles embed to the designated channel.",
    )
    async def ping_me_roles(self, interaction: discord.Interaction):
        """Sends the Ping Me Roles embed to the designated channel."""
        try:
            # Check if user is a staff member
            is_staff = await is_staff_member(interaction)
            if not is_staff:
                await interaction.response.send_message(
                    "You do not have permission to use this command.", ephemeral=True
                )
                return

            guild = interaction.guild
            user = interaction.user

            channel = guild.get_channel(ROLES_CHANNEL_ID)
            if not channel:
                await interaction.response.send_message(
                    "The designated channel was not found.", ephemeral=True
                )
                return

            # Optional: delete previously sent ping me roles embeds by the bot
            async for msg in channel.history(limit=20):
                if msg.author.id == interaction.client.user.id and msg.components:
                    try:
                        await msg.delete()
                        pretty_log(
                            "info",
                            "Deleted old Ping Me Roles embed message.",
                        )
                    except:
                        pass
            title = "VNA Roles"
            desc = (
                "🌸 Role Categories\n\n" "🎀 General Roles\n" "🎯 Market Snipe Roles\n"
            )
            embed = discord.Embed(
                title=title,
                description=desc,
                color=EMBED_COLOR,
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.set_image(url=Dividers.orange_stars)

            await channel.send(embed=embed, view=Main_Ping_Me_Roles_Embed_View())
            await interaction.response.send_message(
                f"Ping Me Roles embed has been sent to {channel.mention}.",
                ephemeral=True,
            )

        except Exception as e:
            pretty_log("error", f"Error in Ping Me Roles command: {e}")
            await interaction.response.send_message(
                "An unexpected error occurred.", ephemeral=True
            )
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping_Me_Roles(bot))
