import asyncio
import re
from datetime import datetime

import discord

from constants.aesthetic import Emojis
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.vna_members_db_func import upsert_member
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.move_to_members_category")
enable_debug(f"{__name__}.clan_members_command_listener")

extracted_members_list = []
pages_seen = set()  # To track seen pages and avoid duplicates

PRO_MEMBERS_CATEGORY_ID = 1381773427362234488
STAFF_ROLE_IDS = [VN_ALLSTARS_ROLES.staff, VN_ALLSTARS_ROLES.senior_mod]

CLAN_MEMBER_CATEGORY_ONE_ID = 909881910505898044
CLAN_MEMBER_CATEGORY_TWO_ID = 1456263954526371861
STAFF_CATEGORY_ID = 1234042069991821386
CATCH_CATEGORY_MAP = {
    "Pro Members": {"category_id": PRO_MEMBERS_CATEGORY_ID, "min_catches": 100000},
    "Clan Members 1": {
        "category_id": CLAN_MEMBER_CATEGORY_ONE_ID,
        "min_catches": 50000,
    },
    "Clan Members 2": {"category_id": CLAN_MEMBER_CATEGORY_TWO_ID, "min_catches": 0},
}

import re

TESTING_CHECK_MEMBERS = True


def extract_page_numbers(text):
    match = re.search(r"Page\s*(\d+)\s*/\s*(\d+)", text)
    if match:
        current_page = int(match.group(1))
        total_pages = int(match.group(2))
        return current_page, total_pages
    return None, None


