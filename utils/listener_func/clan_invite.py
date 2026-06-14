import re

import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.vna_members_db_func import upsert_member
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.auto_clan_invite")
image_url = "https://media.discordapp.net/attachments/.../image.png"

CLAN_MEMBER_CATEGORY_ONE_ID = 909881910505898044
CLAN_MEMBER_CATEGORY_TWO_ID = 1456263954526371861

CATEGORY_CHANNEL_LIMIT = 50


# 🟣────────────────────────────────────────────
#      🗂️ Category Overflow Helper
# 🟣────────────────────────────────────────────
async def get_or_create_available_category(
    guild: discord.Guild,
    base_category_id: int,
) -> discord.CategoryChannel | None:
    """
    Returns a category that has room for a new channel (< 50).
    If the base category is full, searches for another category with
    the same name that has space. If none found, creates a new one
    with the same name and permission overwrites as the base category.
    """
    base_category = guild.get_channel(base_category_id)
    if not base_category:
        return None

    if len(base_category.channels) < CATEGORY_CHANNEL_LIMIT:
        return base_category

    # Base is full — look for a same-named category with room
    for category in guild.categories:
        if (
            category.name == base_category.name
            and len(category.channels) < CATEGORY_CHANNEL_LIMIT
        ):
            return category

    # All matching categories are full — create a new overflow category
    new_category = await guild.create_category(
        name=base_category.name,
        overwrites=dict(base_category.overwrites),
        reason="Clan member category overflow — previous category is full",
    )
    return new_category


