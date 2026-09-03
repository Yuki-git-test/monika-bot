import discord

from constants.vn_allstars_constants import (MONIKA_EMBED_COLOR,
                                             VN_ALLSTARS_ROLES,
                                             VN_ALLSTARS_TEXT_CHANNELS,
                                             VNA_SERVER_ID)


# ─────────────────────────────────────────────
# 💫 Drop Role Autoping
# ─────────────────────────────────────────────
async def handle_drop_role_autoping(bot:discord.Client, message:discord.Message):
    content = f"<@&{VN_ALLSTARS_ROLES.drops}>"
    await message.channel.send(content)