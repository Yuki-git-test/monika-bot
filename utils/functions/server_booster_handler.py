import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    KHY_USER_ID,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.custom_roles_db_func import (
    fetch_custom_role_id,
    remove_role,
    update_gradient_role,
    upsert_role,
)
from utils.logs.pretty_log import pretty_log
from utils.visuals.colors import get_random_monika_color
from utils.logs.debug_log import debug_log, enable_debug
from utils.functions.webhook_func import send_webhook

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log
REFERENCE_ROLE_ID = VN_ALLSTARS_ROLES.personal_roles_divider
PEACH_SERVER_BOOSTER_ICON_URL = "https://media.discordapp.net/attachments/1394913073520967680/1441576187099877529/ChatGPT_Image_Nov_22_2025_07_44_57_AM.png?ex=69224bf2&is=6920fa72&hm=bcfec42a965eb116e5dba345a4c3b68788e03adad7d9b0f532d848232fa6d0da&=&format=webp&quality=lossless&width=855&height=855"


TEST_ROLE_ID = 1013465409049067632

enable_debug(f"{__name__}.safe_set_role_position")
# 🍭──────────────────────────────
#   🎀 Handle Server Booster Role Removal
# 🍭──────────────────────────────
async def handle_server_booster_role_remove(
    bot: discord.Client,
    member: discord.Member,
):
    """Delete custom role when server booster role is removed."""

    # Make exemption for staff members
    staff_role = member.guild.get_role(VN_ALLSTARS_ROLES.staff)
    seafoam_role = member.guild.get_role(VN_ALLSTARS_ROLES.seafoam)
    if staff_role in member.roles or seafoam_role in member.roles:
        pretty_log(
            message=f"Member '{member.display_name}' is staff; skipping custom role deletion on server booster removal.",
            tag="info",
            label="Server Booster Role Remove",
        )
        return

    # Fetch custom role ID from DB
    custom_role_id = await fetch_custom_role_id(bot, member)
    if custom_role_id:
        # Check if custom role exists in guild
        custom_role = member.guild.get_role(custom_role_id)
        if custom_role:
            try:
                # Delete the custom role
                await custom_role.delete(reason="Server booster role removed.")
                pretty_log(
                    message=f"Deleted custom role '{custom_role.name}' for member '{member.display_name}' after server booster role removal.",
                    tag="success",
                    label="Server Booster Role Remove",
                )
            except Exception as e:
                pretty_log(
                    message=f"Failed to delete custom role '{custom_role.name}' for member '{member.display_name}': {e}",
                    tag="error",
                )
        # Remove from DB
        await remove_role(bot, member)
        pretty_log(
            message=f"Removed custom role record from database for member '{member.display_name}' after server booster role removal.",
            tag="info",
            label="Server Booster Role Remove",
        )


async def safe_set_role_position(guild, role, reference_role, bot):
    ref_pos = reference_role.position
    bot_pos = guild.me.top_role.position
    role_pos = role.position
    bot_member = guild.me
    perms = bot_member.guild_permissions



    debug_log(f"[RoleMove] Bot: {bot_member.display_name} (ID: {bot_member.id})")
    debug_log(f"[RoleMove] Bot top role: {bot_member.top_role.name} (pos: {bot_pos})")
    debug_log(f"[RoleMove] Reference role: {reference_role.name} (pos: {ref_pos})")
    debug_log(f"[RoleMove] Target role: {role.name} (pos: {role_pos})")
    debug_log(
        f"[RoleMove] Bot permissions: manage_roles={perms.manage_roles}, administrator={perms.administrator}"
    )

    if not perms.manage_roles:
        pretty_log(
            message=f"Bot lacks 'Manage Roles' permission. Cannot move role.",
            tag="error",
        )
        return

    if bot_pos <= ref_pos:
        pretty_log(
            message=f"Bot top role ({bot_pos}) is not above reference role ({ref_pos}); cannot move role.",
            tag="error",
        )
        return

    if bot_pos <= role_pos:
        pretty_log(
            message=f"Bot top role ({bot_pos}) is not above target role ({role_pos}); cannot move role.",
            tag="error",
        )
        return

    try:
        await role.edit(position=ref_pos - 1)
        # Fetch updated role position
        updated_role = guild.get_role(role.id)
        debug_log(
            f"[RoleMove] Role '{updated_role.name}' new position: {updated_role.position}"
        )
        pretty_log(
            message=f"Moved role '{role.name}' below reference role '{reference_role.name}'.",
            tag="success",
        )
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        pretty_log(
            message=f"Failed to move role '{role.name}': {e}\nTraceback:\n{tb}",
            tag="error",
        )


