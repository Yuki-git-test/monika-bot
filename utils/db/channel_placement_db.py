import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE channel_placement (
    channel_id BIGINT NOT NULL,
    user_name VARCHAR(100) NULL,
    user_id BIGINT NULL,
    catches BIGINT NULL
);"""


async def upsert_channel_placement(
    bot,
    channel_id: int,
    user_id: int = None,
    user_name: str = None,
    catches: int = None,
):
    """
    Upserts a channel placement record into the database.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO channel_placement (channel_id, user_id, user_name, catches)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (channel_id) DO UPDATE
            SET user_id = EXCLUDED.user_id,
                user_name = EXCLUDED.user_name,
                catches = EXCLUDED.catches;
            """,
            channel_id,
            user_id,
            user_name,
            catches,
        )
        pretty_log(
            "info",
            f"Upserted channel placement: Channel ID {channel_id}, User ID {user_id}, User Name {user_name}, Catches {catches}",
            label="Channel Placement DB",
        )
        # Update cache as well
        from utils.cache.channel_placement_cache import upsert_channel_placement_cache
        upsert_channel_placement_cache(
            channel_id=channel_id,
            user_id=user_id,
            user_name=user_name,
            catches=catches,
        )

async def fetch_all_channel_placements(bot):
    """
    Fetches all channel placement records from the database.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT channel_id, user_id, user_name, catches
            FROM channel_placement;
            """
        )
        placements = [
            {
                "channel_id": row["channel_id"],
                "user_id": row["user_id"],
                "user_name": row["user_name"],
                "catches": row["catches"],
            }
            for row in rows
        ]
        pretty_log(
            "info",
            f"Fetched {len(placements)} channel placements from the database.",
            label="Channel Placement DB",
        )
        return placements

async def delete_channel_placement(bot, channel_id: int):
    """
    Deletes a channel placement record from the database.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM channel_placement
            WHERE channel_id = $1;
            """,
            channel_id,
        )
        pretty_log(
            "info",
            f"Deleted channel placement for Channel ID {channel_id}",
            label="Channel Placement DB",
        )
        # Also remove from cache
        from utils.cache.channel_placement_cache import remove_channel_placement_cache
        remove_channel_placement_cache(channel_id=channel_id)

async def bulk_update_channel_placement_catches(
        bot,
        channel_catches_list, batch_size = 10
    ):
    """
    Bulk updates catches for multiple channel placements.
    """
    async with bot.pg_pool.acquire() as conn:
        for i in range(0, len(channel_catches_list), batch_size):
            batch = channel_catches_list[i:i + batch_size]
            await conn.executemany(
                """
                UPDATE channel_placement
                SET catches = $2
                WHERE channel_id = $1;
                """,
                batch
            )
        pretty_log(
            "info",
            f"Bulk updated catches for {len(channel_catches_list)} channel placements.",
            label="Channel Placement DB",
        )