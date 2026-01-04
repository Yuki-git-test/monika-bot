import discord

from utils.db.monthly_req_db import reset_expected_catches_to_1500
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Monthly Requirements Reset
# 🍭──────────────────────────────
async def monthly_reqs_reset_func(
    bot: discord.Client,
):
    """Reset monthly requirements for all members."""

    await reset_expected_catches_to_1500(bot)
    pretty_log(
            "info",
            "Expected Monthly requirements have been reset to 1500 catches for all members.",
            label="Monthly Reqs Reset",
        )