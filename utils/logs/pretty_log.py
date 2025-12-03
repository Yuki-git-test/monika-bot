import traceback
from datetime import datetime

# -------------------- 🧩 Global Bot Reference --------------------
from typing import Optional

import discord
from discord.ext import commands

BOT_INSTANCE: Optional[commands.Bot] = None
CC_ERROR_LOGS_CHANNEL_ID = 1444997181244444672

def set_monika_bot(bot: commands.Bot):
    """Set the global bot instance for automatic logging."""
    global BOT_INSTANCE
    BOT_INSTANCE = bot


# -------------------- 🍑 Monika's Log Tags --------------------
TAGS = {
    "info": "📖 INFO",
    "cache": "🍊 CACHE",
    "db": "🍑 DB",
    "cmd": "🖋️ CMD",
    "ready": "🌹 READY",
    "error": "💔 ERROR",
    "warn": "⚡ WARN",
    "critical": "🎭 CRITICAL",
    "skip": "📝 SKIP",
    "sent": "💌 SENT",
    "debug": "🔍 DEBUG",
    "success": "✅ SUCCESS",
    "scheduler": "⏰ SCHEDULER",
}

# -------------------- 🍑 Monika's ANSI Colors --------------------
COLOR_CORAL_COOL = "\033[38;2;255;154;122m"  # Monika's signature cool coral
COLOR_SOFT_PINK = "\033[38;2;255;182;193m"  # Soft romantic pink
COLOR_CORAL = "\033[38;2;255;127;80m"  # Warm coral for warnings
COLOR_LAVENDER = "\033[38;2;230;230;250m"  # Gentle lavender for info
COLOR_CRIMSON = "\033[38;2;220;20;60m"  # Deep crimson for errors
COLOR_RESET = "\033[0m"

MAIN_COLORS = {
    "cyan": COLOR_CORAL_COOL,  # Primary color - cool coral
    "teal": COLOR_SOFT_PINK,  # Secondary - soft pink
    "orange": COLOR_CORAL,  # Warnings - coral
    "purple": COLOR_LAVENDER,  # Critical - lavender
    "red": COLOR_CRIMSON,  # Errors - deep crimson
    "reset": COLOR_RESET,
}

# -------------------- ⚠️ Critical Logs Channel --------------------
CRITICAL_LOG_CHANNEL_ID = (
    1375702774771093697  # replace with your Arceus bot log channel
)
CRITICAL_LOG_CHANNEL_LIST = [
    1375702774771093697,  # Arceus Bot Logs
    CC_ERROR_LOGS_CHANNEL_ID,
]

# -------------------- 🌟 Pretty Log --------------------
def pretty_log(
    tag: str = None,
    message: str = "",
    *,
    label: str = None,
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    """
    Prints a colored log for Arceus-themed bots with timestamp and emoji.
    Sends critical/error/warn messages to Discord if bot is set.
    """
    prefix = TAGS.get(tag) if tag else ""
    prefix_part = f"[{prefix}] " if prefix else ""
    label_str = f"[{label}] " if label else ""

    # Choose color based on tag
    color = MAIN_COLORS["cyan"]
    if tag in ("warn",):
        color = MAIN_COLORS["orange"]
    elif tag in ("error",):
        color = MAIN_COLORS["red"]
    elif tag in ("critical",):
        color = MAIN_COLORS["purple"]

    now = datetime.now().strftime("%H:%M:%S")
    log_message = f"{color}[{now}] {prefix_part}{label_str}{message}{COLOR_RESET}"
    print(log_message)

    # Optionally print traceback
    if include_trace and tag in ("error", "critical"):
        traceback.print_exc()

    # Send to all Discord channels in the list if bot available
    bot_to_use = bot or BOT_INSTANCE
    if bot_to_use and tag in ("critical", "error", "warn"):
        for channel_id in CRITICAL_LOG_CHANNEL_LIST:
            try:
                channel = bot_to_use.get_channel(channel_id)
                if channel:
                    full_message = f"{prefix_part}{label_str}{message}"
                    if include_trace and tag in ("error", "critical"):
                        full_message += f"\n```py\n{traceback.format_exc()}```"
                    if len(full_message) > 2000:
                        full_message = full_message[:1997] + "..."
                    bot_to_use.loop.create_task(channel.send(full_message))
            except Exception:
                print(
                    f"{COLOR_CRIMSON}[❌ ERROR] Failed to send log to Discord channel {channel_id}{COLOR_RESET}"
                )
                traceback.print_exc()


# -------------------- 🌸 UI Error Logger --------------------
def log_ui_error(
    *,
    error: Exception,
    interaction: discord.Interaction = None,
    label: str = "UI",
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    """Logs UI errors with automatic Discord reporting."""
    location_info = ""
    if interaction:
        user = interaction.user
        location_info = f"User: {user} ({user.id}) | Channel: {interaction.channel} ({interaction.channel_id})"

    error_message = f"UI error occurred. {location_info}".strip()
    now = datetime.now().strftime("%H:%M:%S")

    print(
        f"{COLOR_CRIMSON}[{now}] [💥 CRITICAL] {label} error: {error_message}{COLOR_RESET}"
    )
    if include_trace:
        traceback.print_exception(type(error), error, error.__traceback__)

    bot_to_use = bot or BOT_INSTANCE

    pretty_log(
        "error",
        error_message,
        label=label,
        bot=bot_to_use,
        include_trace=include_trace,
    )

    if bot_to_use:
        try:
            channel = bot_to_use.get_channel(CRITICAL_LOG_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"⚠️ UI Error Logged [{label}]",
                    description=f"{location_info or '*No interaction data*'}",
                    color=0xFF9A7A,  # Cool coral
                )
                if include_trace:
                    trace_text = "".join(
                        traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                    )
                    if len(trace_text) > 1000:
                        trace_text = trace_text[:1000] + "..."
                    embed.add_field(
                        name="Traceback", value=f"```py\n{trace_text}```", inline=False
                    )
                bot_to_use.loop.create_task(channel.send(embed=embed))
        except Exception:
            print(
                f"{COLOR_CRIMSON}[❌ ERROR] Failed to send UI error to bot channel{COLOR_RESET}"
            )
            traceback.print_exc()
