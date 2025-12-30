import discord

from utils.db.monthly_req_db import reset_expected_catches
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Monthly Requirements Reset
# 🍭──────────────────────────────
async def monthly_reqs_reset_func(
    bot: discord.Client,
):
    """Reset monthly requirements for all members."""

    await reset_expected_catches(bot)
    pretty_log(
        "info",
        "Monthly requirements reset successfully.",
        label="Monthly Requirements Reset",
    )
