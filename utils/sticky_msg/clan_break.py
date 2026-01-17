import discord

from constants.vn_allstars_constants import (
    MONIKA_APP_ID,
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)


async def clan_break_sticky_msg(message: discord.Message):
    """Sends a sticky message in the clan break channel when a user posts a message there."""

    # Remove old sticky message
    vna_server = message.guild
    clan_break_channel = vna_server.get_channel(VN_ALLSTARS_TEXT_CHANNELS.clan_break)
    async for msg in clan_break_channel.history(limit=100):
        # Check if the message is from the bot and contains the embed
        if (
            msg.author.id == MONIKA_APP_ID
            and msg.embeds
            and msg.embeds[0].title == "🛡️ Clan Break Rules"
        ):
            await msg.delete()
            break

    # Send new sticky message
    desc = """> - Must be 1 month in clan before requesting
> - Always state your clan name when asking
> - Staff may or may not grant the role
> - Members can't join giveaways while on break
> - Role lasts 14 days, then you must re‑request if needed"""
    vna_server = message.guild
    embed = discord.Embed(
        title="🛡️ Clan Break Rules", description=desc, color=MONIKA_EMBED_COLOR
    )
    embed.set_footer(
        text="If you have any questions, please contact a staff member.",
        icon_url=vna_server.icon.url if vna_server.icon else None,
    )

    await clan_break_channel.send(embed=embed)
