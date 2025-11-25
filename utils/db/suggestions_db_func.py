import discord
from discord import app_commands
from discord.ext import commands

from utils.logs.pretty_log import pretty_log

# SQL Script
"""CREATE TABLE suggestions (
    id SERIAL,
    message_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    user_name TEXT NOT NULL,
    suggestion_text TEXT NOT NULL
);"""


async def insert_suggestion(
    bot,
    message_id: int,
    user: discord.Member,
    suggestion_text: str,
    suggestion_title: str,
    thread_id: int,
):
    """
    Insert a new suggestion into the suggestions table.
    """
    user_id = user.id
    user_name = user.name
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO suggestions (message_id, user_id, user_name, suggestion_text, suggestion_title, thread_id)
            VALUES ($1, $2, $3, $4, $5, $6);
            """,
            message_id,
            user_id,
            user_name,
            suggestion_text,
            suggestion_title,
            thread_id,
        )
        pretty_log(
            "db",
            f"Inserted suggestion from {user_name} ({user_id}) with message_id {message_id}.",
        )


async def fetch_suggestion_by_message_id(bot, message_id: int):
    """
    Fetch a suggestion by its message_id.
    Returns None if not found.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM suggestions
            WHERE message_id = $1;
            """,
            message_id,
        )


async def get_latest_suggestion_id(bot):
    """
    Fetch the latest suggestion id.
    Returns None if no suggestions exist.
    """
    async with bot.pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id FROM suggestions
            ORDER BY id DESC
            LIMIT 1;
            """
        )
        return row["id"] if row else None


async def fetch_suggestion_by_id(bot, suggestion_id: int):
    """
    Fetch a suggestion by its id.
    Returns None if not found.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM suggestions
            WHERE id = $1;
            """,
            suggestion_id,
        )


async def fetch_all_suggestions(bot):
    """
    Fetch all suggestions.
    """
    async with bot.pg_pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM suggestions;
            """
        )


async def remove_suggestion_by_message_id(bot, message_id: int):
    """
    Remove a suggestion by its message_id.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM suggestions
            WHERE message_id = $1;
            """,
            message_id,
        )
        pretty_log(
            "db",
            f"Removed suggestion with message_id {message_id}.",
        )

async def remove_suggestion_by_id(bot, suggestion_id: int):
    """
    Remove a suggestion by its id.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM suggestions
            WHERE id = $1;
            """,
            suggestion_id,
        )
        pretty_log(
            "db",
            f"Removed suggestion with id {suggestion_id}.",
        )

# Autocomplte suggestion titles as display with value = suggestion ids
async def fetch_suggestion_titles_for_autocomplete(bot):
    """
    Fetch all suggestion titles and their ids for autocomplete.
    Returns a list of tuples (id, suggestion_title).
    """
    async with bot.pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, suggestion_title FROM suggestions;
            """
        )
        return [(row["id"], row["suggestion_title"]) for row in rows]


# 🍭──────────────────────────────
#   🎀 Autocomplete
# 🍭──────────────────────────────
async def suggestion_title_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:
    """
    Autocomplete function for suggestion titles.
    """
    bot = interaction.client
    suggestions = await fetch_suggestion_titles_for_autocomplete(bot)
    filtered = [
        app_commands.Choice(name=f"ID: {sugg_id} | {title}", value=sugg_id)
        for sugg_id, title in suggestions
        if current.lower() in title.lower()
    ]
    return filtered[:25]  # Limit to 25 choices
