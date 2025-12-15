import datetime
import json
import os
import time
from typing import Tuple

import pytz

from utils.cache.cache_list import vna_members_cache

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_PATH = os.path.join(BASE_DIR, "data", "monthly_requirements.json")


def is_member_less_than_a_month_old(user_id: int) -> bool:
    """
    Checks if a member has been in the VNA for less than a month (using US/Eastern timezone).
    clan_joined_date is a unix timestamp.
    """
    member_info = vna_members_cache.get(user_id)
    if not member_info:
        return False
    join_timestamp = member_info.get("clan_joined_date")
    if not join_timestamp:
        return False
    est = pytz.timezone("US/Eastern")
    join_date = datetime.datetime.fromtimestamp(join_timestamp, tz=est)
    now = datetime.datetime.now(est)
    delta = now - join_date
    return delta.days < 30


def read_monthly_requirements() -> Tuple[int, int]:
    """
    Reads the monthly_requirements.json file and returns catches and updated_on.
    Returns:
        (catches, updated_on)
    """
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    reqs = data.get("monthly_requirements", {})
    return reqs.get("expected_catches"), reqs.get("updated_on")


def write_monthly_requirements(new_expected_catches: int) -> bool:
    """
    Overwrites catches and updated_on in the JSON file, but only if at least a day has passed since last update,
    or if the old expected_catches value is 0.
    Returns True if write succeeded, False if not enough time has passed.
    """
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    reqs = data.get("monthly_requirements", {})
    last_update = reqs.get("updated_on", 0)
    old_expected_catches = reqs.get("expected_catches", 0)
    now = int(time.time())
    if old_expected_catches != 0 and now - last_update < 86400:
        return False  # Not enough time has passed and not a reset
    reqs["expected_catches"] = new_expected_catches
    reqs["updated_on"] = now
    data["monthly_requirements"] = reqs
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return True


def is_this_week_last_of_month(week_start=0):
    """
    Returns True if the current week (based on today) is the last week of the month and crosses into the next month.
    week_start: 0=Monday, 6=Sunday
    """
    today = datetime.date.today()
    # Find the start of the week
    start_of_week = today - datetime.timedelta(days=(today.weekday() - week_start) % 7)
    # Find the end of the week
    end_of_week = start_of_week + datetime.timedelta(days=6)
    # Last day of the month
    next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    last_day_of_month = next_month - datetime.timedelta(days=1)
    # If end_of_week is in the next month or after last day of month, it's the last week
    return end_of_week.month != today.month or end_of_week > last_day_of_month


def get_member_weeks_in_clan(user_id: int) -> int:
    """
    Returns the number of full 7-day weeks the member has been in the VNA (using US/Eastern timezone).
    clan_joined_date is a unix timestamp.
    """
    member_info = vna_members_cache.get(user_id)
    if not member_info:
        return 0
    join_timestamp = member_info.get("clan_joined_date")
    if not join_timestamp:
        return 0
    est = pytz.timezone("US/Eastern")
    join_date = datetime.datetime.fromtimestamp(join_timestamp, tz=est)
    now = datetime.datetime.now(est)
    delta = now - join_date
    return delta.days // 7


def reset_monthly_requirements():
    """
    Resets the monthly requirements to default values (expected_catches=0, updated_on=now).
    """
    now = int(time.time())
    data = {"monthly_requirements": {"expected_catches": 0, "updated_on": now}}
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
