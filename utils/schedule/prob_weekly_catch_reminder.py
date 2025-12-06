import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Weekly PROB Catch Reminder
# 🍭──────────────────────────────
async def prob_weekly_catch_reminder(bot):
    """Send a reminder in annoucement channel for probation members to catch their required catches."""
    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log(
            "error",
            "PROB Weekly Catch Reminder: VNA server not found.",
        )
        return
    announcement_channel = guild.get_channel(
        VN_ALLSTARS_TEXT_CHANNELS.clan_announcement
    )
    if not announcement_channel:
        pretty_log(
            "error",
            "PROB Weekly Catch Reminder: Announcement channel not found.",
        )
        return
    reminder_message = """<@&1426299800386539521> <@&1445374287098937418> <a:Ppdinkdonk:1388792655147700304>
A gentle reminder to please meet your weekly catch requirement.
You can view your specific requirement anytime using /catch-requirement.

To remove your <@&1426299800386539521>  role, be sure to complete your requirement before the weekly reset.
Failing to do so will add another __**1,500 catches**__ to your requirements, and the <@&1445374287098937418>  role will be applied (if you don’t already have it).

Once you’ve met your required catches, you can automatically remove your Probation role by running `;clan stats m`,
or you may contact a staff member if you need assistance. <:vna_Cute_cap:1380599067217887235>"""

    try:
        await announcement_channel.send(reminder_message)
        pretty_log(
            "info",
            "PROB Weekly Catch Reminder sent successfully.",
        )
    except Exception as e:
        pretty_log(
            "error",
            f"PROB Weekly Catch Reminder: Failed to send message. Error: {e}",
        )
