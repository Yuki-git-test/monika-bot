import discord
from discord.ext import commands

from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.stats_parsers import fetch_message_obj_from_link
from utils.listener_func.new_monthly_stats_listener import new_monthly_stats_checker


async def monthly_stats_checker_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    message_link: str,
):
    # Initialize loader
    loader = await pretty_defer(
        interaction=interaction,
        content="Checking Monthly Stats...",
        ephemeral=True,
    )
    # Fetch message object from link
    message, error_message = await fetch_message_obj_from_link(bot, message_link)
    if error_message:
        await loader.error(content=error_message)
        return

    # Pass to the new_monthly_stats_checker function
    await new_monthly_stats_checker(
        bot=bot,
        before_message=message,
        after_message=message,
        command_context="manual_checking",
    )
    await loader.success(content="Weekly stats check completed.")
