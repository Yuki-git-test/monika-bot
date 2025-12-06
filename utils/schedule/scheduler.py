import asyncio
import calendar
import zoneinfo
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log

from .schedule_manager import SchedulerManager

# Schedule Functions
from .weekly_stats_check_reminder import weekly_stats_check_reminder

# Timezones
MANILA = zoneinfo.ZoneInfo("Asia/Manila")
NYC = zoneinfo.ZoneInfo("America/New_York")  # auto-handles EST/EDT

scheduler_manager = SchedulerManager(timezone_str="Asia/Manila")


async def setup_schedulers(bot):
    # Start the scheduler
    scheduler_manager.start()
    pretty_log("scheduler", "Scheduler started.")

    # Weekly Stats Check Reminder Every Saturday at 11:50 PM EST
    try:
        job = scheduler_manager.add_cron_job(
            func=weekly_stats_check_reminder,
            name="weekly_stats_check_reminder",
            hour=23,
            minute=50,
            day_of_week="sat",
            timezone=NYC,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: Weekly Stats Check Reminder every 7th, 14th, 21st, and 28th day at 11:50 PM EST\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule Weekly Stats Check Reminder. Error: {e}"),
        )

    # Attach the scheduler manager to the bot for later access
    bot.scheduler_manager = scheduler_manager
