from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.message_logs
DELETED_IMAGE_THREAD_ID = 1442024624803287180
from utils.functions.webhook_func import send_webhook

# 🍭──────────────────────────────
#   🎀 Event: On Message Delete
# 🍭──────────────────────────────
class OnMessageDeleteCog(commands.Cog):
    """Cog to handle message deletion events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Handle message deletion events."""
        guild = message.guild
        if not guild or guild.id != VNA_SERVER_ID:
            return

        pretty_log(
            "info",
            f"Message deleted in {guild.name} by {message.author} in #{message.channel}: {message.content}",
        )


        # Get media attachments
        media_attachments = [
            att
            for att in message.attachments
            if att.content_type and att.content_type.startswith(("image/", "video/"))
        ]

        pretty_log(
            "info",
            f"Found {len(media_attachments)} media attachments in the deleted message.",
        )
        # Embed for one image/video attachment
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            pretty_log(
                "error",
                "Log channel not found.",
            )
            return

        pretty_log(
            "info",
            f"Logging deleted message attachments to channel ID {LOG_CHANNEL_ID}.",
        )
        if len(media_attachments) == 0:

            embed = discord.Embed(
                title="🗑️ Message Deleted",
                color=discord.Color.red(),
                description=(
                    f"**Member:** {message.author.mention}\n"
                    f"**Channel:** {message.channel.mention}\n"
                ),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="Message Content",
                value=message.content or "[No text]",
                inline=False,
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )
            embed.set_footer(
                text=f"Message ID: {message.id}",
                icon_url=message.guild.icon.url if message.guild.icon else None,
            )
            await send_webhook(
                bot=self.bot,
                channel=log_channel,
                embed=embed,
            )
        elif len(media_attachments) == 1:
            try:
                pretty_log(
                    "info",
                    "Processing single attachment in deleted message.",
                )
                attachment = media_attachments[0]
                content = ""
                if message.content:
                    content = f"**Content:** {message.content}\n"
                # Send the attachment in the private thread for deleted images/videos
                thread = discord.utils.get(guild.threads, id=DELETED_IMAGE_THREAD_ID)
                if not thread:
                    try:
                        thread = await guild.fetch_channel(DELETED_IMAGE_THREAD_ID)
                    except Exception as e:
                        pretty_log(
                            "error",
                            f"Deleted image thread channel not found or could not be fetched: {e}",
                        )
                        return
                pretty_log(
                    "info",
                    f"Sending deleted attachment to thread ID {DELETED_IMAGE_THREAD_ID}.",
                )
                try:
                    media_file = await attachment.to_file()
                    media_msg = await thread.send(file=media_file)
                except Exception as e:
                    pretty_log(
                        "error",
                        f"Failed to send attachment to deleted image thread: {e}",
                    )
                    return
                # Get url from media_msg
                media_url = media_msg.attachments[0].url
                # If the attachment is an image , set it as the embed image
                if attachment.content_type.startswith("image/"):
                    embed = discord.Embed(
                        title="🗑️ Image Deleted",
                        color=discord.Color.red(),
                        description=(
                            f"{content}"
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Deleted At:** <t:{int(datetime.now().timestamp())}:D>"
                        ),
                        timestamp=datetime.now(),
                    )
                    embed.set_image(url=media_url)
                    embed.set_author(
                        name=message.author.display_name,
                        icon_url=message.author.display_avatar.url,
                    )
                elif attachment.content_type.startswith("video/"):
                    embed = discord.Embed(
                        title="🗑️ Video Deleted",
                        color=discord.Color.red(),
                        description=(
                            f"{content}"
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Deleted At:** <t:{int(datetime.now().timestamp())}:D>"
                        ),
                        timestamp=datetime.now(),
                    )
                    embed.add_field(name="Video URL", value=media_url, inline=False)
                    embed.set_author(
                        name=message.author.display_name,
                        icon_url=message.author.display_avatar.url,
                    )
                    embed.set_footer(
                        text=f"Message ID: {message.id}",
                        icon_url=message.guild.icon.url if message.guild.icon else None,
                    )
                await send_webhook(
                    bot=self.bot,
                    channel=log_channel,
                    embed=embed,
                )
            except Exception as e:
                pretty_log(
                    "error",
                    f"Failed to log deleted message attachment: {e}",
                )

        elif len(media_attachments) > 1:
            # Message with multiple attachments
            content = ""
            if message.content:
                content = f"**Content:** {message.content}\n"

            files = []
            for a in media_attachments:
                try:
                    files.append(await a.to_file())
                except Exception as e:
                    pretty_log(
                        "error",
                        f"Failed to convert attachment to file: {e}",
                    )
                    pass  # Continue with other attachments
            types = set(
                a.content_type.split("/")[0]
                for a in media_attachments
                if a.content_type
            )
            type_str = (
                "Images and Videos"
                if len(types) > 1
                else ("Images" if "image" in types else "Videos")
            )
            log_text = (
                f"🗑️ **Deleted Message With {type_str}**\n"
                f"**Author:** {message.author.name} (ID: {message.author.id})\n"
                f"**Channel:** {message.channel.mention}\n"
                f"**Message Content:**\n{message.content or '[No text]'}"
            )
            if files:
                await log_channel.send(content=log_text, files=files)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageDeleteCog(bot))
