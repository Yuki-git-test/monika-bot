"""CREATE TABLE probation_list (
    user_id   BIGINT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
);"""

import discord

from utils.logs.pretty_log import pretty_log


async def upsert_probation_member(bot, user: discord.Member, pokemeow_name: str):
    """
    Insert or update a probation_list row for a user.
    """
    user_id = user.id
    user_name = str(user)
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO probation_list (user_id, user_name, pokemeow_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET user_name = EXCLUDED.user_name, pokemeow_name = EXCLUDED.pokemeow_name;
            """,
            user_id,
            user_name,
            pokemeow_name,
        )
        pretty_log(
            "info",
            f"Upserted probation member: {user_name} ({user_id})",
            label="Probation List DB",
        )
        # Update cache as well
        from utils.cache.probation_list_cache import upsert_probation_list_cache

        upsert_probation_list_cache(user, pokemeow_name)


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


async def fetch_all_probation_members(bot):
    """
    Fetch all probation_list members.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, pokemeow_name FROM probation_list;
            """
        )
        probation_members = [
            (row["user_id"], row["user_name"], row["pokemeow_name"]) for row in rows
        ]
        pretty_log(
            "info",
            f"Fetched {len(probation_members)} probation members.",
            label="Probation List DB",
        )
        return probation_members
