import discord

from constants.worldboss import WBRegImage, WBShinyImage, get_regdex_key_by_value
from utils.monika_library.library import (
    default_monika_library_embed,
    get_random_color,
    send_report_embed,
)

mmy_both_consistency_mvp_strat = [
    "ven",
    "cen",
    "bla",
    "cha",
    "cin",
    "gar",
    "gen",
    "int",
    "kin",
    "lap",
    "mac",
    "meo",
    "ril",
    "san",
    "sno",
    "tox",
    "urs",
    "eev",
    "dur",
    "eet",
]
mmy_consistentcy_strat = ["alc", "app", "fla", "but", "cop", "mel", "cor", "hat", "orb"]
non_mmy_mvp_strat = [
    "alc",
    "app",
    "fla",
    "but",
    "cop",
    "mel",
    "cor",
    "gri",
    "hat",
    "orb",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🐲 Monika Library WB Info Embed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_wb_info_embed(message: discord.Message):
    user = message.author
    color = 0xD900FF
    image_url = "https://cdn.discordapp.com/attachments/1346306868221317130/1379993083181011084/8DEAA704-B73C-4803-BD91-BAF055993A19.png?ex=68424236&is=6840f0b6&hm=679f1fdc749d44c7d80422d9baf24daee9fe78d6a0eb10fdee207dc560c85e6b&"
    desc = """## 🌸Monika's Library: WORLD BOSS


### World Boss Commands:

✩ **`!wbi`** World Boss info
✩ **`!wbee`** | **`(!7244)`** WB Eternamax-Eternatus
✩ **`!wbalc`** | **`(!7193)`** WB Gmax-Alcremie
✩ **`!wbapp`** | **`(!7241)`** WB Gmax-Appletun
✩ **`!wbbla`** | **`(!7160)`** WB Gmax-Blastoise
✩ **`!wbbut`** | **`(!7166)`** WB Gmax-Butterfree
✩ **`!wbcen`** | **`(!7211)`** WB Gmax-Centiskorch
✩ **`!wbcha`** | **`(!7145)`** WB Gmax-Charizard
✩ **`!wbcin`** | **`(!7148)`** WB Gmax-Cinderace
✩ **`!wbcoa`** | **`(!7199)`** WB Gmax-Coalossal
✩ **`!wbcop`** | **`(!7226)`** WB Gmax-Copperajah
✩ **`!wbcor`** | **`(!7184)`** WB Gmax-Corviknight
✩ **`!wbdre`** | **`(!7223)`** WB Gmax-Drednaw
✩ **`!wbdur`** | **`(!7214)`** WB Gmax-Duraludon
✩ **`!wbeev`** | **`(!7154)`** WB Gmax-Eevee
✩ **`!wbfla`** | **`(!7229)`** WB Gmax-Flapple
✩ **`!wbgar`** | **`(!7190)`** WB Gmax-Garbodor
✩ **`!wbgen`** | **`(!7151)`** WB Gmax-Gengar
✩ **`!wbgri`** | **`(!7202)`** WB Gmax-Grimmsnarl
✩ **`!wbhat`** | **`(!7238)`** WB Gmax-Hatterene
✩ **`!wbint`** | **`(!7217)`** WB Gmax-Inteleon
✩ **`!wbkin`** | **`(!7181)`** WB Gmax-Kingler
✩ **`!wblap`** | **`(!7175)`** WB Gmax-Lapras
✩ **`!wbmac`** | **`(!7157)`** WB Gmax-Machamp
✩ **`!wbmel`** | **`(!7187)`** WB Gmax-Melmetal
✩ **`!wbmeo`** | **`(!7172)`** WB Gmax-Meowth
✩ **`!wborb`** | **`(!7220)`** WB Gmax-Orbeetle
✩ **`!wbpik`** | **`(!7169)`** WB Gmax-Pikachu
✩ **`!wbril`** | **`(!7205)`** WB Gmax-Rillaboom
✩ **`!wbsan`** | **`(!7208)`** WB Gmax-Sandaconda
✩ **`!wbsno`** | **`(!7178)`** WB Gmax-Snorlax
✩ **`!wbtox`** | **`(!7196)`** WB Gmax-Toxtricity
✩ **`!wburs`** | **`(!7235)`** WB Gmax-Urshifu Rapid Strike
✩ **`!wbuss`** | **`(!7232)`** WB Gmax-Urshifu Single Strike
✩ **`!wbven`** | **`(!7163)`** WB Gmax-Venusaur"""
    embed = discord.Embed(description=desc, color=color)
    embed.set_image(url=image_url)
    embed = default_monika_library_embed(user, embed)
    embed.color = color
    await message.reply(embed=embed, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🐲 Build WB Embed Function
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_sub_wb_embed(pokemon: str, topic: str, color):
    embed = discord.Embed(color=color)
    embed.add_field(
        name="- **Grimer**",
        value="""> Equipment: `N/A`
> Moves: `Memento`
> EVs: `N/A`
> -# *Note: You can use any `Memento` user instead of **Grimer**""",
        inline=False,
    )
    embed.add_field(
        name="- **Muk**",
        value="""> Equipment: `Loaded-Dice` | `Sitrus-berry`
> Moves: `Memento` `Acid-spray` `Screech`
> EVs: `HP 252` `SPD 252` """,
        inline=False,
    )

    if pokemon in mmy_both_consistency_mvp_strat or pokemon in mmy_consistentcy_strat:
        if topic == "consistency":
            title = "## CONSISTENCY TEAM:"
            color = color
            image_url = getattr(WBRegImage, pokemon)
            embed.add_field(
                name="- **Mega Mewtwo Y**",
                value="""> Equipment: `Metronome` | `Twisted-spoon`
> Moves: `Calm-mind` `Bulk-up` `Recover` `Stored-power`
> EVs: `SPA 252` `SPD 252` `HP 6` """,
                inline=False,
            )
            embed.add_field(
                name="## **STRATEGY**",
                value="""- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-spray` 3x times to get -6 special defence, then use 1x `Memento`
- With **MMY**, use `Calm-mind` 6x times then `Bulk-up` at least 1x time. The amount of `Bulk-up` depends on how many people participate. More `Bulk-up` = more damage multiplier
- After the setup above, spam `Stored-power` to damage the WB.
- Use `Recover` to heal when low HP.""",
                inline=False,
            )
        elif topic == "mvp" and pokemon not in non_mmy_mvp_strat:
            title = "## MVP TEAM:"
            image_url = getattr(WBShinyImage, pokemon)
            embed.add_field(
                name="- **Mega Mewtwo Y**",
                value="""> Equipment: `Choice-cloak` | `Choice-specs`
> Moves: `Stored-power`
> EVs: `SPA 252` `SPD 252` `HP 6` """,
                inline=False,
            )
            embed.add_field(
                name="## ** MVP STRATEGY**",
                value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-spray` 3x times to get -6 special defence, then use 1x `Memento`
- With **MMY**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD. `Stored-power` damage scales off these stats buffs.
- After the setup above, spam `Stored-power` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.""",
                inline=False,
            )

    # Alcremie MVP Strategy
    elif pokemon == "alc" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Zacian-Crowned**",
            value="""> Equipment: `Choice-cloak` | `Choice-band` | `Metronome`
> Moves: `Behemoth-blade`  `Swords-dance`
> EVs: `ATK 252` `SPD 252` `HP 6` """,
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **ZC**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Behemoth-blade` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )

    # Flapple / Appletun MVP Strategy
    elif (pokemon == "app" or pokemon == "fla") and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Golden Kyurem-White**",
            value="""> Equipment: `Choice-cloak` | `Choice-specs` | `Expert-belt` | `Metronome`
> Moves: `Ice-burn` `Roost`
> EVs: `SPA 252` `SPD 252` `HP 6` """,
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-spray` 3x times to get -6 special defence, then use 1x `Memento`
- With **GKW**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Ice-burn` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP. (Or) `Roost` if you don't have choice items on.""",
            inline=False,
        )

    # Butterfree MVP Strategy
    elif pokemon == "but" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Golden Rhyperior**",
            value="""> Equipment: `Choice-band` `Expert-belt` `Choice-cloak` `Hard-stone`
> Moves: `Rock-wrecker`  `swords-dance`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **Golden Rhyperior**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Rock-wrecker` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )
    # Copperajah MVP Strategy
    elif pokemon == "cop" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Pangoro**",
            value="""> Equipment: `Choice-band` `Choice-cloak` `Black-glasses` `Metronome`
> Moves: `Power-trip` `Bulk-up`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **Pangoro**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Power-trip` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )

    # Melmetal MVP Strategy
    elif pokemon == "mel" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Gmax-Charizard**",
            value="""> Equipment: `Choice-specs` `Expert-belt` `Choice-cloak` `Metronome`
> Moves: `Max-flare` `Roost`
> EVs: `SPA 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **Gmax-Charizard**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Max-flare` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note use MMY if you don't plan to aux""",
            inline=False,
        )

    # Corviknight MVP Strategy
    elif pokemon == "cor" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Pangoro**",
            value="""> Equipment: `Choice-band` `Choice-cloak` `Black-glasses` `Metronome`
> Moves: `Power-trip` `Bulk-up`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **Pangoro**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Power-trip` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )

    # Grimmsnarl Consistency and MVP Strategy
    elif pokemon == "gri":
        if topic == "consistency":
            title = "## CONSISTENCY TEAM:"
            color = color
            image_url = getattr(WBRegImage, pokemon)
            embed.add_field(
                name="- **Xerneas**",
                value="""> Equipment: `Metronome` | `Twisted-spoon`  | `Expert-belt` | `Fairy-feather`
> Moves: `Draining-kiss` `Geomancy` `Moonblast`
> EVs: `SPA 252` `SPD 252` `HP 6`
_
**(OR)**
_""",
                inline=False,
            )
            embed.add_field(
                name="- **Mega-Gardevoir**",
                value="""> Equipment: `Metronome` | `Twisted-spoon`  | `Expert-belt` | `Fairy-feather`
> Moves: `Draining-kiss` `Calm-mind` `Moonblast`
> EVs: `SPA 252` `SPD 252` `HP 6` """,
                inline=False,
            )
            embed.add_field(
                name="## **STRATEGY**",
                value="""- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-spray` 3x times to get -6 special defence, then use 1x `Memento`
- With **Xernas**, use `Geomancy` 3x times. If you pick **Mega-Gardevoir**, use `Calm-mind` 6x times.
- After the setup above, spam `Moonblast` to damage the WB.
-Do more `Calm-mind` or `Geomancy` if you get debuff. (You want to stay at +6 in SPA and SPD maximum damage).
- Use `Draining-kiss` to heal when low HP.""",
                inline=False,
            )
        elif topic == "mvp":
            title = "## MVP TEAM:"
            image_url = getattr(WBShinyImage, pokemon)
            embed.add_field(
                name="- **Zacian-Crowned**",
                value="""> Equipment: `Choice-cloak` | `Choice-band` | `Metronome`
> Moves: `Behemoth-blade`  `Swords-dance`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
                inline=False,
            )
            embed.add_field(
                name="## ** MVP STRATEGY**",
                value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **ZC**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Behemoth-blade` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
                inline=False,
            )

    # Hatterene MVP Strategy
    elif pokemon == "hat" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Zacian-Crowned**",
            value="""> Equipment: `Choice-cloak` | `Choice-band` | `Metronome`
> Moves: `Behemoth-blade`  `Swords-dance`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **ZC**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Behemoth-blade` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )

    # Urshifu Singlestrike Consistency and MVP Strategy
    elif pokemon == "uss":
        if topic == "consistency":
            title = "## CONSISTENCY TEAM:"
            color = color
            image_url = getattr(WBRegImage, pokemon)
            embed.add_field(
                name="- **Xerneas**",
                value="""> Equipment: `Metronome` | `Twisted-spoon`  | `Expert-belt` | `Fairy-feather`
> Moves: `Draining-kiss` `Geomancy` `Moonblast`
> EVs: `SPA 252` `SPD 252` `HP 6`
_
**(OR)**
_""",
                inline=False,
            )
            embed.add_field(
                name="- **Mega-Gardevoir**",
                value="""> Equipment: `Metronome` | `Twisted-spoon`  | `Expert-belt` | `Fairy-feather`
> Moves: `Draining-kiss` `Calm-mind` `Moonblast`
> EVs: `SPA 252` `SPD 252` `HP 6` """,
                inline=False,
            )
            embed.add_field(
                name="## **STRATEGY**",
                value="""- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-spray` 3x times to get -6 special defence, then use 1x `Memento`
- With **Xernas**, use `Geomancy` 3x times. If you pick **Mega-Gardevoir**, use `Calm-mind` 6x times.
- After the setup above, spam `Moonblast` to damage the WB.
-Do more `Calm-mind` or `Geomancy` if you get debuff. (You want to stay at +6 in SPA and SPD maximum damage).
- Use `Draining-kiss` to heal when low HP.""",
                inline=False,
            )
        elif topic == "mvp":
            title = "## MVP TEAM:"
            image_url = getattr(WBShinyImage, pokemon)
            embed.add_field(
                name="- **Gmax-Hatterene**",
                value="""> Equipment: `Choice-cloak` | `Choice-band` | `Metronome`
> Moves: `Gmax-Smite`  `Draining-kiss` `Calm-mind`
> EVs: `SPA 252` `SPD 252` `HP 6`""",
                inline=False,
            )
            embed.add_field(
                name="## ** MVP STRATEGY**",
                value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Acid-Spray` 3x times to get -6  defence, then use 1x `Memento`
- With **Gmax-Hatterene**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Gmax-Smite` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
                inline=False,
            )

    elif pokemon == "orb" and topic == "mvp":
        title = "## MVP TEAM:"
        image_url = getattr(WBShinyImage, pokemon)
        embed.add_field(
            name="- **Pangoro**",
            value="""> Equipment: `Choice-band` `Choice-cloak` `Black-glasses` `Metronome`
> Moves: `Power-trip` `Bulk-up`
> EVs: `ATK 252` `SPD 252` `HP 6`""",
            inline=False,
        )
        embed.add_field(
            name="## ** MVP STRATEGY**",
            value="""- Must have at least 3x `Aux powerguard`.
- Keep a few `Aux power` and `Aux guard` in-case the WB lowers your stats.
- **Grimer** can be any level. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6  defence, then use 1x `Memento`
- With **Pangoro**, use 3x `Aux powerguard` to max out SPA, ATK, DEF, SPD.
- After the setup above, spam `Power-trip` to damage the WB.
- Use `Aux power` or `Aux guard` whenever your stats gets lowered by 2 stages.
- Use `Max-potions` to heal when low HP.
-# *Note even if you're using `Metronome`, at least 3x `Aux-guard` required to survive a few hits""",
            inline=False,
        )
    embed.title = title
    embed.set_image(url=image_url)
    return embed



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🐲 Send WB Embed Function
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_wb_embed(message:discord.Message):
    user = message.author
    content = message.content.lower()
    pokemon = None
    topic = "consistency"
    if content.startswith("!wb"):
        pokemon = content[3:6]
    else:
        content = content.strip("!")
        pokemon = get_regdex_key_by_value(content)

    color = get_random_color()
    embed = build_sub_wb_embed(pokemon, topic, color)
    embed = default_monika_library_embed(user, embed)
    embed.color = color
    view = WBButtons(pokemon, user.id, color)
    view.disable_initial_consistency()
    await message.reply(embed=embed, view=view, mention_author=False)
    await send_report_embed(message)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🐲 WB Buttons View
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class WBButtons(discord.ui.View):
    def __init__(self, pokemon: str, author_id: int, color):
        super().__init__(timeout=120)
        self.pokemon = pokemon
        self.author_id = author_id
        self.topic = "consistency"
        self.color = color

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

    @discord.ui.button(label="Consistency", style=discord.ButtonStyle.primary)
    async def consistency_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topic = "consistency"
        embed = build_sub_wb_embed(self.pokemon, self.topic, self.color)
        await interaction.response.edit_message(embed=embed, view=self)

        # disable this button and enable the other
        button.disabled = True
        self.mvp_button.disabled = False
        await interaction.message.edit(view=self)

    @discord.ui.button(label="MVP", style=discord.ButtonStyle.success)
    async def mvp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topic = "mvp"
        embed = build_sub_wb_embed(self.pokemon, self.topic, self.color)
        await interaction.response.edit_message(embed=embed, view=self)

        # disable this button and enable the other
        button.disabled = True
        self.consistency_button.disabled = False
        await interaction.message.edit(view=self)

    def disable_initial_consistency(self):
        self.consistency_button.disabled = True