async def move_to_members_category(
    bot, member: discord.Member, channel: discord.TextChannel, context: str
):
    """Move the given channel to the Pro Members category. If member has reached 100k catches."""
    debug_log(
        f"Called with channel={channel.name}, member={member.name}, context={context}"
    )
    # debug_log(f"Member roles: {[role.id for role in member.roles]}")
    debug_log(f"Channel category: {channel.category.id if channel.category else None}")
    shiny_donator_role = member.guild.get_role(VN_ALLSTARS_ROLES.shiny_donator)

    target_category_id = CATCH_CATEGORY_MAP.get(context, {}).get("category_id")
    if not target_category_id:
        debug_log(f"Invalid context '{context}' - no target_category_id found.")
        pretty_log(
            "error",
            f"Invalid context '{context}' provided for moving channel {channel.name}.",
        )
        return
    # Check if its already in target category
    if channel.category and channel.category.id == target_category_id:
        debug_log(
            f"Channel {channel.name} already in target category {target_category_id}."
        )
        pretty_log(
            "info",
            f"Channel {channel.name} is already in {context} category.",
        )
        return

    # Check if staff member
    if any(role.id in STAFF_ROLE_IDS for role in member.roles):
        debug_log(f"Member {member.name} is staff. Skipping move.")
        pretty_log(
            "info",
            f"Member {member.name} is a staff member. Skipping move.",
        )
        return

    # Check if in staff category, if yes dnt move
    if channel.category and channel.category.id == STAFF_CATEGORY_ID:
        debug_log(f"Channel {channel.name} is in staff category. Skipping move.")
        pretty_log(
            "info",
            f"Channel {channel.name} is in Staff category. Skipping move.",
        )
        return

    # Check if has shiny donator role, if yes dnt move
    if shiny_donator_role and shiny_donator_role in member.roles:
        debug_log(f"Member {member.name} has shiny donator role. Skipping move.")
        pretty_log(
            "info",
            f"Member {member.name} has Shiny Donator role. Skipping move.",
        )
        return

    try:
        target_members_category = channel.guild.get_channel(target_category_id)
        if target_members_category is None:
            debug_log(
                f"Target members category with ID {target_category_id} not found."
            )
            pretty_log(
                "error",
                f" Members category with ID {target_category_id} not found in guild {channel.guild.name}.",
            )
            return
        debug_log(
            f"Moving channel {channel.name} to category {target_members_category.name}."
        )
        await channel.edit(category=target_members_category)
        pretty_log(
            "info",
            f"Channel {channel.name} moved to {target_members_category.name} Category in guild {channel.guild.name}.",
        )
        log_channel = channel.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
        if log_channel:
            min_catches = CATCH_CATEGORY_MAP[context]["min_catches"]
            reason_str = (
                f"Reached {min_catches:,} catches"
                if min_catches > 0
                else "Haven't reached 50k catches"
            )
            embed = discord.Embed(
                title=f"Channel Moved to {target_members_category.name} Category",
                description=(
                    f"**Member:** {member.mention} ({member.name})\n"
                    f"**Channel:** {channel.mention}\n"
                    f"**Reason:** {reason_str}"
                ),
                color=MONIKA_EMBED_COLOR,
                timestamp=datetime.now(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )
            embed.set_footer(
                text=f"User ID: {member.id}",
                icon_url=channel.guild.icon.url if channel.guild.icon else None,
            )
            await send_webhook(bot=bot, channel=log_channel, embed=embed)

    except Exception as e:
        debug_log(f"Exception occurred: {e}")
        pretty_log(
            "error",
            f"Error moving channel {channel.name} to Pro Members category: {e}",
        )
        return


def get_username_from_line(user_line):
    # Remove bold and whitespace
    cleaned = user_line.replace("**", "").strip()
    # Try to match patterns like '<@id> - id}' or '<@id> - id' or just 'id'
    # Regex for <@digits> - digits (with or without trailing })
    match = re.match(r"\d+\s+<@(?P<uid1>\d+)>\s*-\s*(?P<uid2>\d+)}?", cleaned)
    if match:
        # Always use the second ID after the dash for cache lookup
        user_id = int(match.group("uid2"))
        return str(user_id)
    # Try to match just <@id> - id (without leading number)
    match2 = re.match(r"<@(?P<uid1>\d+)>\s*-\s*(?P<uid2>\d+)}?", cleaned)
    if match2:
        user_id = int(match2.group("uid2"))
        return str(user_id)
    # Fallback: try to extract last word as user id if it's all digits
    parts = cleaned.split()
    if parts and re.fullmatch(r"\d{10,}", parts[-1]):
        user_id = int(parts[-1])
        return str(user_id)
    # Otherwise, fallback to original logic: everything after first space
    user_name = cleaned.split(" ", 1)[-1] if " " in cleaned else cleaned
    return user_name


def get_member_from_line(guild: discord.Guild, user_line):
    """Extract member object from user line in embed."""
    cleaned = user_line.replace("**", "").strip()
    # Try to match patterns like '<@id> - id}' or '<@id> - id' or just 'id'
    # Regex for <@digits> - digits (with or without trailing })
    match = re.match(r"\d+\s+<@(?P<uid1>\d+)>\s*-\s*(?P<uid2>\d+)}?", cleaned)
    if match:
        # Always use the second ID after the dash for cache lookup
        user_id = int(match.group("uid2"))
        member = guild.get_member(user_id)
        if member:
            return member, user_id
        else:
            return None, user_id

    # Try to match just <@id> - id (without leading number)
    match2 = re.match(r"<@(?P<uid1>\d+)>\s*-\s*(?P<uid2>\d+)}?", cleaned)
    if match2:
        user_id = int(match2.group("uid2"))
        member = guild.get_member(user_id)
        if member:
            return member, user_id
        else:
            return None, user_id

    # Fallback: try to extract last word as user id if it's all digits
    parts = cleaned.split()
    if parts and re.fullmatch(r"\d{10,}", parts[-1]):
        user_id = int(parts[-1])
        member = guild.get_member(user_id)
        return member
    # Otherwise, fallback to original logic: everything after first space
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    user_name = cleaned.split(" ", 1)[-1] if " " in cleaned else cleaned
    user_id = fetch_vna_member_id_by_username_or_pokemeow_name(user_name)
    if user_id:
        member = guild.get_member(user_id)
        return member, user_id
    else:
        return None, user_id


async def clan_members_command_listener(
    bot, message: discord.Message, msg_context: str = None
):
    """Listener for clan members command."""

    debug_log(f"Called with message.id={message.id}, msg_context={msg_context}")
    processsing_msg = None
    if msg_context and msg_context == "reply":
        debug_log("Message context is reply, fetching replied message.")
        replied_message = message.reference.resolved
        if replied_message:
            debug_log("Replied message found.")
            message = replied_message
            processsing_msg = await replied_message.reply(
                f"{Emojis.orange_loading} Sorting channels...", mention_author=False
            )
    elif msg_context and msg_context == "check_members":
        debug_log("Message context is reply, fetching replied message.")
        replied_message = message.reference.resolved
        if replied_message:
            debug_log("Replied message found.")
            message = replied_message
            processsing_msg = await replied_message.reply(
                f"{Emojis.orange_loading} Checking members...", mention_author=False
            )

        else:
            debug_log("No replied message found.")
            return

    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log("No embed found in message.")

        return

    embed_description = embed.description or ""
    if "Clan Member Information - VN Allstar" not in embed_description:
        debug_log("Embed does not contain expected description header.")
        return

    vna_guild = bot.get_guild(VNA_SERVER_ID)
    if not vna_guild:
        debug_log(f"VNA guild with ID {VNA_SERVER_ID} not found.")
        pretty_log(
            "error",
            f"VNA guild with ID {VNA_SERVER_ID} not found.",
        )
        return

    user_lines = embed.fields[0].value.splitlines()
    contribution_line = embed.fields[1].value.splitlines()

    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    vna_member_cache_ids = set(vna_members_cache.keys())
    # Exctract page numbers to avoid processing duplicates when reactions are added
    current_page, total_pages = extract_page_numbers(embed.footer.text)
    pretty_log(
        "info",
        f"Processing clan members command for page {current_page} of {total_pages}.",
    )
    for user_line, contrib_line in zip(user_lines, contribution_line):
        debug_log(f"Processing user_line: {user_line}, contrib_line: {contrib_line}")
        user_name = user_line.split(" ", 1)[-1].replace("**", "").strip()
        member, user_id = get_member_from_line(vna_guild, user_line)

        # Put to extracted members list for future reference
        if user_id not in extracted_members_list:
            debug_log(f"Adding user ID {user_id} to extracted members list.")
            extracted_members_list.append(user_id)

        if user_id not in vna_member_cache_ids:
            debug_log(
                f"User ID {user_id} extracted from embed but not found in VNA members cache."
            )
            pretty_log(
                "info",
                f"User ID {user_id} extracted from embed but not found in VNA members cache.",
            )
            if not member:
                # Fetch user for better logging
                user = bot.get_user(user_id) or await bot.fetch_user(user_id)
                # Upsert with minimal info to avoid missing members in future checks
                try:
                    await upsert_member(bot, user)
                    await message.channel.send(
                        f"User {user.name} (ID: {user_id}) was listed in the clan members embed but not found in the VNA members cache. They have now been added to the database for future reference."
                    )
                except Exception as e:
                    debug_log(f"Error upserting member with user ID {user_id}: {e}")
                    pretty_log(
                        "error",
                        f"Error upserting member with user ID {user_id}: {e}",
                    )
                    await message.channel.send(
                        f"Error upserting member with user ID {user_id}: {e}"
                    )

        if not member:
            debug_log(f"Member for user line '{user_line}' not found in VNA guild.")
            pretty_log(
                "info",
                f"Member for user line '{user_line}' not found in VNA guild.",
            )
            continue
        if not TESTING_CHECK_MEMBERS:
            debug_log("TESTING_CHECK_MEMBERS is False, skipping channel sort process.")

            # Extract catches from contribution line
            contrib_match = re.search(r"> ?\*?\*?([\d,]+)", contrib_line)
            catches = (
                int(contrib_match.group(1).replace(",", "")) if contrib_match else None
            )

            # Get info
            user_id = member.id
            member_info = vna_members_cache.get(user_id)
            if not member_info:
                debug_log(f"Member info for user ID {user_id} not found in cache.")
                pretty_log(
                    "info",
                    f"Member info for user ID {user_id} not found in VNA members cache.",
                )
                continue

            channel_id = member_info.get("channel_id")
            if not channel_id:
                debug_log(f"Channel ID for user ID {user_id} not found in cache.")
                pretty_log(
                    "info",
                    f"Channel ID for user ID {user_id} not found in VNA members cache.",
                )
                continue
            channel = vna_guild.get_channel(channel_id)
            if not channel:
                debug_log(f"Channel with ID {channel_id} not found in VNA guild.")
                pretty_log(
                    "info",
                    f"Channel with ID {channel_id} not found in VNA guild.",
                )
                continue
            # Move to Pro Members category if catches >= 100000
            debug_log(f"Member {member.name} has {catches} catches.")
            if catches is not None and catches >= 100000:
                await move_to_members_category(
                    bot, member, channel, context="Pro Members"
                )
            elif catches is not None and 50000 <= catches < 100000:
                await move_to_members_category(
                    bot, member, channel, context="Clan Members 1"
                )
            elif catches is not None and catches < 50000:
                await move_to_members_category(
                    bot, member, channel, context="Clan Members 2"
                )

            # Sleep for 3 seconds between moves to avoid rate limits
            await asyncio.sleep(3)

    debug_log("Processing completed.")
    pretty_log(
        "info",
        "Clan members command listener processing completed.",
    )
    if current_page in pages_seen:
        debug_log(
            f"Page {current_page} already processed, skipping duplicate processing."
        )
        return

    pages_seen.add(current_page)  # Mark this page as seen to avoid duplicate processing
    debug_log(f"Added page {current_page} to seen pages: {pages_seen}")
    if current_page is not None and total_pages is not None:
        if (current_page == total_pages and processsing_msg is None) or (
            processsing_msg
            and msg_context == "check_members"
            and len(pages_seen) == total_pages
        ):
            debug_log("Last page processed, sending completion message.")
            # Members not in clan
            non_clan_members = []
            debug_log(f"Checking extracted_members_list: {extracted_members_list}")
            cache_keys_sample = list(vna_members_cache.keys())[:4]
            debug_log(
                f"vna_members_cache keys sample: {cache_keys_sample} (showing 4 of {len(vna_members_cache)})"
            )

            for user_id in vna_member_cache_ids:
                debug_log(f"Checking user_id: {user_id}")
                if user_id not in extracted_members_list:
                    debug_log(f"User ID {user_id} NOT found in vna_members_cache.")
                    # Get user object for better logging
                    user = bot.get_user(user_id) or await bot.fetch_user(user_id)
                    non_clan_member_line = f"{user.name} (ID: {user_id})"
                    non_clan_members.append(non_clan_member_line)
                    # pretty_log(
                    #     "info",
                    #     f"User {user.name} (ID: {user_id}) listed in clan members embed but not found in VNA members cache.",
                    # )
                else:
                    debug_log(f"User ID {user_id} found in vna_members_cache.")

            if non_clan_members:
                embed = discord.Embed(
                    title="Non-Clan Members Detected",
                    description=(
                        "The following members were listed in the clan members embed but were not found in the VNA members cache. This likely means they are not actually in the clan or there is a mismatch in usernames.\n\nKindly do the command `;stats <user_id>` to verify\n\n"
                        + "\n".join(non_clan_members)
                    ),
                    color=MONIKA_EMBED_COLOR,
                    timestamp=datetime.now(),
                )

                if processsing_msg:
                    await processsing_msg.edit(
                        content=f"{Emojis.orange_check} Member check completed with discrepancies found.",
                        embed=embed,
                    )
                else:
                    await message.channel.send(embed=embed)
                debug_log(f"Non-clan members detected: {', '.join(non_clan_members)}")
                # pretty_log(
                #     "info",
                #     f"Non-clan members detected: {', '.join(non_clan_members)}",
                # )
            else:
                if processsing_msg:
                    await processsing_msg.edit(
                        content=f"{Emojis.orange_check} Member check completed! No discrepancies found.",
                    )
                debug_log("Member check completed with no discrepancies found.")
                # pretty_log(
                #     "info",
                #     "Member check completed with no discrepancies found.",
                # )
            # pages_seen.clear()  # Clear seen pages for next time
    if processsing_msg and msg_context == "check_members":
        await processsing_msg.edit(
            content=f"{Emojis.orange_check} Member check completed! Processed {len(pages_seen)} pages."
        )
    if processsing_msg and msg_context == "reply":
        # Get category channel number
        pro_members_category = vna_guild.get_channel(PRO_MEMBERS_CATEGORY_ID)
        clan_member_one_category = vna_guild.get_channel(CLAN_MEMBER_CATEGORY_ONE_ID)
        clan_member_two_category = vna_guild.get_channel(CLAN_MEMBER_CATEGORY_TWO_ID)
        pro_members_channel_count = (
            len(pro_members_category.channels) if pro_members_category else 0
        )
        clan_member_one_channel_count = (
            len(clan_member_one_category.channels) if clan_member_one_category else 0
        )
        clan_member_two_channel_count = (
            len(clan_member_two_category.channels) if clan_member_two_category else 0
        )
        embed = discord.Embed(
            title="Sorting Completed!",
            description=(
                f"**Pro Members Category Channels:** {pro_members_channel_count}\n"
                f"**Clan Members 1 Category Channels:** {clan_member_one_channel_count}\n"
                f"**Clan Members 2 Category Channels:** {clan_member_two_channel_count}\n"
            ),
            color=MONIKA_EMBED_COLOR,
            timestamp=datetime.now(),
        )
        await processsing_msg.edit(
            content=f"{Emojis.orange_check} Sorting completed!", embed=embed
        )
