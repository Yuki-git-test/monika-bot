import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.safe_run_command import run_command_safe
from utils.group_command_func.channel import *
from utils.logs.pretty_log import pretty_log

# 🍭──────────────────────────────
#   🎀 Channel Group Command
# 🍭──────────────────────────────
class ChannelGroupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Register the group command
    channel_group = app_commands.Group(
        name="channel", description="Commands related to personal channels"
    )

    # 🎀────────────────────────────────────────────
    #          🌸 /channel add 🌸
    # 🎀────────────────────────────────────────────
    @channel_group.command(
        name="add",
        description="Add a member to your personal channel",
    )
    @app_commands.describe(
        member="The member to add to your personal channel",
    )
    async def channel_add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ):
        slash_cmd_name = "/channel add"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=channel_add_func,
            member=member,
        )
    channel_add.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #          🌸 /channel remove 🌸
    # 🎀────────────────────────────────────────────
    @channel_group.command(
        name="remove",
        description="Remove a member from your personal channel",
    )
    @app_commands.describe(
        member="The member to remove from your personal channel",
    )
    async def channel_remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ):
        slash_cmd_name = "/channel remove"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=channel_remove_func,
            member=member,
        )
    channel_remove.extras = {"category": "Public"}
    
# 🎀────────────────────────────────────────────
#           🌸 Cog Setup Function 🌸
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelGroupCommand(bot))
