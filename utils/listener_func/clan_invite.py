import re

import discord
from utils.functions.webhook_func import send_webhook
from constants.vn_allstars_constants import (
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.logs.pretty_log import pretty_log
image_url = "https://media.discordapp.net/attachments/1220786720082235403/1382956264102826004/image.png?ex=684d09e3&is=684bb863&hm=8e69e66a6897337d74b88efac9a84b6ad95e1dc42b6cc269ea352e9e766d0299&=&format=webp&quality=lossless&width=1600&height=128"

# 🟣────────────────────────────────────────────
#          ⚡ Auto Clan Invite ⚡
# 🟣────────────────────────────────────────────
async def auto_clan_invite(bot: discord.Client, message: discord.Message):
    """
    Automatically creates a channel when a user accepts the clan invite.
    """

    # Check if this is a clan join success message
    if (
        ":tada: Welcome," in message.content
        and "You have successfully joined" in message.content
    ):
        # Extract user ID from the mention format <@USER_ID>
        user_mention_pattern = r"<@(\d+)>"
        match = re.search(user_mention_pattern, message.content)

        if match:
            user_id = match.group(1)  # Get the captured group (the user ID)
            pretty_log(f"Extracted User ID: {user_id}")

            # You can now use this user_id for further processing
            # Example: Get the user object
            try:
                user = await bot.fetch_user(int(user_id))
                pretty_log(f"User found: {user.display_name} ({user.name})")

                guild = message.guild
                # Roles
                vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
                lottery_role = guild.get_role(VN_ALLSTARS_ROLES.lottery)
                giveaway_role = guild.get_role(VN_ALLSTARS_ROLES.giveaways)
                announcment_role = guild.get_role(VN_ALLSTARS_ROLES.announcments)
                staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
                bots_role = guild.get_role(VN_ALLSTARS_ROLES.bots)

                # Assign roles to user
                await user.add_roles(
                    vna_member_role,
                    lottery_role,
                    giveaway_role,
                    announcment_role,
                    reason="Auto role assignment on clan join",
                )
                # Channel info and creation
                channel_name = f"《👾》{user.name}"
                channel_topic = (
                    "This is your personal channel!! You may use this however you like."
                )
                new_channel = await guild.create_text_channel(
                    name=channel_name,
                    topic=channel_topic,
                    category=guild.get_channel(VN_ALLSTARS_CATEGORIES.CLAN_MEMBERS),
                )
                pretty_log(
                    "sucess",
                    f"Channel '{new_channel.name}' created for user {user.display_name}",
                    label="Auto Clan Invite",
                )

                # Set channel permissions so only the user and admins can access it
                user_permissions = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_messages=True,
                )

                everyone_permissions = discord.PermissionOverwrite(
                    view_channel=False,
                )

                await new_channel.set_permissions(user, overwrite=user_permissions)
                await new_channel.set_permissions(
                    guild.default_role, overwrite=everyone_permissions
                )
                await new_channel.set_permissions(
                    staff_role, overwrite=user_permissions
                )
                await new_channel.set_permissions(bots_role, overwrite=user_permissions)

                # Add an success embed for the new member
                desc = f"Successfully assigned {vna_member_role.mention} to {user.mention} and given access to your personal channel {new_channel.mention}!"
                embed = discord.Embed(
                    description=desc,
                    color=0xFF00EE,  # Magenta
                )
                embed.set_image(url=image_url)
                await message.channel.send(embed=embed)
                pretty_log(
                    "sucess",
                    f"Assigned roles to {user.display_name} and created channel {new_channel.name}",
                    label="Auto Clan Invite",
                )
                # Send a log embed to your server log channel
                log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
                if log_channel:
                    log_embed = discord.Embed(
                        title="New Clan Member Joined",
                        description=f"{user.mention} has joined the clan and was assigned roles and a personal channel.",
                        color=0xFF00EE,  # Magenta
                    )
                    log_embed.add_field(name="User", value=user.mention, inline=True)
                    log_embed.add_field(
                        name="Channel", value=new_channel.mention, inline=True
                    )
                    await send_webhook(
                        bot=bot,
                        channel=log_channel,
                        embed=log_embed,
                    )

            except discord.NotFound:
                pretty_log("error", f"User with ID {user_id} not found")
            except Exception as e:
                pretty_log("error", f"Error fetching user: {e}")
        else:
            pretty_log("info", "No user mention found in the message")
