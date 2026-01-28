"""CREATE TABLE probation_list (
    user_id   BIGINT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    pokemeow_name VARCHAR(100),
    catch_requirement INT,
    assigned_on BIGINT,
    catch_req_updated_on BIGINT,
    stacking_requirements INT DEFAULT 0,
    stacking_req_updated_on BIGINT
);"""

# SQL script to add the new column to an existing table:
# ALTER TABLE probation_list ADD COLUMN stacking_req_updated_on BIGINT;

import time

import discord

from utils.logs.pretty_log import pretty_log


async def upsert_probation_member(
    bot,
    user: discord.Member,
    pokemeow_name: str,
    catch_requirement: int,
    stacking_requirements: int = 0,
):
    """
    Insert or update a probation_list row for a user.
    """
    user_id = user.id
    user_name = user.name
    import time

    assigned_on = int(time.time())
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO probation_list (user_id, user_name, pokemeow_name, catch_requirement, assigned_on, stacking_requirements)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE
            SET user_name = EXCLUDED.user_name,
                pokemeow_name = EXCLUDED.pokemeow_name,
                catch_requirement = EXCLUDED.catch_requirement,
                assigned_on = EXCLUDED.assigned_on,
                stacking_requirements = EXCLUDED.stacking_requirements;
            """,
            user_id,
            user_name,
            pokemeow_name,
            catch_requirement,
            assigned_on,
            stacking_requirements,
        )
        pretty_log(
            "info",
            f"Upserted probation member: {user_name} ({user_id})",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import upsert_probation_list_cache

        upsert_probation_list_cache(
            user, pokemeow_name, catch_requirement, assigned_on, stacking_requirements
        )


async def update_stacking_requirements(bot, user_id: int, stacking_requirements: int):
    """
    Update the stacking_requirements for a probation_list member and set stacking_req_updated_on to current time.
    """
    import time

    now = int(time.time())
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE probation_list
            SET stacking_requirements = $1,
                stacking_req_updated_on = $2
            WHERE user_id = $3;
            """,
            stacking_requirements,
            now,
            user_id,
        )
        pretty_log(
            "info",
            f"Updated stacking_requirements for probation member ID: ({user_id}) to {stacking_requirements} and stacking_req_updated_on to {now}",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import (
            update_stacking_requirements_by_id_cache,
        )

        update_stacking_requirements_by_id_cache(user_id, stacking_requirements)


# Update All required catches for all probation members
async def update_all_probation_catch_requirements(bot):
    """
    Update the catch requirement for all probation_list members.
    """

    one_day_ago = int(time.time()) - 86400
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE probation_list
            SET catch_requirement = catch_requirement + 1500,
                catch_req_updated_on = $1
            WHERE catch_req_updated_on IS NULL OR catch_req_updated_on < $2;
            """,
            int(time.time()),
            one_day_ago,
        )
        pretty_log(
            "info",
            f"Updated catch requirement for all probation members by +1500 where applicable.",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import (
            update_all_probation_catch_requirements_cache,
        )

        update_all_probation_catch_requirements_cache()


async def update_probation_catch_requirement(
    bot, user: discord.Member, catch_requirement: int
):
    """
    Update the catch requirement for a probation_list member.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE probation_list
            SET catch_requirement = $1
            WHERE user_id = $2;
            """,
            catch_requirement,
            user_id,
        )
        pretty_log(
            "info",
            f"Updated catch requirement for probation member: {user} ({user_id}) to {catch_requirement}",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import (
            update_probation_catch_requirement_cache,
        )

        update_probation_catch_requirement_cache(user, catch_requirement)


async def update_probation_catch_requirement_by_id(
    bot, user_id: int, catch_requirement: int
):
    """
    Update the catch requirement for a probation_list member by user_id.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE probation_list
            SET catch_requirement = $1
            WHERE user_id = $2;
            """,
            catch_requirement,
            user_id,
        )
        pretty_log(
            "info",
            f"Updated catch requirement for probation member ID: ({user_id}) to {catch_requirement}",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import (
            update_catch_requirement_by_id_cache,
        )

        update_catch_requirement_by_id_cache(user_id, catch_requirement)


async def remove_probation_member_by_user_id(bot, user_id: int):
    """
    Remove a probation_list row for a user by user_id.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM probation_list
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Removed probation member:  ({user_id})",
            label="Probation List DB",
        )
        # Remove from cache as well
        from utils.cache.probation_list_cache import (
            remove_probation_list_cache_by_user_id,
        )

        remove_probation_list_cache_by_user_id(user_id)


async def remove_probation_member(bot, user: discord.Member):
    """
    Remove a probation_list row for a user.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM probation_list
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Removed probation member: {user} ({user_id})",
            label="Probation List DB",
        )
        # Remove from cache as well
        from utils.cache.probation_list_cache import remove_probation_list_cache

        remove_probation_list_cache(user)


async def update_all_probation_member_catch_requirements(bot, catch_requirement: int):
    """
    Update the catch requirement for all probation_list members to a specific value.
    """

    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE probation_list
            SET catch_requirement = $1;
            """,
            catch_requirement,
        )
        pretty_log(
            "info",
            f"Updated catch requirement for all probation members to {catch_requirement}.",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import (
            update_all_probation_catch_requirements_to_value_cache,
        )

        update_all_probation_catch_requirements_to_value_cache(catch_requirement)


async def fetch_all_probation_members(bot):
    """
    Fetch all probation_list members.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, pokemeow_name, catch_requirement, assigned_on, catch_req_updated_on, stacking_requirements FROM probation_list;
            """
        )
        probation_members = [
            (
                row["user_id"],
                row["user_name"],
                row["pokemeow_name"],
                row["catch_requirement"],
                row["assigned_on"],
                row["catch_req_updated_on"],
                row["stacking_requirements"],
            )
            for row in rows
        ]
        pretty_log(
            "info",
            f"Fetched {len(probation_members)} probation members.",
            label="Probation List DB",
        )
        return probation_members
