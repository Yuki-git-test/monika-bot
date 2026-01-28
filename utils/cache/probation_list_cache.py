import time

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
            catch_req_updated_on,
            stacking_requirements,
            stacking_req_updated_on,
        ) in probation_members:
            probation_list_cache[user_id] = {
                "user_name": user_name,
                "pokemeow_name": pokemeow_name,
                "catch_requirement": catch_requirement,
                "assigned_on": assigned_on,
                "catch_req_updated_on": catch_req_updated_on,
                "stacking_requirements": stacking_requirements,
                "stacking_req_updated_on": stacking_req_updated_on,
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


def update_all_probation_catch_requirements_to_value_cache(catch_requirement: int):
    """
    Update the catch requirement for all probation_list_cache members to a specific value.
    """
    for user_id in probation_list_cache:
        probation_list_cache[user_id]["catch_requirement"] = catch_requirement
        probation_list_cache[user_id]["catch_req_updated_on"] = int(time.time())
    pretty_log(
        "info",
        f"Updated catch requirement for all probation list cache members to {catch_requirement}.",
        label="Probation List Cache",
    )


def update_stacking_requirements_by_id_cache(
    user_id: int, new_stacking_requirements: int
):
    """
    Update the stacking_requirements for a probation_list_cache member by user_id.
    """
    if user_id in probation_list_cache:
        probation_list_cache[user_id][
            "stacking_requirements"
        ] = new_stacking_requirements
        probation_list_cache[user_id]["stacking_req_updated_on"] = int(time.time())
        pretty_log(
            "info",
            f"Updated stacking_requirements for probation list cache member by user_id: ({user_id}) to {new_stacking_requirements} and stacking_req_updated_on to current time",
            label="Probation List Cache",
        )


def update_catch_requirement_by_id_cache(user_id: int, new_catch_requirement: int):
    """
    Update the catch requirement for a probation_list_cache member by user_id.
    """
    if user_id in probation_list_cache:
        probation_list_cache[user_id]["catch_requirement"] = new_catch_requirement
        probation_list_cache[user_id]["catch_req_updated_on"] = int(time.time())
        pretty_log(
            "info",
            f"Updated catch requirement for probation list cache member by user_id: ({user_id}) to {new_catch_requirement}",
            label="Probation List Cache",
        )


def update_all_probation_catch_requirements_cache():
    """
    Update the catch requirement for all probation_list_cache members.
    """
    import time

    one_day_ago = int(time.time()) - 86400
    updated_count = 0
    for user_id in probation_list_cache:
        entry = probation_list_cache[user_id]
        # Only update if catch_req_updated_on is not set or older than 1 day
        if (
            "catch_req_updated_on" not in entry
            or entry["catch_req_updated_on"] is None
            or entry["catch_req_updated_on"] < one_day_ago
        ):
            entry["catch_requirement"] = entry.get("catch_requirement", 0) + 1500
            entry["catch_req_updated_on"] = int(time.time())
            updated_count += 1
    pretty_log(
        "info",
        f"Incremented catch requirement by 1500 for {updated_count} probation list cache members.",
        label="Probation List Cache",
    )


# Accepts user and pokemeow_name
def upsert_probation_list_cache(
    user: discord.Member,
    pokemeow_name: str,
    catch_requirement: int,
    assigned_on: int,
    stacking_requirements: int = 0,
):
    user_name = user.name

    probation_list_cache[user.id] = {
        "user_name": user_name,
        "pokemeow_name": pokemeow_name,
        "catch_requirement": catch_requirement,
        "assigned_on": assigned_on,
        "stacking_requirements": stacking_requirements,
        "stacking_req_updated_on": int(time.time()),
    }

    pretty_log(
        "info",
        f"Upserted probation list cache member: {user_name} ({user.id}) | Pokemeow: {pokemeow_name} | Catch Requirement: {catch_requirement}",
        label="Probation List Cache",
    )


# Update stacking_requirements for a probation_list_cache member
def update_probation_stacking_requirements_cache(
    user: discord.Member, stacking_requirements: int
):
    """
    Update the stacking_requirements for a probation_list_cache member.
    """
    if user.id in probation_list_cache:
        probation_list_cache[user.id]["stacking_requirements"] = stacking_requirements
        probation_list_cache[user.id]["stacking_req_updated_on"] = int(time.time())
        pretty_log(
            "info",
            f"Updated stacking_requirements for probation list cache member: {user} ({user.id}) to {stacking_requirements} and stacking_req_updated_on to current time",
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
        probation_list_cache[user.id]["catch_req_updated_on"] = int(time.time())
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


def remove_probation_list_cache_by_user_id(user_id: int):
    """
    Remove a user from the probation_list_cache by user_id.
    """
    if user_id in probation_list_cache:
        del probation_list_cache[user_id]
        pretty_log(
            "info",
            f"Removed probation list cache member by user_id: ({user_id})",
            label="Probation List Cache",
        )
