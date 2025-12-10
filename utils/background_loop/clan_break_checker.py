import discord

from constants.vn_allstars_constants import (
    MONIKA_APP_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.clan_break_members_db import (
    fetch_all_due_clan_break_members,
    remove_clan_break_member,
)
from utils.logs.pretty_log import pretty_log


async def clan_break_checker(bot: discord.Client):
    """Checks for due clan break members and removes their roles."""
    due_members = await fetch_all_due_clan_break_members(bot)
    if not due_members:
        return  # Nothing to process

    guild = bot.get_guild(VNA_SERVER_ID)
    clan_break_role = guild.get_role(VN_ALLSTARS_ROLES.clan_break)
    for member_data in due_members:
        member_id = member_data["user_id"]
        member_name = member_data["user_name"]
        member = guild.get_member(member_id)
        if not member:
            # Remove stale entry from db
            await remove_clan_break_member(bot, member_id)
            pretty_log(
                "info",
                f"Removed stale clan break member entry for {member_name} as they are no longer in the guild.",
                label="Clan Break Checker",
            )
            continue  # Member not found in guild

        if clan_break_role in member.roles:
            # Try to get the user who removed the role from audit logs
            await member.remove_roles(clan_break_role, reason="Clan break period ended")
            pretty_log(
                "info",
                f"Removed Clan Break role from '{member.display_name}' as their break period has ended.",
                label="Clan Break Checker",
            )
