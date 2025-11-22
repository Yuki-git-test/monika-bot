import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log


class EchoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="echo", description="Echo a message to a specified channel."
    )
    @app_commands.describe(
        message="The message to echo",
        channel="The channel to send the message to",
        member="Optionally mention a member",
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel,
        member: discord.Member = None,
    ):
        """Echo a message to a specified channel, optionally mentioning a member."""
        is_staff = await is_staff_member(interaction=interaction)
        if not is_staff:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        if member:
            content = f"{member.mention} {message}"
        else:
            content = message

        await channel.send(content)
        pretty_log(
            "info",
            f"Echoed message to {channel.mention} by {interaction.user} ({interaction.user.id})",
            label="Echo Command",
        )

        await interaction.response.send_message(
            f"Message echoed to {channel.mention}.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(EchoCog(bot))
