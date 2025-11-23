import discord
from discord.ext import commands

from constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Event: on_invite_create
# 🍭──────────────────────────────
class InviteCreateEvent(commands.Cog):
    """Cog for handling invite creation events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        """Handles the event when a new invite is created."""
        guild = invite.guild
        if guild.id != VNA_SERVER_ID:
            return  # Ignore invites from other servers

        log_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
        if not log_channel:
            return  # Log channel not found

        creator = invite.inviter
        # Check if the creator is a staff member
        staff_role = guild.get_role(VN_ALLSTARS_ROLES.staff)
        if staff_role not in creator.roles:
            # Delete the invite if created by non-staff
            try:
                # Log the invite creation attempt before deletion
                embed = discord.Embed(
                    title="⚠️ Unauthorized Invite Creation Attempt",
                    color=discord.Color.red(),
                    description=(
                        f"**Creator:** {creator.mention}\n"
                        f"**Invite URL:** {invite.url}\n"
                        f"**Channel:** {invite.channel.mention} ({invite.channel.name})\n\n"
                        "This invite was deleted because it was created by a non-staff member."
                    ),
                )
                await log_channel.send(embed=embed)
                await invite.delete()
                pretty_log(f"Deleted invite created by non-staff member {creator}.")
                # DM the creator about the deletion
                try:
                    dm_embed = discord.Embed(
                        title="❌ Invite Deleted",
                        color=discord.Color.red(),
                        description=(
                            "Your invite has been deleted because only staff members are allowed to create invites in this server."
                        ),
                    )
                    await creator.send(embed=dm_embed)
                except Exception as e:
                    pretty_log(f"Failed to send DM to {creator}: {e}")

            except Exception as e:
                pretty_log(f"Failed to delete invite: {e}")
            return

        invite_url = invite.url
        max_uses = invite.max_uses if invite.max_uses else "Unlimited"
        expires_at = (
            invite.expires_at.strftime("%Y-%m-%d %H:%M:%S")
            if invite.expires_at
            else "Never"
        )

        embed = discord.Embed(
            title="📩 New Invite Created",
            color=discord.Color.green(),
            description=(
                f"**Creator:** {creator.mention}\n"
                f"**Invite URL:** {invite_url}\n"
                f"**Max Uses:** {max_uses}\n"
                f"**Expires At:** {expires_at}\n"
                f"**Channel:** {invite.channel.mention} ({invite.channel.name})"
            ),
        )
        await log_channel.send(embed=embed)
        pretty_log(f"Invite created by {creator} logged in {log_channel.name}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(InviteCreateEvent(bot))