# 🟣────────────────────────────────────────────
#          ⚡ Auto Clan Invite ⚡
# 🟣────────────────────────────────────────────
async def auto_clan_invite(bot: discord.Client, message: discord.Message):
    """
    Automatically creates a channel when a user accepts the clan invite.
    """

    if (
        ":tada: Welcome," in message.content
        and "You have successfully joined" in message.content
    ):
        debug_log("Auto Clan Invite triggered")
        user_mention_pattern = r"<@(\d+)>"
        debug_log(f"Searching for user mention in message: {message.content}")
        match = re.search(user_mention_pattern, message.content)
        pokemeow_name = "N/A"

        if not match:
            pretty_log("info", "No user mention found in the message")
            debug_log("No user mention found in the message content.")
            return

        user_id = match.group(1)
        pretty_log(f"Extracted User ID: {user_id}")
        debug_log(f"Extracted User ID: {user_id}")

        try:
            debug_log(f"Attempting to fetch user with ID: {user_id}")

            user = await bot.fetch_user(int(user_id))
            pretty_log(f"User found: {user.display_name} ({user.name})")
            debug_log(f"Fetched user: {user.display_name} ({user.name})")
            pokemeow_name = user.name

            replied_message = message.reference.resolved if message.reference else None
            if replied_message and replied_message.content:
                debug_log(f"Found replied message: {replied_message.content}")
                match = re.search(
                    r"has invited \\*\\*(.*?)\\*\\* to join", replied_message.content
                )
                if match:
                    pokemeow_name = match.group(1)
                    debug_log(
                        f"Extracted pokemeow_name from replied message: {pokemeow_name}"
                    )

            guild = message.guild
            member = guild.get_member(user.id)
            if not member:
                pretty_log(
                    "error", f"User {user.display_name} is not a member of the guild."
                )
                debug_log(f"User {user.display_name} is not a member of the guild.")
                return

            invoked_message = message.reference.resolved if message.reference else None
            processing_msg = None
            if invoked_message:
                processing_msg = await invoked_message.reply(
                    f"{Emojis.orange_loading} Making clan channel for {member.mention}..."
                )
            debug_log(f"Guild: {guild.name} ({guild.id})")
            # Roles
            vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
            lottery_role = guild.get_role(VN_ALLSTARS_ROLES.lottery)
            giveaway_role = guild.get_role(VN_ALLSTARS_ROLES.giveaways)
            announcment_role = guild.get_role(VN_ALLSTARS_ROLES.announcments)
            staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
            bots_role = guild.get_role(VN_ALLSTARS_ROLES.bots)
            pokemeow_bot = guild.get_member(POKEMEOW_APP_ID)

            debug_log(
                f"Roles resolved: vna_member_role={vna_member_role}, lottery_role={lottery_role}, giveaway_role={giveaway_role}, announcment_role={announcment_role}, staff_role={staff_role}, bots_role={bots_role}, pokemeow_bot={pokemeow_bot}"
            )

            # Permission overwrites
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(
                    view_channel=True,
                    manage_channels=True,
                    send_messages=True,
                    manage_messages=True,
                    send_messages_in_threads=True,
                    create_public_threads=True,
                    attach_files=True,
                    manage_threads=True,
                ),
                staff_role: discord.PermissionOverwrite(
                    view_channel=True,
                    manage_channels=True,
                    manage_messages=True,
                    manage_threads=True,
                ),
                bots_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                ),
                pokemeow_bot: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                ),
            }
            debug_log(f"Permission overwrites set for new channel.")

            # Channel creation
            channel_name = f"《👾》{member.name}"
            channel_topic = (
                "This is your personal channel!! You may use this however you like."
            )
            debug_log(
                f"Creating text channel: {channel_name} in category {CLAN_MEMBER_CATEGORY_TWO_ID}"
            )
            try:
                target_category = await get_or_create_available_category(
                    guild=guild,
                    base_category_id=CLAN_MEMBER_CATEGORY_TWO_ID,
                )
                debug_log(
                    f"Target category resolved: {target_category.name if target_category else 'None'} ({target_category.id if target_category else 'N/A'})"
                )
                new_channel = await guild.create_text_channel(
                    name=channel_name,
                    topic=channel_topic,
                    category=target_category,
                    overwrites=overwrites,
                )
                pretty_log(
                    "success",
                    f"Channel '{new_channel.name}' created for user {member.display_name}",
                    label="Auto Clan Invite",
                )
                debug_log(
                    f"Channel '{new_channel.name}' created for user {member.display_name}"
                )
            except Exception as e:
                pretty_log(
                    "error",
                    f"Failed to create channel for user {member.display_name}: {e}",
                    label="Auto Clan Invite",
                )
                debug_log(
                    f"Failed to create channel for user {member.display_name}: {e}"
                )
                if processing_msg:
                    await processing_msg.delete()
                return

            # Upsert member into DB
            debug_log(
                f"Upserting member into DB: user={member}, channel_id={new_channel.id}, pokemeow_name={pokemeow_name}"
            )
            await upsert_member(
                bot=bot,
                user=member,
                channel_id=new_channel.id,
                pokemeow_name=pokemeow_name,
            )

            # Assign roles
            debug_log(f"Assigning roles to user {member.display_name}")
            await member.add_roles(
                vna_member_role,
                lottery_role,
                giveaway_role,
                announcment_role,
                reason="Auto role assignment on clan join",
            )

            # Success embed
            desc = f"Successfully assigned {vna_member_role.mention} to {member.mention} and given access to your personal channel {new_channel.mention}!"
            embed = discord.Embed(description=desc, color=0xFF00EE)
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.set_image(url=image_url)
            debug_log(f"Sending success embed to channel {message.channel}")
            if processing_msg:
                await processing_msg.delete()
            await message.channel.send(embed=embed)

            pretty_log(
                "success",
                f"Assigned roles to {member.display_name} and created channel {new_channel.name}",
                label="Auto Clan Invite",
            )
            debug_log(
                f"Assigned roles to {member.display_name} and created channel {new_channel.name}"
            )
            clan_channel_category_id = new_channel.category_id
            clan_channel_category = guild.get_channel(clan_channel_category_id)

            channel_category_count = 0
            if clan_channel_category:
                channel_category_count = len(clan_channel_category.channels)

            category_str = f"**Category:** {clan_channel_category.name} with {channel_category_count} channels"
            debug_log(f"Channel category info: {category_str}")

            # Log embed
            log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
            debug_log(f"Log channel resolved: {log_channel}")
            if log_channel:
                log_embed_description = f"**Member:** {member.mention}\n**Pokemeow Name:**{pokemeow_name}\n**Channel:** {new_channel.mention}\n{category_str}"
                debug_log(f"Log embed description: {log_embed_description}")
                log_embed = discord.Embed(
                    title="New Clan Member Joined",
                    url=message.jump_url,
                    description=log_embed_description,
                    color=0xFF00EE,
                )
                log_embed.set_thumbnail(url=member.display_avatar.url)
                log_embed.set_author(
                    name=member.display_name, icon_url=member.display_avatar.url
                )
                log_embed.set_footer(
                    text=f"User ID: {member.id}",
                    icon_url=guild.icon.url if guild.icon else None,
                )
                debug_log(f"Sending log embed to webhook in log channel.")
                await send_webhook(bot=bot, channel=log_channel, embed=log_embed)

        except discord.NotFound:
            pretty_log("error", f"User with ID {user_id} not found")
            debug_log(f"User with ID {user_id} not found (discord.NotFound)")
        except Exception as e:
            pretty_log("error", f"Error fetching user: {e}")
            debug_log(f"Exception occurred: {e}")
