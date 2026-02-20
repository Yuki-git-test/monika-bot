vna_members_cache: dict[int, dict] = {}
# Structure
# user_id: {
# "user_name": str,
# "pokemeow_name": str,
# "channel_id": int,
# "perks": str,
# "faction": str,
# "clan_joined_date": int,
# "last_month_catches": int,
# }
top_monthly_grinders_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
# }

webhook_url_cache: dict[tuple[int, int], str] = {}
#     ...
#
# }
# key = (bot_id, channel_id)
# Structure:
# webhook_url_cache = {
# (bot_id, channel_id): {
#     "url": "https://discord.com/api/webhooks/..."
#     "channel_name": "alerts-channel",
# },
#

probation_list_cache: dict[int, dict] = {}
# Structure
# user_id: {
# "user_name": str,
# "pokemeow_name": str,
# "catch_requirement": int,
# "assigned_on": int,
# "catch_req_updated_on": int,
# "stacking_requirements": int,
# }

kick_list_cache: dict[int, dict] = {}
# Structure
# user_id: {
# "user_name": str,
#  "pokemeow_name": str,
# }
#

channel_placement_cache: dict[int, dict] = {}
# Structure:
# channel_id -> {
#   "user_id": int,
#   "user_name": str,
#   "catches": int,
# }


# Variables

processed_clan_members_msg_ids = set()  # To track processed messages and avoid reprocessing