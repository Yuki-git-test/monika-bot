import discord
from discord.ext import commands

from constants.monika_library import get_random_color
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log, BOT_INSTANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🌸 Monika's Library Function 🌸
#   "Just Monika."
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   📝 Monika Report System 📝
#   "I love sharing knowledge with you!"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_report_embed(message: discord.Message):
    user = message.author
    user_name = user.display_name
    user_avatar = user.avatar.url if user.avatar else user.default_avatar.url
    desc = f"{user.mention} used {message.content} in {message.channel.mention}"

    embed = discord.Embed(
        description=desc,
        color=0xFF0000,
    )

    log_channel_id = 1349024210923687956
    log_channel = message.guild.get_channel(log_channel_id)
    if log_channel:
        try:
            await send_webhook(
                bot=BOT_INSTANCE,
                channel=log_channel,
                embed=embed,
            )
        except Exception as e:
            pretty_log(
                message=(
                    f"Failed to send report embed for user '{user.display_name}'. "
                    f"Error: {e}"
                ),
                tag="error",
                label="Monika Library Report Embed",
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💡 Monika Default Library Embed 💡
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def default_monika_library_embed(user: discord.Member, embed: discord.Embed):
    embed.color = get_random_color()
    guild = user.guild
    guild_icon = guild.icon.url if guild.icon else None
    embed.set_footer(
        text=f"Inquiry by {user.display_name}",
        icon_url=guild_icon,
    )
    return embed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   📚 Monika's Library Embed 📚
#   "Welcome to my library, friend~"
#   Trigger: !library , !help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_library_embed(message: discord.Message):
    user = message.author
    user_name = user.display_name
    user_avatar = user.avatar.url if user.avatar else user.default_avatar.url

    desc = """Psst, welcome to my library ♪
I've got all the info you'd possibly need so don't be shy~

Use the commands below to open any book <a:Cuddle:1373477979509887016>"""

    embed = discord.Embed(
        title="Monika's Library ₍^. .^₎⟆",
        description=desc,
    )
    # Add image url here then uncomment the lines below
    # image_url = ""
    # embed.set_image(url=image_url)

    embed.add_field(name="!battle", value="View recommended battle mons", inline=False)
    embed.add_field(name="!begin", value="Beginners’ guide to pokemeow", inline=False)
    embed.add_field(
        name="!bt",
        value="Battle Tower guide and how to grind efficiently ",
        inline=False,
    )
    embed.add_field(
        name="!coin", value="Ways to earn coins effeicientlys", inline=False
    )
    embed.add_field(
        name="!exp", value="Anything to know about `;explore`", inline=False
    )
    embed.add_field(
        name="!item",
        value="Held items usage and information about evolution items",
        inline=False,
    )
    embed.add_field(name="!mc", value="Mega chamber strategies", inline=False)
    embed.add_field(
        name="!mr", value="Meow Rogue guide and challenge strategies", inline=False
    )
    embed.add_field(
        name="!npc",
        value="gyms/champions/faction npc battle counters and strategies",
        inline=False,
    )
    embed.add_field(
        name="!wb", value="All information + Strategies on World Boss", inline=False
    )
    desc = f"""𝒫.𝒮. 𝒴𝑜𝓊'𝓇𝑒 𝓃𝑜𝓉 𝒶𝓁𝓁𝑜𝓌𝑒𝒹 𝓉𝑜 𝓁𝑒𝒶𝓋𝑒 𝓂𝓎 𝓁𝒾𝒷𝓇𝒶𝓇𝓎 {user_name}
𝒩𝑜𝓉 𝓊𝓃𝓉𝒾𝓁 𝓎𝑜𝓊 𝒻𝒾𝓃𝒾𝓈𝒽 𝑒𝓋𝑒𝓇𝓎 𝒷𝑜𝑜𝓴."""
    embed.add_field(name="˚ ༘ ೀ⋆｡ ˚", value=desc, inline=False)

    embed = default_monika_library_embed(user, embed)
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   📖 Monika's Beginner Guide Embed 📖
#   "Here's some tips to get you started~"
#  Trigger: !begin
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_beginner_guide_embed(message: discord.Message):
    user = message.author
    title = "Beginners' Guide by Monika ₍^. .^₎⟆"
    desc = "Oh my, you're freshly starting out pokemeow I see. No worries~ Here's some important info you should know ♪"
    image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6848c005&is=68476e85&hm=e65a73028a6d3f022902af7cd66b4dc556fea10cb03842a2f0c99380eee7adaa&"
    embed = discord.Embed(
        title=title,
        description=desc,
        color=get_random_color(),
    )

    embed.set_image(url=image_url)
    embed.add_field(
        name="1. Buy 10 Amulet Coins",
        value=";shop → 150,000 <:vna_pokecoin:1173890257285042227> each.\nEach Amulet can give you 5% coin boost in every pokemon you catch.",
        inline=False,
    )
    embed.add_field(
        name="2. Keep a Master Ball",
        value="Just in case you run into a Shiny or Legendary or an event exclusive pokemon. Never risk it.",
        inline=False,
    )
    embed.add_field(
        name="3. Daily Commands",
        value=(
            "Do `;daily`, `;hunt`, `;swap`, `;q` and `;vote`.\n"
            "Check `;cl` to see if you've done them. "
        ),
        inline=False,
    )
    embed.add_field(
        name="4. Lock Valuable Pokémon",
        value=(
            "Lock valuables such as `;r lock mega-line`, `;r lock egg`, `;r lock fossil` so you don't accidentally release them.\n\n"
            "Also check `;coll view buyers`. Collectors would pay more than release price for duplicaties. Locking = Profit. Always."
        ),
        inline=False,
    )
    embed.add_field(
        name="5. Release Duplicates",
        value=(
            "If you need coins but can't trade yet or use market yet, release safe duplicates.\n"
            "Check ;r view-locks first. "
        ),
        inline=False,
    )
    embed.add_field(
        name="6. Buy 5 Shiny Charms ",
        value=(
            """`;shop` → 50 vote coins
Boost shiny odds = more shiny to sell = more coins"""
        ),
        inline=False,
    )
    embed.add_field(
        name="7. Upgrade Catchbot",
        value="""Upgrade order: Cost → Pokémon → Duration
Command: `;cb`. DO NOT upgrade luck because it is useless and not worth investing.""",
        inline=False,
    )
    embed.add_field(
        name=" 8. Get a Better Rod",
        value="""Save Fishing Coins → Upgrade rods.
Only buy lures after Super Rod. You can also get lures (pokelure and misty lure) from quests.
Fish during Golden or Calm Water for better catch rates.""",
        inline=False,
    )
    embed.add_field(
        name="9. Use Training Accounts",
        value="""Use Focus-Punch Slaking strategy. Do `;bud set slaking` and then you can buy the move.
`;b user 675725560470831125` for Lv 40–60
`;b user 508692505810698241` for Lv 61–100
Also you can do level-grinding on mega line such as gible, charizard etc and selling to get profit.""",
        inline=False,
    )
    embed.add_field(
        name="10. Battle Npcs for extra coins",
        inline=False,
        value="Faction npcs battles can give you extra coins and items. Check out `!library npc` more strategies.",
    )
    embed.add_field(
        name="11. Join a Clan",
        value="Post your ;stats in clan recruitment channel in os and look for clans in clan ads. A good clan can greatly improve your experience and provide assistance in whatever you'd need. The clan perks are also really important.",
        inline=False,
    )
    embed.add_field(
        name="˚ ༘ ೀ⋆｡˚",
        value=f"I'm always here for you {user.display_name}. Just make any inquiry~ ",
        inline=False,
    )
    embed = default_monika_library_embed(user, embed)
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💰 Monika's Coin Guide Embed 💰
#   "Need coins? I've got you covered~"
# Trigger: !coin , !coins
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_coin_guide_embed(message: discord.Message):
    user = message.author
    desc = "## Monika's Money Guide: <:vna_pokecoin:1173890257285042227>"

    embed = discord.Embed(
        description=desc,
        color=get_random_color(),
    )

    embed.add_field(
        name="**Method 1: ** Grind with 12 amulet coins (17 with shiny patreon)",
        value="> 13 amulet coins are available in total from ;shop ;clan and ;explore. A further 4 can be obtained from shiny patreon. Amulet coins boost the amount of coins you earn per catch by 5% each.",
        inline=False,
    )

    embed.add_field(
        name="**Method 2:** Battle with a luck incense",
        value="""> Obtainable from the "Obtain a battle icon" quest. Luck incense doubles your coins from battles.""",
        inline=False,
    )

    embed.add_field(
        name="**Method 3:** Sell rare pokemon on the market/to other players",
        value="> Shinies, Goldens, Legendaries tend to sell for the most. Ask in  <#910102221373456404> on help with prices so pros can help.",
        inline=False,
    )

    embed.add_field(
        name="**Method 4:** Do ;r d ",
        value="> ;r d releases all of your duplicate pokemon which gives you a good amount of money quickly. However, since most of the time its more profitable to sell than release, you should only do this method when you are in desperate need for coins. Some ideas of good things to lock: mega-line, event, fossil.",
        inline=False,
    )
    embed.add_field(
        name="**Method 5:** Exchange items earned from ;p",
        value="> Check out ;res to see how much coins can be earned from exchanging different items. To exchange items, do ;res ex (item) and follow the prompts given. If the item has 2 words, use a _ to join them",
        inline=False,
    )

    embed.add_field(
        name="**Method 7:** Complete ;q",
        value="> You can get a new quest every 2 hours (without patreon). For help regarding quests to do with fun items (chocolate bars, candy etc), please politely ask in <#898176723626127390>. Remember you are not guaranteed that someone will give you the item(s) you need as people do it out of their own generosity, free time and free will.",
        inline=False,
    )

    embed.add_field(
        name="**Method 8:** Enter the ;lot [Be lucky] <:vna_worryPat:910231775870058556>",
        value="> When entering the lottery, it is important to remember that you are not always guaranteed to make a profit. The more tickets = higher chance of winning. Check ;lot to see when they occur. It is recommended to buy 1-10 tickets every time in order to still have a chance of winning something whilst spending a little amount",
        inline=False,
    )

    embed.add_field(
        name="**Method 9:** ;explore",
        value="> **Explore** is Patreon only at the moment but worth. You earn less coins per catches but it's much, much faster and you can farm a lot of collectors' mons there. Explore exclusive golden mons also fetch a good price. Clans usually host explore events with big prices too so it's one of the best way to earn coins fast.",
        inline=False,
    )
    embed.add_field(
        name="**Method 10:** Complete ;promo",
        value="> Promo goldens are usually worth a lot of coins, even more so if they are useful. Grinding for the golden then selling it will most like bring in (tens of) millions of coins.",
        inline=False,
    )
    embed.add_field(
        name="**Method 11:** Defeat ;wb",
        value="> The more damage you do the more coins you get. For finding out the best strats for each boss please `!wb`. Thankfully it’s pretty easy to at least qualify, even with cheap pokemon! From there, you can then sell the pokemon you get as a reward (goldens, shinies, gmax, shiny gmax) for pretty good amounts.",
        inline=False,
    )
    embed.add_field(
        name="₊✩‧₊˚౨ৎ˚₊✩‧₊",
        value=f"I'm always here for you {user.display_name}. Just make any inquiry~ ",
        inline=False,
    )
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔬 Monika's Research Guide Embed 🔬
#   "Here's everything about research items~"
#   Trigger: !res
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_research_guide_embed(message: discord.Message):
    user = message.author
    desc = "## Monika's Collection of Research: <a:jirachiii:1301844526100516936>"

    embed = discord.Embed(
        description=desc,
        color=get_random_color(),
    )

    val_1 = """> - Pearl, Nugget, Star Piece, Comet Shard, Rare Candy, Egg, Relic items (Crown, Statue, Band and Vase) + evolution/battle items.
> - You can spend the research points at /research shop . To see what the items do, you can check `/items info category:research`."""
    embed.add_field(
        name="**Research info**",
        value=val_1,
        inline=False,
    )
    val_2 = """> **Nuggets:-**
> `;res ex nugget pc amount`
> - To exchange it for points and coins.
> `;res ex nugget nugget`
> - To get a big nugget in exchange of 10 small ones.
> **Pearls:-**
> - These are same as nuggets.
> **Star piece and Comet shard:-**
> - `res ex star_piece/comet_shard pc amount`
> **Relics:-**
> - `;res ex relics`
> **Fossils:-**
> - `;res ex cover_fossil`"""

    embed.add_field(
        name="**Research items exchange commands :**",
        value=val_2,
        inline=False,
    )
    val_3 = """> **Red shard:** Moltres and Ho-Oh
> **Blue shard:** Articuno and Lugia
> **Green shard:** Celebei and Rayquaza
> **Yellow shard:** Zapados and Jirachi
Note* You consume the shard after encontering the mons."""

    embed.add_field(
        name="**__Research Exclusives__**",
        value=val_3,
        inline=False,
    )
    embed.add_field(
        name=" ᡣ𐭩 •｡ꪆৎ ˚⋅",
        value=f"I'm always here for you {user.display_name}. Just make any inquiry~ ",
        inline=False,
    )
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   ⚔️ Monika's Battle Guide Embed ⚔️
#   "Looking for strong battle mons? I've got you covered~"
#   Trigger: !battle , !b, !library battle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_battle_guide_commands_embed(message: discord.Message):
    user = message.author
    desc = """# Monika's Library: Battle mons

### Battle Mon COMMANDS:

- `!bmew` | `!b 151` Mew collection
- `!bmewtwo` | `!b 150` MewTwo collection
- `!bmmx` | `!b 7109` Mega MewTwo-X collection
- `!bmmy` | `!b 7121` Mega MewTwo-Y collection
- `!bmchomp` | `!b 7034` Mega Garchomp collection
- `!bresh` | `!b 643` Reshirem collection
- `!bsha` | `!b 802` Marshadow collection
- `!bxer` | `!b 716` Xerneas collection
- `!byvel` | `!b 717` Yveltal collection
- `!barc` | `!b 493` Arceus collection
- `!bkyo` | `!b 382` Kyogre collection
- `!bgrd` | `!b 383` Groudon collection
- `!bzac` | `!b 888` Zacian collection
- `!bzc` | `!b 7891` Zacian-crowned collection"""
    embed = discord.Embed(
        description=desc,
        color=get_random_color(),
    )
    embed = default_monika_library_embed(user, embed)
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)
