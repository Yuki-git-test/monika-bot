from datetime import datetime

import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
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

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log
REFERENCE_ROLE_ID = VN_ALLSTARS_ROLES.personal_roles_divider
PEACH_SERVER_BOOSTER_ICON_URL = "https://media.discordapp.net/attachments/1394913073520967680/1441576187099877529/ChatGPT_Image_Nov_22_2025_07_44_57_AM.png?ex=69224bf2&is=6920fa72&hm=bcfec42a965eb116e5dba345a4c3b68788e03adad7d9b0f532d848232fa6d0da&=&format=webp&quality=lossless&width=855&height=855"


# 🍭──────────────────────────────
#   🎀 Handle Server Booster Role Addition
# 🍭──────────────────────────────
async def handle_server_booster_role_add(
    bot: discord.Client,
    member: discord.Member,
):
    """Handle server booster role addition events."""
    #  Check if the member already has a custom role
    context = "new custom role"
    guild = member.guild
    first_line_str = ""
    role = None
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
        CUSTOM_ROLE_POSITION = guild.get_role(REFERENCE_ROLE_ID).position - 1
        try:
            new_role = await guild.create_role(
                name=role_name,
                reason="Creating custom role after server boost.",
                mentionable=False,
            )
            try:
                await new_role.edit(position=CUSTOM_ROLE_POSITION)
                pretty_log(
                    message=f"Set position for new custom role '{new_role.name}' to {CUSTOM_ROLE_POSITION}.",
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

        except Exception as e:
            pretty_log(
                message=f"Failed to create or assign custom role for member '{member.display_name}': {e}",
                tag="error",
            )
            return
        description = (
            f"{first_line_str}"
            f"Feel free to customize it, using `/custom-role edit` and `/custom-role edit-icon`\n"
            f"You can check out your the rest of your perks in <#{VN_ALLSTARS_TEXT_CHANNELS.perks}>"
        )
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
        embed.set_footer(
            name=guild.name, icon_url=guild.icon.url if guild.icon else None
        )
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
                        name=guild.name, icon_url=guild.icon.url if guild.icon else None
                    )
                    await log_channel.send(embed=log_embed)
