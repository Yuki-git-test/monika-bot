"""CREATE TABLE kick_list (
    user_id   BIGINT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
);"""

import discord

from utils.logs.pretty_log import pretty_log


async def upsert_kick_list_member(bot, user: discord.Member, pokemeow_name: str):
    """
    Insert or update a kick_list row for a user.
    """
    user_id = user.id
    user_name = str(user)
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO kick_list (user_id, user_name, pokemeow_name)
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
            f"Upserted kick list member: {user_name} ({user_id}) | Pokemeow: {pokemeow_name}",
            label="Kick List DB",
        )
        # Update cache as well
        from utils.cache.kick_list_cache import upsert_kick_list_cache

        upsert_kick_list_cache(user, pokemeow_name)


async def remove_kick_list_member(bot, user: discord.Member):
    """
    Remove a kick_list row for a user.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM kick_list
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Removed kick list member: {user} ({user_id})",
            label="Kick List DB",
        )
        # Remove from cache as well
        from utils.cache.kick_list_cache import remove_kick_list_cache

        remove_kick_list_cache(user)


async def fetch_all_kick_list_members(bot):
    """
    Fetch all kick_list members.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, pokemeow_name FROM kick_list;
            """
        )
        kick_list_members = [
            (row["user_id"], row["user_name"], row["pokemeow_name"]) for row in rows
        ]
        pretty_log(
            "info",
            f"Fetched {len(kick_list_members)} kick list members.",
            label="Kick List DB",
        )
        return kick_list_members
