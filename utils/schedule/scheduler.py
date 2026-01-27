import asyncio
import calendar
import zoneinfo
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log

from .custom_role_checker import custom_role_checker
from .monthly_reqs_reset import monthly_reqs_reset_func
from .prob_weekly_catch_reminder import (
    new_prob_catch_reminder,
    prob_weekly_catch_reminder,
)
from .schedule_manager import SchedulerManager

# Schedule Functions
from .weekly_stats_check_reminder import (
    monthly_stats_check_reminder,
    weekly_stats_check_reminder,
)

# Timezones
MANILA = zoneinfo.ZoneInfo("Asia/Manila")
NYC = zoneinfo.ZoneInfo("America/New_York")  # auto-handles EST/EDT

scheduler_manager = SchedulerManager(timezone_str="Asia/Manila")


async def setup_schedulers(bot):
    # Start the scheduler
    scheduler_manager.start()
    pretty_log("scheduler", "Scheduler started.")

    # Monthly Stats Check Reminder Every 7th, 14th, 21st, and 28th at 11:50 PM EST
    try:
        job = scheduler_manager.add_cron_job(
            func=monthly_stats_check_reminder,
            name="monthly_stats_check_reminder",
            hour=23,
            minute=0,
            day_of_month="7,14,21,28",
            timezone=NYC,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: Monthly Stats Check Reminder every 7th, 14th, 21st, and 28th day at 11:50 PM EST\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule Monthly Stats Check Reminder. Error: {e}"),
        )
    # Schedule new probation reminder every 7th, 14th, 21st, and 28th at 11:50 PM Eastern Time
    try:
        job = scheduler_manager.add_cron_job(
            func=new_prob_catch_reminder,
            name="new_prob_catch_reminder",
            hour=23,
            minute=50,
            day_of_month="7,14,21,28",
            timezone=NYC,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: New Probation Catch Reminder every 7th, 14th, 21st, and 28th day at 11:50 PM EST\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule New Probation Catch Reminder. Error: {e}"),
        )

    """# Weekly Stats Check Reminder Every Saturday at 11:50 PM EST
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
    """

    """# PROB Weekly Catch Reminder Every Friday Midnight EST
    try:
        job = scheduler_manager.add_cron_job(
            func=prob_weekly_catch_reminder,
            name="prob_weekly_catch_reminder",
            hour=0,
            minute=0,
            day_of_week="fri",
            timezone=NYC,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: PROB Weekly Catch Reminder every Friday at 12:00 AM EST\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule PROB Weekly Catch Reminder. Error: {e}"),
        )"""
    """# Monthly Requirements Reset on 1st of every month at 12:00 AM EST
    try:
        job = scheduler_manager.add_cron_job(
            func=monthly_reqs_reset_func,
            name="monthly_reqs_reset_func",
            hour=0,
            minute=0,
            day_of_month=1,
            timezone=NYC,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: Monthly Requirements Reset on the 1st of every month at 12:00 AM EST\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule Monthly Requirements Reset. Error: {e}"),
        )"""

    # Custom Role Checker Every 2nd of the Month at 12:00 PM Manila Time
    try:
        job = scheduler_manager.add_cron_job(
            func=custom_role_checker,
            name="custom_role_checker",
            hour=12,
            minute=0,
            day_of_month=2,
            timezone=MANILA,
            args=[bot],
        )
        pretty_log(
            "scheduler",
            message=(
                f"Scheduled: Custom Role Checker every 2nd of the month at 12:00 PM Manila Time\n"
                f"Next Scheduled Run: {job.next_run_time}"
            ),
        )
    except Exception as e:
        pretty_log(
            "error",
            message=(f"Failed to schedule Custom Role Checker. Error: {e}"),
        )

    # Attach the scheduler manager to the bot for later access
    bot.scheduler_manager = scheduler_manager
