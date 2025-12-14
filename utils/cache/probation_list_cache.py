import discord

from utils.cache.cache_list import probation_list_cache
from utils.db.probation_list_db import fetch_all_probation_members
from utils.logs.pretty_log import pretty_log


async def load_probation_list_cache(bot):
    """
    Load all probation list members into the probation_list_cache.
    """
    probation_list_cache.clear()
    try:
        probation_members = await fetch_all_probation_members(bot)
        if not probation_members:
            pretty_log(
                "info",
                "No probation list members found to load into cache.",
                label="Probation List Cache",
            )
            return

        for (
            user_id,
            user_name,
            pokemeow_name,
            catch_requirement,
            assigned_on,
        ) in probation_members:
            probation_list_cache[user_id] = {
                "user_name": user_name,
                "pokemeow_name": pokemeow_name,
                "catch_requirement": catch_requirement,
                "assigned_on": assigned_on,
            }
        pretty_log(
            "info",
            f"Loaded {len(probation_list_cache)} probation list members into cache.",
            label="Probation List Cache",
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Error loading probation list cache: {e}",
            label="Probation List Cache",
        )




# Accepts user and pokemeow_name
def upsert_probation_list_cache(
    user: discord.Member,
    pokemeow_name: str,
    catch_requirement: int,
    assigned_on: int,
):
    user_name = user.name
    probation_list_cache[user.id] = {
        "user_name": user_name,
        "pokemeow_name": pokemeow_name,
        "catch_requirement": catch_requirement,
        "assigned_on": assigned_on,
    }
    pretty_log(
        "info",
        f"Upserted probation list cache member: {user_name} ({user.id}) | Pokemeow: {pokemeow_name} | Catch Requirement: {catch_requirement}",
        label="Probation List Cache",
    )


def update_probation_catch_requirement_cache(
    user: discord.Member, catch_requirement: int
):
    """
    Update the catch requirement for a probation_list_cache member.
    """
    if user.id in probation_list_cache:
        probation_list_cache[user.id]["catch_requirement"] = catch_requirement
        pretty_log(
            "info",
            f"Updated catch requirement for probation list cache member: {user} ({user.id}) to {catch_requirement}",
            label="Probation List Cache",
        )


def remove_probation_list_cache(user: discord.Member):
    """
    Remove a user from the probation_list_cache.
    """
    if user.id in probation_list_cache:
        del probation_list_cache[user.id]
        pretty_log(
            "info",
            f"Removed probation list cache member: {user} ({user.id})",
            label="Probation List Cache",
        )
