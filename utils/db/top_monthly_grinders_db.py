import discord

from utils.logs.pretty_log import pretty_log

"""CREATE TABLE IF NOT EXISTS top_monthly_grinders (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT NOT NULL
);"""

async def fetch_all_top_monthly_grinders(bot):
    """
    Fetch all top_monthly_grinders rows.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM top_monthly_grinders;
            """
        )
async def upsert_top_monthly_grinder(bot, user: discord.Member):
    """
    Insert or update a top_monthly_grinders row for a user.
    """
    user_id = user.id
    user_name = user.name
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO top_monthly_grinders (user_id, user_name)
                VALUES ($1, $2)
                ON CONFLICT (user_id)
                DO UPDATE SET user_name = $2;
                """,
                user_id,
                user_name,
            )
            pretty_log(
                "db",
                f"Upserted top_monthly_grinder {user_name} ({user_id}) into database.",
            )
    except Exception as e:
        pretty_log(
            "error",
            f"Error upserting top_monthly_grinder {user_name} ({user_id}) into database: {e}",
        )

async def delete_top_monthly_grinder(bot, user:discord.Member):
    """
    Delete a top_monthly_grinders row for a user.
    """
    user_id = user.id
    user_name = user.name
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM top_monthly_grinders
                WHERE user_id = $1;
                """,
                user_id,
            )
            pretty_log(
                "db",
                f"Deleted top_monthly_grinder ({user_name}) from database.",
            )
    except Exception as e:
        pretty_log(
            "error",
            f"Error deleting top_monthly_grinder ({user_name}) from database: {e}",
        )
