import discord

from constants.vn_allstars_constants import (
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.logs.pretty_log import pretty_log

# SQL to create the team_trophies table
"""CREATE TABLE team_trophies (
    role_id   BIGINT PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL,
    amount    INT NOT NULL
);"""
TABLE_NAME = "team_trophies"

LEADERBOARD_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.clan_leaderboard


async def fetch_current_leaderboard_info(bot):
    """
    Fetch the trophy leaderboard info.
    Returns None if not found.
    """

    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM current_trophy_leaderboard
            WHERE channel_id = $1
            LIMIT 1;
            """,
            LEADERBOARD_CHANNEL_ID,
        )


# Upsert row if table is empty
async def upsert_leaderboard_msg_id(bot, message_id: int, channel: discord.TextChannel):
    """
    Upsert the trophy leaderboard message ID.
    """
    channel_name = channel.name
    channel_id = channel.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO current_trophy_leaderboard (message_id, channel_id, channel_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (message_id) DO UPDATE
            SET channel_id = EXCLUDED.channel_id,
                channel_name = EXCLUDED.channel_name;
            """,
            message_id,
            channel_id,
            channel_name,
        )
        pretty_log(
            "info",
            f"Upserted leaderboard message ID: {message_id} in channel {channel_name} ({channel_id})",
            label="Trophy Leaderboard DB",
        )


async def remove_leaderboard_msg_id(bot):
    """
    Remove the trophy leaderboard message ID.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM current_trophy_leaderboard
            WHERE channel_id = $1;
            """,
            LEADERBOARD_CHANNEL_ID,
        )
        pretty_log(
            "info",
            f"Removed leaderboard message ID for channel ID: {LEADERBOARD_CHANNEL_ID}",
            label="Trophy Leaderboard DB",
        )


async def delete_all_team_trophies(bot: discord.Client):
    """Deletes all team trophy records from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                DELETE FROM {TABLE_NAME};
            """
            await conn.execute(query)
            pretty_log(
                tag="db",
                message="Deleted all team trophies from the database",
            )
            # Reset the leaderboard message ID as well
            await remove_leaderboard_msg_id(bot)

    except Exception as e:
        pretty_log(tag="error", message=f"Error deleting all team trophies: {e}")


async def upsert_team_trophy(
    bot: discord.Client, role_id: int, role_name: str, amount: int
):
    """Inserts or updates a team trophy record in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                INSERT INTO {TABLE_NAME} (role_id, role_name, amount)
                VALUES ($1, $2, $3)
                ON CONFLICT (role_id) DO UPDATE
                SET role_name = EXCLUDED.role_name,
                    amount = EXCLUDED.amount;
            """
            await conn.execute(query, role_id, role_name, amount)
            pretty_log(
                tag="db",
                message=f"Upserted team trophy: {role_name} ({role_id}) - {amount}",
            )
    except Exception as e:
        pretty_log(tag="error", message=f"Error upserting team trophy: {e}")


async def fetch_team_trophy(
    bot: discord.Client, role_id: int
) -> dict[str, int] | None:
    """Fetches a team trophy record from the database by role_id."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                SELECT role_name, amount
                FROM {TABLE_NAME}
                WHERE role_id = $1;
            """
            row = await conn.fetchrow(query, role_id)
            if row:
                pretty_log(
                    tag="db",
                    message=f"Fetched team trophy: {row['role_name']} ({role_id}) - {row['amount']}",
                )
                return {"role_name": row["role_name"], "amount": row["amount"]}
            else:
                pretty_log(
                    tag="db",
                    message=f"No team trophy found for role_id: {role_id}",
                )
                return None
    except Exception as e:
        pretty_log(tag="error", message=f"Error fetching team trophy: {e}")
        return None


async def fetch_all_team_trophies(
    bot: discord.Client,
) -> dict[int, dict[str, int]]:
    """Fetches all team trophies from the database and returns as a dictionary."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                SELECT role_id, role_name, amount
                FROM {TABLE_NAME};
            """
            rows = await conn.fetch(query)
            trophies = {
                row["role_id"]: {
                    "role_name": row["role_name"],
                    "amount": row["amount"],
                }
                for row in rows
            }
            pretty_log(
                tag="db",
                message=f"Fetched {len(trophies)} team trophies from the database",
            )
            return trophies
    except Exception as e:
        pretty_log(tag="error", message=f"Error fetching team trophies: {e}")
        return {}


async def delete_team_trophy(bot: discord.Client, role_id: int):
    """Deletes a team trophy record from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                DELETE FROM {TABLE_NAME}
                WHERE role_id = $1;
            """
            await conn.execute(query, role_id)
            pretty_log(
                tag="db",
                message=f"Deleted team trophy with role_id: {role_id}",
            )
    except Exception as e:
        pretty_log(tag="error", message=f"Error deleting team trophy: {e}")
