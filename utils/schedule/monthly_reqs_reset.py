import discord

from utils.functions.monthly_requirements_utils import reset_monthly_requirements
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Monthly Requirements Reset
# 🍭──────────────────────────────
async def monthly_reqs_reset_func(
    bot: discord.Client,
):
    """Reset monthly requirements for all members."""

    reset_monthly_requirements()
    pretty_log(
        "info",
        "Monthly requirements reset successfully.",
        label="Monthly Requirements Reset",
    )
