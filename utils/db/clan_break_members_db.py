import time
from datetime import datetime

import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE clan_break_members (
    user_id     BIGINT PRIMARY KEY,
    user_name   VARCHAR(100) NOT NULL,
    assigned_on BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT),
    ends_on     BIGINT
);"""


async def upsert_clan_break_member(
    bot: discord.Client,
    user: discord.Member,
):
    """
    Insert or update a clan_break_members row for a user.
    """
    # Add 14 days to current time for ends_on
    ends_on = int(time.time()) + 14 * 24 * 60 * 60
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO clan_break_members (user_id, user_name, ends_on)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET user_name = EXCLUDED.user_name, ends_on = EXCLUDED.ends_on;
            """,
            user_id,
            user_name,
            ends_on,
        )

        pretty_log(
            "info",
            f"Upserted clan break member: {user_name} ({user_id})",
            label="Clan Break Members DB",
        )
        return ends_on
    return None



async def remove_clan_break_member(
    bot: discord.Client,
    user_id: int
):
    """
    Remove a clan_break_members row for a user.
    """


    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM clan_break_members
            WHERE user_id = $1;
            """,
            user_id,
        )
        pretty_log(
            "info",
            f"Removed clan break member:  ({user_id})",
            label="Clan Break Members DB",
        )



async def fetch_all_clan_break_members(bot: discord.Client):
    """
    Fetch all clan_break_members rows.
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, assigned_on, ends_on
            FROM clan_break_members;
            """,
        )
        clan_break_members = []
        for row in rows:
            member_entry = {
                "user_id": row["user_id"],
                "user_name": row["user_name"],
                "assigned_on": row["assigned_on"],
                "ends_on": row["ends_on"],
            }
            clan_break_members.append(member_entry)
        return clan_break_members


async def fetch_all_due_clan_break_members(
    bot: discord.Client,
):
    """Returns all clan break members whose break period has ended."""
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, user_name, assigned_on, ends_on
            FROM clan_break_members
            WHERE ends_on IS NOT NULL AND ends_on <= $1;
            """,
            int(time.time()),
        )
        due_members = []
        for row in rows:
            member_entry = {
                "user_id": row["user_id"],
                "user_name": row["user_name"],
                "assigned_on": row["assigned_on"],
                "ends_on": row["ends_on"],
            }
            due_members.append(member_entry)
        return due_members
