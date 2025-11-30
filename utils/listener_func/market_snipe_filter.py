import re

import discord

from utils.logs.pretty_log import pretty_log
async def check_market_buy_command(message: discord.Message):
    # Regex for valid buy command patterns
    pattern = r"^;\s*(m|market)\s*(b|buy)\s*\d+(\s*(\d+|all))?$"
    if re.match(pattern, message.content.strip(), re.IGNORECASE):
        return   # Valid command

    # If not valid, delete and warn
    try:
        await message.delete()
        # DM user with the message deleted
        pretty_log(
            "info",
            f"Deleted invalid market buy command from {message.author.display_name}, Content: {message.content} ",
        )
        embed = discord.Embed(
            title="❌ Invalid Snipe Channel Message",
            description=(
                "Your message was deleted because its not a valid market buy command.\n"
                "Please avoid chatting in the snipe channel"
            ),
            color=discord.Color.red(),
        )
        embed.add_field(name="Deleted Message:", value=message.content, inline=False)

        # Send DM to user
        try:
            await message.author.send(embed=embed)
            pretty_log(
                "info",
                f"Sent invalid market buy command DM to {message.author.display_name}",
            )
        except discord.Forbidden:
            pretty_log(
                "warning",
                f"Could not send DM to {message.author.display_name} about invalid market buy command",
            )
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to delete invalid market buy command from {message.author.display_name}: {e}",
        )
