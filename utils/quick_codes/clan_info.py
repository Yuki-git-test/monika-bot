import discord

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)


async def post_clan_info(message: discord.Message):
    guild = message.guild
    desc = f"""**{Emojis.crown} Clan Owner: <@715486300383477823>**
{Emojis.purple_mod} **Co-Owners: <@898892921334550528> <@590479088741908491> <@705447976658665552>**"""
    perks_name_str = f"**{Emojis.purple_star} Perks:**"
    perks_value_str = """> - Active and helpful community.
> - Private grinding channels
> - Fully boosted server with our own VNA tag.
> - 250m <:vna_pokecoin:1173890257285042227> worth of monthly grinder rewards!
> - Daily/weekly events and competitions with special rewards"""

    req_name_str = f"**{Emojis.purple_exclamation} Requirements:**"
    req_value_str = """> - Must do at least **1,500 catches** per week. (Catchbot not included)
> - Be nice! <a:Cuddle:1373477979509887016>
> - Donations are always appreciated so we can host better quality events and giveaways. Can either ;give <@824975437440352266> (amount) or `;clan donate (amount)`
*Ping staff members if you have any questions or inquiries*"""
    title = (
        f"{VN_ALLSTARS_EMOJIS.amethyst} Clan Information {VN_ALLSTARS_EMOJIS.amethyst}"
    )
    embed = discord.Embed(title=title, description=desc, color=0xB505CA)
    embed.add_field(name=perks_name_str, value=perks_value_str, inline=False)
    embed.add_field(name=req_name_str, value=req_value_str, inline=False)
    embed.set_thumbnail(url=guild.icon.url)
    embed.set_image(url=Dividers.starry_sky)
    await message.channel.send(embed=embed)
