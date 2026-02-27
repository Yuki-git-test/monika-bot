import re

import discord
from discord.ext import commands

from constants.settings import POKEMEOW_APPLICATION_ID
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.listener_func.clan_command_listener import clan_command_listener
from utils.listener_func.clan_invite import auto_clan_invite
from utils.listener_func.clan_members_listener import clan_members_command_listener
from utils.listener_func.faction_listener import extract_faction_from_faction_command
from utils.listener_func.market_snipe_filter import check_market_buy_command
from utils.listener_func.monthly_stats_listener import monthly_stats_checker
from utils.listener_func.perks_listener import (
    extract_perks_from_perk_message,
    extract_perks_from_profile_message,
    update_perks_via_perks_purchase,
)
from utils.listener_func.pokemeow_username_listener import (
    update_pokemeow_username_by_command,
)
from utils.listener_func.stats_listener import stats_command_handler
from utils.listener_func.top_grinder_listener import assign_top_grinder_roles_listener
from utils.listener_func.weekly_stats_listener import weekly_stats_checker
from utils.logs.pretty_log import pretty_log
from utils.monika_library.monika_lib_ar import monika_lib_ar_handler
from utils.quick_codes.cleanup import clean_graveyard_channels_func
from utils.quick_codes.quick_codes_handler import quick_codes_handler
from utils.quick_codes.sync_members import sync_members_func
from utils.sticky_msg.clan_break import clan_break_sticky_msg
from utils.listener_func.new_monthly_stats_listener import new_monthly_stats_checker

dot_role_id = 1375712535512354898

