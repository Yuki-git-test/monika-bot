import discord
from discord.ext import commands
from discord import app_commands

from constants.vn_allstars_constants import (
    POKEMEOW_APP_ID,
    VN_ALLSTARS_CATEGORIES,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.db.vna_members_db_func import upsert_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

image_url = "https://media.discordapp.net/attachments/.../image.png"


# 🟣────────────────────────────────────────────
#          ⚡ Clan Invite ⚡
# 🟣────────────────────────────────────────────
async def clan_invite_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    channel_name: str,
    member: discord.Member,
):
    """Command to manually create a clan channel for a member."""

    guild = interaction.guild
    user = member
    channel = interaction.channel
    staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)

    # Staff-only check
    if staff_role not in interaction.user.roles:
        await interaction.response.send_message(
            "Only staff members can use this command.", ephemeral=True
        )
        return

    # Channel restriction check
    if channel.id != VN_ALLSTARS_TEXT_CHANNELS.ꨄclan_recruitment:
        await interaction.response.send_message(
            "This command can only be used in the Clan Recruitment channel.",
            ephemeral=True,
        )
        return

    # Roles
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    lottery_role = guild.get_role(VN_ALLSTARS_ROLES.lottery)
    giveaway_role = guild.get_role(VN_ALLSTARS_ROLES.giveaways)
    announcment_role = guild.get_role(VN_ALLSTARS_ROLES.announcments)
    bots_role = guild.get_role(VN_ALLSTARS_ROLES.bots)

    # Permissions
    pokemeow_bot = guild.get_member(POKEMEOW_APP_ID)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(
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

    # Channel creation
    channel_name = f"《👾》{channel_name}"
    channel_topic = "This is your personal channel!! You may use this however you like."
    new_channel = await guild.create_text_channel(
        name=channel_name,
        topic=channel_topic,
        category=guild.get_channel(VN_ALLSTARS_CATEGORIES.CLAN_MEMBERS),
        overwrites=overwrites,
    )
    pretty_log(
        "success",
        f"Channel '{new_channel.name}' created for user {user.display_name}",
        label="Clan Invite",
    )

    # Upsert member into DB
    await upsert_member(bot=bot, user=user, channel_id=new_channel.id)

    # Assign roles
    await user.add_roles(
        vna_member_role,
        lottery_role,
        giveaway_role,
        announcment_role,
        reason="Auto role assignment on clan join",
    )

    # Success embed
    desc = f"Successfully assigned {vna_member_role.mention} to {user.mention} and given access to your personal channel {new_channel.mention}!"
    embed = discord.Embed(description=desc, color=0xFF00EE)
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_image(url=image_url)
    await interaction.channel.send(embed=embed)

    pretty_log(
        "success",
        f"Assigned roles to {user.display_name} and created channel {new_channel.name}",
        label="Clan Invite",
    )

    # Log embed
    log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    if log_channel:
        log_embed = discord.Embed(
            title="New Clan Member Joined",
            description=f"**Member:** {user.mention}\n**Channel:** {new_channel.mention}",
            color=0xFF00EE,
        )
        log_embed.set_thumbnail(url=user.display_avatar.url)
        log_embed.set_author(
            name=member.display_name, icon_url=member.display_avatar.url
        )
        log_embed.set_footer(
            text=f"User ID: {user.id}", icon_url=guild.icon.url if guild.icon else None
        )
        await send_webhook(bot=bot, channel=log_channel, embed=log_embed)
