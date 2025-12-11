import discord
from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE personal_channels (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT NOT NULL,
    channel_id BIGINT NOT NULL
);"""

async def upsert_personal_channel(
    bot: discord.Client,
    user: discord.Member,
    channel_id: int,
):
    """
    Insert or update a personal_channels row for a user.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO personal_channels (user_id, user_name, channel_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET user_name = EXCLUDED.user_name, channel_id = EXCLUDED.channel_id;
            """,
            user_id,
            user_name,
            channel_id,
        )
        pretty_log(
            "info",
            f"Upserted personal channel: {user_name} ({user_id}) - Channel ID: {channel_id}",
            label="Personal Channels DB",
        )
async def fetch_personal_channel_id(bot: discord.Client, user_id: int):
    """
    Fetch the personal channel ID for a user.
    """
    async with bot.pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT channel_id FROM personal_channels
            WHERE user_id = $1;
            """,
            user_id,
        )
        if row:
            return row["channel_id"]
        else:
            return None
async def fetch_all_personal_channels(bot: discord.Client):
    """
    Fetch all personal channels.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, channel_id FROM personal_channels;
            """
        )
        return rows


async def delete_personal_channel(bot: discord.Client, user_id: int):
    """
    Delete a personal_channels row for a user.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM personal_channels
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Deleted personal channel for user ID: {user_id}",
            label="Personal Channels DB",
        )