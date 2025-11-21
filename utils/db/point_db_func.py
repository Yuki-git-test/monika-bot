import discord

from utils.logs.pretty_log import pretty_log

# SQL to create the points table
"""CREATE TABLE points (
    user_id   BIGINT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    amount    INT NOT NULL
);"""


# 🟣────────────────────────────────────────────
#          ⚡ point DB Functions ⚡
# 🟣────────────────────────────────────────────
# Fetch one point entry for a user
async def fetch_user_points(bot, user: discord.Member):
    """
    Fetch a single point row for a user.
    Returns None if not found.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM points
            WHERE user_id = $1;
            """,
            user_id,
        )


# Fetch all points
async def fetch_all_points(bot):
    """
    Fetch all point rows.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM points;
            """
        )


# Update point amount for a user
async def update_points(bot, user: discord.Member, amount: int):
    """
    Update the point amount for a user.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE points
            SET amount = $1
            WHERE user_id = $2;
            """,
            amount,
            user_id,
        )


# Upsert point (insert or update)
async def upsert_points(bot, user: discord.Member, amount: int):
    """
    Insert or update a point row for a user.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO points (user_id, user_name, amount)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET user_name = $2, amount = $3;
            """,
            user_id,
            user_name,
            amount,
        )


# Add point (insert new row)
async def add_points(bot, user: discord.Member, amount: int):
    """
    Add a new point row for a user.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO points (user_id, user_name, amount)
            VALUES ($1, $2, $3);
            """,
            user_id,
            user_name,
            amount,
        )


# Remove point (delete row)
async def remove_points(bot, user: discord.Member):
    """
    Remove a point row for a user.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM points
            WHERE user_id = $1;
            """,
            user_id,
        )


# Reset points (clear table)
async def reset_points(bot):
    """
    Delete all rows from points table.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            TRUNCATE TABLE points;
            """
        )


# Get first place (user with highest amount)
async def get_first_place(bot):
    """
    Get the user with the highest point amount.
    Returns None if table is empty.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM points
            ORDER BY amount DESC
            LIMIT 1;
            """
        )