FACTIONS = ["aqua", "flare", "galactic", "magma", "plasma", "rocket", "skull", "yell"]
TRIGGERS = {
    "pokemeow_name_update": "You spent <:PokeCoin:666879070650236928> **100,000** to change your username to",
    "pro_embed": "to view badge information",
    "perks_embed": "perks",
    "perks_purchase": re.compile(
        r"<a?:[a-zA-Z]+:\d+>\s+Successfully purchased the\s+<a?:[a-zA-Z]+:\d+>\s+\*\*(Bronze|Silver|Gold|Diamond|Amethyst|Onyx)\*\*\s+perks",
        re.IGNORECASE,
    ),
    "monthly_stats_checker": "**Clan Monthly Stats — VN Allstar**",
    "weekly_stats_checker": "**Clan Weekly Stats — VN Allstar**",
    "clan_stats": "Welcome to **VN Allstar**!",
    "clan_member": "Clan Member Information - VN Allstar",
}


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
                content = message.content
                first_embed = message.embeds[0] if message.embeds else None
                first_embed_author_text = (
                    first_embed.author.name
                    if first_embed and first_embed.author
                    else ""
                )
                first_embed_description = first_embed.description if first_embed else ""
                first_embed_footer_text = (
                    first_embed.footer.text
                    if first_embed and first_embed.footer
                    else ""
                )
                first_embed_title = first_embed.title if first_embed else ""
                # 🍭──────────────────────────────
                #   🛡️ Clan Break Sticky Message Handler
                # 🍭──────────────────────────────
                if message.channel.id == VN_ALLSTARS_TEXT_CHANNELS.clan_break:
                    await clan_break_sticky_msg(message)

                # 🍭──────────────────────────────
                #   🎀 Auto Clan Invite Processing
                # 🍭──────────────────────────────
                if (
                    ":tada: Welcome," in message.content
                    and "You have successfully joined" in message.content
                    and "VN Allstar" in message.content
                ):
                    pretty_log(
                        message=f"Detected clan invite message edit for member '{message.author.display_name}'.",
                        tag="info",
                        label="Clan Invite Command",
                    )
                    await auto_clan_invite(self.bot, message)
                # ————————————————————————————————
                # 🔄 Quick Code Handler
                # ————————————————————————————————
                if message.content.startswith("!"):
                    await quick_codes_handler(self.bot, message)

                # ————————————————————————————————
                # 🎭 Perks Handler
                # ————————————————————————————————
                # ;profile command
                if first_embed:
                    if TRIGGERS["pro_embed"] in first_embed_footer_text.lower():
                        await extract_perks_from_profile_message(
                            self.bot,
                            message,
                        )
                # ;perks command
                if first_embed:
                    if TRIGGERS["perks_embed"] in first_embed_author_text.lower():
                        await extract_perks_from_perk_message(
                            self.bot,
                            message,
                        )
                # Perks purchase confirmation
                if content:
                    if re.search(TRIGGERS["perks_purchase"], content):
                        await update_perks_via_perks_purchase(
                            self.bot,
                            message,
                        )

                # ————————————————————————————————
                #  💌 Faction Extraction Logic
                # ————————————————————————————————
                if first_embed:
                    if first_embed.author and any(
                        f in first_embed.author.name.lower() for f in FACTIONS
                    ):
                        await extract_faction_from_faction_command(
                            self.bot,
                            message,
                        )
                # ————————————————————————————————
                #  📝 PokéMeow Username Update Handler
                # ————————————————————————————————
                if content and TRIGGERS["pokemeow_name_update"] in content:
                    await update_pokemeow_username_by_command(
                        self.bot,
                        message,
                    )
                # ————————————————————————————————
                #  🛒 Market Buy Command Filter
                # ————————————————————————————————
                # Only check if message is not from a bot and in snipe channel
                if message.channel.id == VN_ALLSTARS_TEXT_CHANNELS.snipe_channel:
                    if not message.author.bot:
                        await check_market_buy_command(
                            message,
                        )
                """# ————————————————————————————————
                # 🗓️ Weekly Stats Checker Listener
                # ————————————————————————————————
                if first_embed:
                    if (
                        first_embed_title
                        and TRIGGERS["weekly_stats_checker"] in first_embed_title
                    ):
                        pretty_log(
                            "info",
                            "Detected Clan Weekly Stats embed, processing weekly stats...",
                        )
                        await weekly_stats_checker(self.bot, message, message)"""
                # ————————————————————————————————
                # 🗓️ Monthly Stats Checker Listener
                # ————————————————————————————————
                if first_embed:
                    if (
                        first_embed_title
                        and TRIGGERS["monthly_stats_checker"] in first_embed_title
                    ):
                        pretty_log(
                            "info",
                            "Detected Clan Monthly Stats embed, processing monthly stats...",
                        )
                        await new_monthly_stats_checker(self.bot, message, message)
                # ————————————————————————————————
                # 🏆 Top Grinder Roles Assignment Listener
                # ————————————————————————————————
                if message.channel.id == VN_ALLSTARS_TEXT_CHANNELS.clan_stats:
                    if first_embed:
                        if (
                            first_embed_title
                            and TRIGGERS["monthly_stats_checker"] in first_embed_title
                        ):
                            pretty_log(
                                "info",
                                "Detected Clan Monthly Stats embed, assigning Top Grinder roles...",
                            )
                            await assign_top_grinder_roles_listener(
                                self.bot,
                                message,
                            )
                # ————————————————————————————————
                # 📊 Stats Command Handler
                # ————————————————————————————————
                if first_embed:
                    if "Stats" in first_embed_author_text:
                        pretty_log(
                            "info",
                            "Detected Stats embed, processing stats command...",
                        )
                        await stats_command_handler(
                            self.bot,
                            message,
                        )
                # ————————————————————————————————
                # 📂 Clan Command Listener
                # ————————————————————————————————
                if first_embed:
                    if (
                        first_embed_title
                        and TRIGGERS["clan_stats"] in first_embed_title
                    ):
                        pretty_log(
                            "info",
                            "Detected Clan Stats embed, processing clan stats command...",
                        )
                        await clan_command_listener(
                            self.bot,
                            message,
                        )
                # ————————————————————————————————
                # 👥 Clan Members Command Listener
                # ————————————————————————————————
                if first_embed:
                    if (
                        first_embed_description
                        and TRIGGERS["clan_member"] in first_embed_description
                    ):
                        pretty_log(
                            "info",
                            "Detected Clan Member Information embed, processing clan members command...",
                        )
                        await clan_members_command_listener(
                            self.bot,
                            message,
                        )
                """# ————————————————————————————————
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
"""
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
