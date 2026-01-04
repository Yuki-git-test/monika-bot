import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE monthly_requirements (
    expected_catches INT DEFAULT 0,
    updated_on BIGINT DEFAULT (EXTRACT(EPOCH FROM now()))
);"""

async def initialize_monthly_requirements(bot):
    """Initialize the monthly_requirements table with default values if empty."""
    expected_catches = 1500
    async with bot.pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT COUNT(*) AS count
            FROM monthly_requirements;
            """
        )
        if row and row["count"] == 0:
            await conn.execute(
                """
                INSERT INTO monthly_requirements (expected_catches, updated_on)
                VALUES ($1, EXTRACT(EPOCH FROM now()));
                """,
                expected_catches,
            )
            pretty_log(
                "info",
                "Initialized monthly_requirements table with default values.",
                label="Monthly Req DB",
            )
# Increment expected catches by 1500
async def increment_expected_catches(bot, increment: int = 1500):
    """
    Increment the expected catches by a specified amount.
    Default increment is 1500.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE monthly_requirements
            SET expected_catches = expected_catches + $1,
                updated_on = EXTRACT(EPOCH FROM now());
            """,
            increment,
        )
        pretty_log(
            "info",
            f"Incremented expected catches by {increment}.",
            label="Monthly Req DB",
        )

# Get expected catches
async def get_expected_catches(bot) -> int:
    """
    Retrieve the current expected catches.
    """
    async with bot.pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT expected_catches
            FROM monthly_requirements;
            """
        )
        expected_catches = row["expected_catches"] if row else 0
        pretty_log(
            "info",
            f"Retrieved expected catches: {expected_catches}.",
            label="Monthly Req DB",
        )
        return expected_catches

# Reset expected catches to zero
async def reset_expected_catches(bot):
    """
    Reset the expected catches to zero.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE monthly_requirements
            SET expected_catches = 0,
                updated_on = EXTRACT(EPOCH FROM now());
            """
        )
        pretty_log(
            "info",
            "Reset expected catches to zero.",
            label="Monthly Req DB",
        )

async def reset_expected_catches_to_1500(bot):
    """
    Reset the expected catches to 1500.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE monthly_requirements
            SET expected_catches = 1500,
                updated_on = EXTRACT(EPOCH FROM now());
            """
        )
        pretty_log(
            "info",
            "Reset expected catches to 1500.",
            label="Monthly Req DB",
        )