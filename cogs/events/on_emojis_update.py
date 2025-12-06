from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log


class EmojiEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        # Find created emojis
        before_ids = {e.id for e in before}
        after_ids = {e.id for e in after}
        created = [e for e in after if e.id not in before_ids]
        deleted = [e for e in before if e.id not in after_ids]
        # Find updated emojis (renamed)
        updated = [
            e
            for e in after
            if e.id in before_ids
            and any(e.name != b.name for b in before if b.id == e.id)
        ]

        log_channel = guild.get_channel(
            LOG_CHANNEL_ID
        )  # Replace with your log channel ID
        if not log_channel:
            return

        for emoji in created:
            embed = discord.Embed(
                title="Emoji created",
                description=f"{emoji} {emoji.name}\nEmoji ID: {emoji.id}\nCreated: {datetime.now().strftime('%m/%d/%y, %I:%M %p')}",
                color=discord.Color.green(),
            )
            await log_channel.send(embed=embed)

        for emoji in updated:
            before_emoji = next((b for b in before if b.id == emoji.id), None)
            if before_emoji:
                embed = discord.Embed(
                    title="Emoji renamed",
                    description=f"{before_emoji.name} \u2192 {emoji.name}\nEmoji ID: {emoji.id}\n{datetime.now().strftime('%m/%d/%y, %I:%M %p')}",
                    color=discord.Color.blue(),
                )
                await log_channel.send(embed=embed)

        for emoji in deleted:
            embed = discord.Embed(
                title="Emoji deleted",
                description=f"{emoji.name}\nEmoji ID: {emoji.id}\nDeleted: {datetime.now().strftime('%m/%d/%y, %I:%M %p')}",
                color=discord.Color.red(),
            )
            await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(EmojiEvents(bot))
