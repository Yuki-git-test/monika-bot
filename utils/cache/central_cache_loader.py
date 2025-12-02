import discord

from utils.cache.cache_list import vna_members_cache
from utils.logs.pretty_log import pretty_log

from .vna_members_cache import load_vna_members_cache
from .top_monthly_grinders_cache import load_top_monthly_grinders_cache


# Load all caches
async def load_all_caches(bot):
    """
    Load all caches from the database.
    """

    try:
        # Load vna_members cache
        await load_vna_members_cache(bot)

        # Load top_monthly_grinders cache
        await load_top_monthly_grinders_cache(bot)


        pretty_log("cache", "All caches loaded successfully.")
    except Exception as e:
        pretty_log("error", f"Error loading caches: {e}")