# 🍭──────────────────────────────
#   🎀 Handle Server Booster Role Addition
# 🍭──────────────────────────────
async def handle_server_booster_role_add(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role = None,
):
    """Handle server booster role addition events."""

    # If test role id and member is khy delete the old role in server and db
    testing = False
    if role and role.id == TEST_ROLE_ID and member.id == KHY_USER_ID:
        testing = True
        custom_role_id = await fetch_custom_role_id(bot, member)
        if custom_role_id:
            custom_role = member.guild.get_role(custom_role_id)
            if custom_role:
                try:
                    await custom_role.delete(reason="Removing test custom role.")
                    pretty_log(
                        message=f"Deleted test custom role '{custom_role.name}' for member '{member.display_name}'.",
                        tag="success",
                        label="Test Role Cleanup",
                    )
                except Exception as e:
                    pretty_log(
                        message=f"Failed to delete test custom role '{custom_role.name}': {e}",
                        tag="error",
                    )
            await remove_role(bot, member)
            pretty_log(
                message=f"Removed test custom role record from database for member '{member.display_name}'.",
                tag="info",
                label="Test Role Cleanup",
            )

    #  Check if the member already has a custom role
    context = "new custom role"
    guild = member.guild
    first_line_str = ""
    role = None
    reference_role = guild.get_role(REFERENCE_ROLE_ID)
    custom_role_id = await fetch_custom_role_id(bot, member)
    if custom_role_id:
        # Check if custom role exists in guild
        custom_role = guild.get_role(custom_role_id)
        if custom_role:
            # Check if member has their custom role
            if custom_role not in member.roles:
                try:
                    # Restore Custom Role Branch
                    await member.add_roles(
                        custom_role, reason="Restoring custom role after server boost."
                    )
                    pretty_log(
                        message=f"Restored custom role '{custom_role.name}' to member '{member.display_name}' after server boost.",
                        tag="success",
                        label="Server Booster Role Add",
                    )
                    context = "restored custom role"
                    first_line_str = f"Your custom role {custom_role.mention} has been reassigned to you.\n"
                    log_embed_title = "🎉 Custom Role Reassigned"
                    role = custom_role

                except Exception as e:
                    pretty_log(
                        message=f"Failed to restore custom role '{custom_role.name}' to member '{member.display_name}': {e}",
                        tag="error",
                    )
            # If member already has the role branch
            elif custom_role in member.roles:
                context = "existing custom role"
                first_line_str = f"Your custom role {custom_role.mention} is already assigned to you.\n"
                role = custom_role
                pretty_log(
                    message=f"Member '{member.display_name}' already has their custom role '{custom_role.name}' after server boost.",
                    tag="info",
                    label="Server Booster Role Add",
                )

        else:
            # If the custom role does not exist, remove it from the database and create a new one
            await remove_role(bot, member)
            # Log removal of stale custom role
            pretty_log(
                message=f"Removed stale custom role record for member '{member.display_name}' as the role no longer exists.",
                tag="info",
                label="Server Booster Role Add",
            )
            context = "new custom role"

    # Create a new custom role
    if context == "new custom role":
        role_name = member.name

        try:
            new_role = await guild.create_role(
                name=role_name,
                reason="Creating custom role after server boost.",
                mentionable=False,
            )
            await asyncio.sleep(
                1
            )  # Small delay to ensure role is created before positioning
            try:
                # Use safe helper here
                await safe_set_role_position(guild, new_role, reference_role, bot)
                pretty_log(
                    message=f"Set position for new custom role '{new_role.name}' to {reference_role.position - 1}.",
                    tag="success",
                )
            except Exception as e:
                pretty_log(
                    message=f"Failed to set position for new custom role '{new_role.name}': {e}",
                    tag="error",
                )
            await member.add_roles(
                new_role, reason="Assigning custom role after server boost."
            )
            # Save to DB
            await upsert_role(bot=bot, user=member, role_id=new_role.id)
            pretty_log(
                message=f"Created and assigned new custom role '{new_role.name}' to member '{member.display_name}' after server boost.",
                tag="success",
                label="Server Booster Role Add",
            )
            first_line_str = f"As a token of our appreciation, we've created a custom role for you: {new_role.mention}.\n"
            log_embed_title = "🎉 Custom Role Created"
            log_embed_description = (
                f"**Member:** {member.mention}\n" f"**Role:** {new_role.mention}\n"
            )
            role = new_role
            description = (
                f"{first_line_str}"
                f"Feel free to customize it, using `/custom-role edit` and `/custom-role edit-icon`\n"
                f"You can check out your the rest of your perks in <#{VN_ALLSTARS_TEXT_CHANNELS.perks}>"
            )
        except Exception as e:
            pretty_log(
                message=f"Failed to create or assign custom role for member '{member.display_name}': {e}",
                tag="error",
            )
            return

    # Don't send messages or logs if testing
    if testing:
        return

    # Build embed
    content = f"{member.mention} Thank you for boosting the server! 🎉"
    color = get_random_monika_color()
    if context == "restored custom role":
        color = role.color

    embed = discord.Embed(
        description=description,
        color=color,
        timestamp=datetime.now(),
    )
    thumbnail_url = PEACH_SERVER_BOOSTER_ICON_URL
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)

    # Send message in General Channel
    general_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.general)
    if general_channel:
        await general_channel.send(content=content, embed=embed)

        if context != "existing custom role":
            # Log in Server Log Channel
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title=log_embed_title,
                    description=log_embed_description,
                    color=color,
                    timestamp=datetime.now(),
                )
                log_embed.set_author(
                    name=member.display_name, icon_url=member.display_avatar.url
                )
                log_embed.set_footer(
                    text=guild.name,
                    icon_url=guild.icon.url if guild.icon else None,
                )
                await send_webhook(
                    bot=bot,
                    channel=log_channel,
                    embed=log_embed,
                )
