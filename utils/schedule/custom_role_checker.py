from datetime import datetime

import discord

from constants.vn_allstars_constants import (
    HARMLESS_USER_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.custom_roles_db_func import (
    fetch_all_user_ids_with_roles,
    fetch_custom_role_id_by_user_id,
    remove_role,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

EXEMPTED_ROLE_IDS = [
    967868089070915604,
    866623289010159636,
    1436196961647595531,
    1390883091953750016,
]  # Lalibel Role, Nemesis Role,


# Check if user has special roles
def has_special_role(member: discord.Member) -> bool:
    """
    Checks if a member has any special roles.
    """
    special_role_ids = [
        VN_ALLSTARS_ROLES.staff,
        VN_ALLSTARS_ROLES.seafoam,
        VN_ALLSTARS_ROLES.server_booster,
        VN_ALLSTARS_ROLES.top_monthly_grinder,
        VN_ALLSTARS_ROLES.shiny_donator,
        VN_ALLSTARS_ROLES.legendary_donator,
        VN_ALLSTARS_ROLES.diamond_donator,
        VN_ALLSTARS_ROLES.senior_mod,
    ]
    if any(role.id in special_role_ids for role in member.roles):
        return True
    return False


async def custom_role_checker(bot):
    """Check and remove custom roles from users who no longer qualify."""
    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log(
            "error",
            "Custom Role Checker: VNA server not found.",
        )
        return

    user_ids_with_roles = await fetch_all_user_ids_with_roles(bot)

    for user_id in user_ids_with_roles:
        member = guild.get_member(user_id)
        role_id = await fetch_custom_role_id_by_user_id(bot, user_id)
        if not member:
            # Delete role from guild if user not found
            if role_id:
                role = guild.get_role(role_id)
                if role:
                    try:
                        await role.delete(reason="User not found in guild.")
                        pretty_log(
                            "info",
                            f"Custom Role Checker: Deleted role {role.name} ({role.id}) for user ID {user_id} as user not found in guild.",
                        )
                    except Exception as e:
                        pretty_log(
                            "error",
                            f"Custom Role Checker: Failed to delete role {role.name} ({role.id}) for user ID {user_id}. Error: {e}",
                        )
            continue
        if member.id == HARMLESS_USER_ID:
            continue
        if has_special_role(member):
            continue
        if role_id and role_id in EXEMPTED_ROLE_IDS:
            continue

        # Remove role from user if they no longer qualify
        role = guild.get_role(role_id)
        if role:
            # Delete role from guild
            try:
                role_name = role.name
                await role.delete(reason="User no longer qualifies for custom role.")
                pretty_log(
                    "info",
                    f"Custom Role Checker: Deleted role {role.name} ({role.id}) from user {member.display_name} ({member.id}).",
                )
                # Send log embed to staff log channel
                staff_log_channel = guild.get_channel(
                    VN_ALLSTARS_TEXT_CHANNELS.server_log
                )
                if staff_log_channel:
                    desc = (
                        f"**Member:** {member.mention}\n"
                        f"**Role:** {role_name}\n"
                        f"**Reason:** No longer qualifies for custom role."
                    )
                    embed = discord.Embed(
                        title="Custom Role Deleted",
                        description=desc,
                        color=MONIKA_EMBED_COLOR,
                        timestamp=datetime.now(),
                    )
                    embed.set_author(
                        name=member.display_name,
                        icon_url=member.display_avatar.url,
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)

                    await send_webhook(
                        bot=bot,
                        channel=staff_log_channel,
                        embed=embed,
                    )

            except Exception as e:
                pretty_log(
                    "error",
                    f"Custom Role Checker: Failed to delete role {role.name} ({role.id}) from user {member.display_name} ({member.id}). Error: {e}",
                )
    pretty_log(
        "info",
        "Custom Role Checker: Completed checking custom roles.",
    )