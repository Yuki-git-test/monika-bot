import discord
from utils.logs.pretty_log import pretty_log
from utils.db.channel_placement_db import fetch_all_channel_placements
from utils.cache.cache_list import channel_placement_cache


async def load_channel_placement_cache(bot):
    """Load the channel placement cache from the database."""
    # Clear existing cache
    channel_placement_cache.clear()

    # Fetch all channel placements from the database
    try:
        placements = await fetch_all_channel_placements(bot)
        if placements is None:
            pretty_log(
                "cache",
                "No channel placements fetched from database to load into channel placement cache.",
            )
            return
    except Exception as e:
        pretty_log(
            "error",
            f"Error fetching channel placements from database to load into channel placement cache: {e}",
        )
        return

    try:
        for placement in placements:
            channel_id = placement["channel_id"]
            channel_placement_cache[channel_id] = {
                "user_id": placement["user_id"],
                "user_name": placement["user_name"],
                "catches": placement["catches"],
            }
        pretty_log(
            "cache",
            f"Channel placement cache loaded with {len(channel_placement_cache)} placements.",
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Error loading channel placement cache: {e}",
        )


def check_if_placement_changed(old_placement: dict, new_placement: dict) -> bool:
    """Check if the channel placement has changed."""
    for key in new_placement:
        if key not in old_placement or old_placement[key] != new_placement[key]:
            return True
    return False


def sort_channel_placement_cache_by_catches():
    """Sort the channel placement cache by catches in descending order."""
    sorted_cache = dict(
        sorted(
            channel_placement_cache.items(),
            key=lambda item: item[1]["catches"],
            reverse=True,
        )
    )
    channel_placement_cache.clear()
    channel_placement_cache.update(sorted_cache)
    pretty_log(
        "cache",
        "Channel placement cache sorted by catches in descending order.",
    )


def upsert_channel_placement_cache(
    channel_id: int,
    user_id: int,
    user_name: str,
    catches: int,
):
    """Upsert a channel placement into the cache."""
    channel_placement_cache[channel_id] = {
        "user_id": user_id,
        "user_name": user_name,
        "catches": catches,
    }
    pretty_log(
        "cache",
        f"Upserted channel placement for user {user_name} (ID: {user_id}) in channel {channel_id} in cache. Catches: {catches}",
    )
    # Sort cache after upsert
    sort_channel_placement_cache_by_catches()


def update_channel_placement_catches_in_cache(channel_id: int, catches: int):
    """Update the catches for a channel placement in the cache."""
    if channel_id in channel_placement_cache:
        user_name = channel_placement_cache[channel_id]["user_name"]
        channel_placement_cache[channel_id]["catches"] = catches
        pretty_log(
            "cache",
            f"Updated catches for user {user_name} in channel {channel_id} in cache to: {catches}",
        )
        # Sort cache after update
        sort_channel_placement_cache_by_catches()


def remove_channel_placement_cache(channel_id: int):
    """Remove a channel placement from the cache."""
    if channel_id in channel_placement_cache:
        user_name = channel_placement_cache[channel_id]["user_name"]
        del channel_placement_cache[channel_id]
        pretty_log(
            "cache",
            f"Removed channel placement for user {user_name} in channel {channel_id} from cache.",
        )
