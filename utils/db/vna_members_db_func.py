import discord
from utils.logs.pretty_log import pretty_log
# SQL Script to create the vna_members table
"""CREATE TABLE vna_members (
    user_id    BIGINT PRIMARY KEY,
    user_name  VARCHAR(100) NOT NULL,
    channel_id BIGINT NOT NULL
);"""


# Fetch one member entry for a user
async def fetch_user_member(bot, user: discord.Member):
    """
    Fetch a single vna_members row for a user.
    Returns None if not found.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM vna_members
            WHERE user_id = $1;
            """,
            user_id,
        )


# Fetch all members
async def fetch_all_members(bot):
    """
    Fetch all vna_members rows.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM vna_members;
            """
        )


# Update member channel_id for a user
async def update_member_channel(bot, user: discord.Member, channel_id: int):
    """
    Update the channel_id for a user in vna_members.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE vna_members
            SET channel_id = $1
            WHERE user_id = $2;
            """,
            channel_id,
            user_id,
        )
        pretty_log(
            "info",
            f"Updated channel_id for {user.name} to {channel_id} in vna_members.",
        )


# Upsert member (insert or update)
async def upsert_member(bot, user: discord.Member, channel_id: int):
    """
    Insert or update a vna_members row for a user.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO vna_members (user_id, user_name, channel_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET user_name = $2, channel_id = $3;
            """,
            user_id,
            user_name,
            channel_id,
        )
        pretty_log(
            "info",
            f"Upserted vna_members for {user.name} with channel_id {channel_id}.",
        )


# Add member (insert new row)
async def add_member(bot, user: discord.Member, channel_id: int):
    """
    Add a new vna_members row for a user.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO vna_members (user_id, user_name, channel_id)
            VALUES ($1, $2, $3);
            """,
            user_id,
            user_name,
            channel_id,
        )
        pretty_log(
            "info",
            f"Added {user.name} to vna_members with channel_id {channel_id}.",
        )


# Remove member (delete row)
async def remove_member(bot, user: discord.Member):
    """
    Remove a vna_members row for a user.
    """
    user_id = user.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM vna_members
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Removed {user.name} from vna_members.",
        )


# Reset members (clear table)
async def reset_members(bot):
    """
    Delete all rows from vna_members table.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            TRUNCATE TABLE vna_members;
            """
        )


# Get member by channel_id
async def get_member_by_channel(bot, channel_id: int):
    """
    Get the member with the given channel_id.
    Returns None if not found.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM vna_members
            WHERE channel_id = $1;
            """,
            channel_id,
        )
