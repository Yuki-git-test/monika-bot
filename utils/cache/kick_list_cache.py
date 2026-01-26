import discord

from utils.cache.cache_list import kick_list_cache
from utils.db.kick_list_db import fetch_all_kick_list_members
from utils.logs.pretty_log import pretty_log


async def load_kick_list_cache(bot):
    """
    Load all kick list members into the kick_list_cache.
    """
    kick_list_cache.clear()
    try:
        kick_list_members = await fetch_all_kick_list_members(bot)
        if not kick_list_members:
            pretty_log(
                "info",
                "No kick list members found to load into cache.",
                label="Kick List Cache",
            )
            return

        for user_id, user_name in kick_list_members:
            kick_list_cache[user_id] = user_name
        pretty_log(
            "info",
            f"Loaded {len(kick_list_cache)} kick list members into cache.",
            label="Kick List Cache",
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Error loading kick list cache: {e}",
            label="Kick List Cache",
        )


def upsert_kick_list_cache(user: discord.Member):
    """
    Upsert a user into the kick_list_cache.
    """
    user_name = user.name
    kick_list_cache[user.id] = user_name
    pretty_log(
        "info",
        f"Upserted kick list cache member: {user_name} ({user.id})",
        label="Kick List Cache",
    )


def remove_kick_list_cache_by_user_id(user_id: int):
    """
    Remove a user from the kick_list_cache by user_id.
    """
    if user_id in kick_list_cache:
        del kick_list_cache[user_id]
        pretty_log(
            "info",
            f"Removed kick list cache member by user_id: ({user_id})",
            label="Kick List Cache",
        )


def remove_kick_list_cache(user: discord.Member):
    """
    Remove a user from the kick_list_cache.
    """
    if user.id in kick_list_cache:
        del kick_list_cache[user.id]
        pretty_log(
            "info",
            f"Removed kick list cache member: {user} ({user.id})",
            label="Kick List Cache",
        )
