import discord
from discord.ext import commands

from constants.settings import POKEMEOW_APPLICATION_ID
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

from utils.monika_library.monika_lib_ar import monika_lib_ar_handler

dot_role_id = 1375712535512354898


# 🐾────────────────────────────────────────────
#        🌸 Message Create Listener Cog
# 🐾────────────────────────────────────────────
class MessageCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🦋────────────────────────────────────────────
    #           👂 Message Listener Event
    # 🦋────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            # 🚫 Ignore all bots except PokéMeow to prevent loops
            if (
                message.author.bot
                and message.author.id != POKEMEOW_APPLICATION_ID
                and not message.webhook_id
            ):
                return

            # ————————————————————————————————
            # 🏰 Guild Check — Route by server
            # ————————————————————————————————
            guild = message.guild
            if not guild:
                return  # Skip DMs

            # ————————————————————————————————
            # 🩵 VNA message logic
            # ————————————————————————————————
            if guild.id == VNA_SERVER_ID:

                # ————————————————————————————————
                # 📖 Monika Library AR Handler
                # ————————————————————————————————
                # Roles
                member_role = guild.get_role(VN_ALLSTARS_ROLES._server_members)
                staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
                dot_role = guild.get_role(dot_role_id)

                # Channels
                library_channel = guild.get_channel(
                    VN_ALLSTARS_TEXT_CHANNELS.library_working_in_progress
                )
                bot_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.poké_spam)

                message_content = message.content.lower() if message.content else None
                if message_content and message.author != self.bot.user:
                    if message_content.startswith("!"):
                        if member_role in message.author.roles and (
                            message.channel == library_channel
                            or message.channel == bot_channel
                        ):
                            await monika_lib_ar_handler(message)
                        elif (
                            staff_role in message.author.roles
                            or dot_role in message.author.roles
                        ):
                            await monika_lib_ar_handler(message)

        except Exception as e:
            # 🛑────────────────────────────────────────────
            #        Unhandled on_message Error Handler
            # 🛑────────────────────────────────────────────
            pretty_log(
                "critical",
                f"Unhandled exception in on_message: {e}",
                label="MESSAGE",
                bot=self.bot,
                include_trace=True,
            )


# 🌈────────────────────────────────────────────
#        🛠️ Setup function to add cog to bot
# 🌈────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))
