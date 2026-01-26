import discord

from utils.logs.pretty_log import pretty_log

from .clan_break_members_db import remove_clan_break_member
from .kick_list_db import remove_kick_list_member_by_user_id
from .probation_list_db import remove_probation_member_by_user_id
from .trophy import remove_trophy_info_user
from .vna_members_db_func import remove_member_via_user_id


async def db_cleanup_handler(
    bot: discord.Client,
    user_id: int,
):
    await remove_member_via_user_id(bot=bot, user_id=user_id)
    await remove_clan_break_member(bot=bot, user_id=user_id)
    await remove_probation_member_by_user_id(bot=bot, user_id=user_id)
    await remove_trophy_info_user(bot=bot, user_id=user_id)
    await remove_kick_list_member_by_user_id(bot=bot, user_id=user_id)

    pretty_log(
        "info",
        f"Completed DB cleanup for user_id: {user_id}",
        label="DB Cleanup",
    )
