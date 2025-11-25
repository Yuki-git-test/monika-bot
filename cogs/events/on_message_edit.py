import re

import discord
from discord.ext import commands

from constants.settings import POKEMEOW_APPLICATION_ID
from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.listener_func.clan_remove import (
    handle_clan_kick_command,
    handle_clan_leave_command,
)
from utils.listener_func.perks_listener import (
    extract_perks_from_perk_message,
    extract_perks_from_profile_message,
    update_perks_via_perks_purchase,
)
from utils.logs.pretty_log import pretty_log

TRIGGERS = {
    "pro_embed": "to view badge information",
    "clan_leave": "You left **VN Allstar**.",
    "clan_kick": re.compile(
        r"you spent <:pokecoin:\d+>\s+\*\*100,000\*\*\s+to kick\s+.+?\s+from straymons\.",
        re.IGNORECASE,
    ),
}


# 🍭──────────────────────────────
#   🎀 Event: On Message Edit
# 🍭──────────────────────────────
class OnMessageEditCog(commands.Cog):
    """Cog to handle message edit events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # Only log edits in VNA server
        if not after.guild or after.guild.id != VNA_SERVER_ID:
            return

        # Ignore edits made by bots except PokéMeow
        if after.author.bot and after.author.id != POKEMEOW_APPLICATION_ID:
            return

        content = after.content if after.content else ""
        first_embed = after.embeds[0] if after.embeds else None
        first_embed_author_text = (
            first_embed.author.name if first_embed and first_embed.author else ""
        )
        first_embed_description = first_embed.description if first_embed else ""
        first_embed_footer_text = (
            first_embed.footer.text if first_embed and first_embed.footer else ""
        )
        first_embed_title = first_embed.title if first_embed else ""
        # 🍭──────────────────────────────
        #   🎀 Clan Leave Processing
        # 🍭──────────────────────────────
        if content and TRIGGERS["clan_leave"] in content:
            pretty_log(
                message=f"Detected clan leave message edit for member '{after.author.display_name}'.",
                tag="info",
                label="Clan Leave Command",
            )
            await handle_clan_leave_command(self.bot, after)

        # 🍭──────────────────────────────
        #   🎀 Clan Kick Processing
        # 🍭──────────────────────────────
        if (
            content
            and "You spent <:PokeCoin:666879070650236928> **100,000** to kick"
            in content
            and "from VN Allstar." in content
        ):
            pretty_log(
                message=f"Detected clan kick message edit for member '{after.author.display_name}'.",
                tag="info",
                label="Clan Kick Command",
            )
            await handle_clan_kick_command(self.bot, after)
            # ————————————————————————————————
            # 🎭 Perks Handler
            # ————————————————————————————————
            # ;profile command
            if first_embed:
                if TRIGGERS["pro_embed"] in first_embed_footer_text.lower():
                    await extract_perks_from_profile_message(
                        self.bot,
                        after,
                    )


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))
