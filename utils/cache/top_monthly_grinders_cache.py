import discord
from utils.logs.pretty_log import pretty_log
from utils.cache.cache_list import top_monthly_grinders_cache
from utils.db.top_monthly_grinders_db import fetch_all_top_monthly_grinders

async def load_top_monthly_grinders_cache(bot):
    """
    Load all top_monthly_grinders from the database into the cache.
    """
    top_monthly_grinders_cache.clear()
    try:
        grinders = await fetch_all_top_monthly_grinders(bot)
        if grinders:
            for grinder in grinders:
                user_id = grinder["user_id"]
                top_monthly_grinders_cache[user_id] = {
                    "user_name": grinder["user_name"],
                }
            pretty_log(
                "cache", f"Loaded {len(top_monthly_grinders_cache)} top_monthly_grinders into cache."
            )
        elif not grinders:
            pretty_log("cache", "No top_monthly_grinders found to load into cache.")

    except Exception as e:
        pretty_log("error", f"Error loading top_monthly_grinders cache: {e}")

    return top_monthly_grinders_cache

def upsert_top_monthly_grinder_cache(
    user_id: int,
    user_name: str,
):
    """
    Upsert a top_monthly_grinder into the cache.
    """
    top_monthly_grinders_cache[user_id] = {
        "user_name": user_name,
    }
    pretty_log("cache", f"Upserted top_monthly_grinder {user_name} ({user_id}) into cache.")


def remove_top_monthly_grinder_cache(user_id: int):
    """
    Remove a top_monthly_grinder from the cache.
    """
    if user_id in top_monthly_grinders_cache:
        del top_monthly_grinders_cache[user_id]
        pretty_log("cache", f"Removed top_monthly_grinder ({user_id}) from cache.")