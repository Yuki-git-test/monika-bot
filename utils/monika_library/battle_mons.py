import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log
from utils.monika_library.library import (
    default_monika_library_embed,
    get_random_color,
    send_report_embed,
)

MAGENTA_COLOR = 0xC312D2


# 🐾────────────────────────────────────────────
#           Battle Mons Command
# 🐾────────────────────────────────────────────
async def send_battle_mon_embed(embed: discord.Embed, message: discord.Message):
    """
    Create an embed for a battle mon.
    """
    normal_battle_str = "- Normal Battle (non setup)"
    world_boss_str = "- World boss"
    setup_sweeper_str = "- Setup Sweeper"
    debuffer_str = "- Debuffer"
    not_available_str = "> N/A"

    message = message.content.lower()

    # 🐾────────────────────────────────────────────
    #           Mega Garchomp
    # 🐾────────────────────────────────────────────
    if message == "!bmchomp" or message == "!b 7034":
        title = "Battlemon : Mega-Garchomp"
        desc = "Variant : `Mega-garchomp #7034`  | `Golden Mega-Garchomp 7036`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/garchomp-mega.gif"
        color = MAGENTA_COLOR

        embed.add_field(
            name=normal_battle_str,
            value=""">   Moves : `Outrage` `Earthquake` `Iron-head` `Crunch|poison-jab`
>       EVs : `ATK 252` `SPE 252` `HP 4`
>      Item : `Choice-cloak`   |  `Choice-scarf`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=""">   Moves : `Earthquake` `Swords-dance`
>     EVs : `SPA 252` `SPD 252` `HP 4`
>     Item : `Metronome` | `Choice-band` | `Choice-cloak`
>   *Note : At least 3x aux-guard required to use in World Boss""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #             Marshadow
    # 🐾────────────────────────────────────────────
    elif message == "!bsha" or message == "!b 802":
        title = "Battlemon : Marshadow"
        desc = "Variant : `Marshadow` | `Golden Marshadow`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/marshadow.gif"
        color = 0x0B0A0A

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : >   Moves : `Close-combat | Drain-Punch` `Spectral-thief` `Ice-Punch` `Poison-jab | Iron-head | Sucker-Punch`

>     Item :  `Choice_Band`   |   `Choice_Cloak`

>     EVs : `ATK 252` `HP 252` `DEF 4`
""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Xerneas
    # 🐾────────────────────────────────────────────
    elif message == "!b 716" or message == "!bxern":
        title = "Battlemon : Xerneas"
        desc = "Variant : `Xerneas` | `Golden Xerneas`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/xerneas.gif"
        color = 0x2300FA

        embed.add_field(
            name=normal_battle_str,
            value=""">   Moves : `Moonblast` `Draining-kiss` `Thunderbolt` `Psychic`

>   EVs : `SPA 252` `SPE 252`

> Item :   `Choice-Scarf` | `Choice-Cloak` """,
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=""">   Moves : `Moonblast` `Draining-kiss` `Geomancy`
>       EVs : `SPA 252` `SPD 252` `HP 4`
> Item :   `Choice-specs` | `Choice-Cloak` | `Metronome` | `Expert-belt`""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Kyogre
    # 🐾────────────────────────────────────────────
    elif message == "!b 382" or message == "!bkyo":
        title = "Battlemon : Kyogre"
        desc = "Variant :  `Kyogre` | `Primal-Kyogre` | `Golden Kyogre` "
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/kyogre.gif"
        color = 0x0076F5

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Surf | Water-spout` `Earthquake` `Ice-Beam` `Thunderbolt`

> EVs : `SPA 252` `SPE 252` `HP 4`

> Item : `Choice-Scarf` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Groudon
    # 🐾────────────────────────────────────────────
    elif message == "!bgrd" or message == "!b 383":
        title = "Battlemon : Groudon"
        desc = "Variant :  `Groudon` | `Primal-Groudon` | `Golden Groudon`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/groudon.gif"
        color = 0xC35702

        embed.add_field(
            name=normal_battle_str,
            value=""">   Moves : `Earthquake | Precipice-Blades`
>                 `Fire-Punch | Eruption`
>                 `Thunder-Punch`
>                 `Stone-edge | Iron-head | Focus-Punch`
>        EVs : `ATK 252` `SPE 252` `HP 4`
>        Item :  `Choice-Scarf` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=""">   Moves : `Earthquake` `Swords-dance`
>        EVs : `ATK 252` `SPD 252` `HP 4`
>        Item :  `Metronome` | `Choice-Cloak` | `Choice-band` | `Soft-sand`
>      Note* : At least 3x `aux-guard` required for World Boss""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Zacian-Crowned
    # 🐾────────────────────────────────────────────
    elif message == "!bZC" or message == "!b 7891":
        title = "Battlemon : Zacian-Crowned"
        desc = "Variant : `Shiny Zacian-Crowned` | `Zacian-Crowned` "
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/zacian-crowned.gif"
        color = 0xC312D2

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Play-Rough` `Behemoth-Blade` `Close-Combat` `Wild-Charge | Crunch`
> EVs : `ATK 252` `HP 252` `SPE 4`
> Item : `Choice-Band` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=setup_sweeper_str,
            value=not_available_str,
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value="""> Moves : `Behemoth-Blade` `Swords-Dance`
>     EVs : `ATK 252` `SPD 252` `HP 4`
>     Item : `Choice-Band` `Metronome` `Metal-Coat`
>   Note* : At least 3x `aux-guard` required
""",
            inline=False,
        )
        embed.add_field(
            name=debuffer_str,
            value="""> Moves : `Noble-Roar`
>     EVs : `HP 252` `SPE 252` `SPD 4` | `HP 252` `SPD 128` `DEF 128`
>    Item : `Choice-Scarf`""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Yveltal
    # 🐾────────────────────────────────────────────
    elif message == "!b 717" or message == "!byve":
        title = "Battlemon : Yveltal"
        desc = "Variant :  `Yveltal` | `Golden Yveltal`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/yveltal.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value=""">   Moves : `Sucker-Punch` `Oblivion-wing` `Psychic` `Heat-wave`

>   EVs : `SPA 252` `HP 252` `SPE 4`

>  Item : `Life_Orb` | `Choice_Specs` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Reshiram
    # 🐾────────────────────────────────────────────
    elif message == "!b 643" or message == "!bresh":
        title = "Battlemon : Reshiram"
        desc = "Variant :  `Reshiram` | `Golden Reshiram`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/reshiram.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Outrage` `Fusion-flare` `Earth-power` `Shadow-ball | Psychic | Blue-flare`

> EVs : `SPA 252` `SPE 252` `HP 4`
> Item : `Choice_scarf` | `Choice_Cloak` """,
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Slaking
    # 🐾────────────────────────────────────────────
    elif message == "!bslak" or message == "!b 289":
        title = "Battlemon : Slaking"
        desc = "Variant :  `Slaking` | `Golden Slaking`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/slaking.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Sucker-Punch` `Earthquake` `Fucus-Punch | Drain-Punch` `Play-rough | Ice-Punch | Thunder-Punch`

> EVs : `ATK 252` `SPD 128` `HP 128`

> Item :   `Assault_Vest` | `Expert_Belt` | `Choice_Band` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Rayquaza
    # 🐾────────────────────────────────────────────
    elif message == "!bray" or message == "!b 384":
        title = "Battlemon : Rayquaza"
        desc = "Variant :  `Rayquaza` | `Mega-Rayquaza` | `Golden Rayquaza`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/rayquaza.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Outrage` `Dragon-ascent` `Earthquake` `V-create | Rock-slide | Ice-Beam`

> EVs : `ATK 252` `HP 252` `SPE 4`

> Item :  `Choice_Band` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Arceus
    # 🐾────────────────────────────────────────────
    elif message == "!b 493" or message == "!barc":
        title = "Battlemon : Arceus"
        desc = "Variant :  `Arceus` | `Golden Arceus`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/arceus.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Extreme-speed` `Last-resort` `Earthquake` `Recover | Outrage | Foul-play`

> EVs : `ATK 252` `HP 252` `DEF 4`

> Item :   `Silk-Scarf` | `Life_Orb` | `Choice_Band` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Zekrom
    # 🐾────────────────────────────────────────────
    elif message == "!b 644" or message == "!bzek":
        title = "Battlemon : Zekrom"
        desc = "Variant :  `Zekrom` | `Golden Zekrom`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/zekrom.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Outrage` `Fusion-bolt` `crunch` `Earth-power`

>  EVs : `ATK 252` `SPE 252` `HP 4`

> Item : `Choice_Scarf`  | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Ho-oh
    # 🐾────────────────────────────────────────────
    elif message == "!b 250" or message == "!bhoh":
        title = "Battlemon : Ho-oh"
        desc = "Variant :  `Ho-oh` | `Golden Ho-oh`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/ho-oh.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value=""">  Moves : `Brave-bird` `Dream-Eater` `Sacred-fire` `Earthquake`

> EVs : `ATK 252` `SPE252` `HP 4`

>  Item : `Choice_Scarf` | `Choice_Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Calyrex-Shadow
    # 🐾────────────────────────────────────────────
    elif message == "!b 7873" or message == "!bcaly":
        title = "Battlemon : Calyrex-Shadow"
        desc = "Variant :  `Calyrex-Shadow`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/calyrex-shadow.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Astral-barrage` `Future-sight

> EVs : `SPA 252` `HP 252` `SPE 4`

> Item : `Choice_Specs`  | `Choice_specs`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Mega Mewtwo X
    # 🐾────────────────────────────────────────────
    elif message == "!b 7109" or message == "!bmmx":
        title = "Battlemon : Mega-MewTwo-X"
        desc = """"Battlemon : Mega-MewTwo-X

Variant : `Mega-Mewtwo-X`  | `Golden Mega-Mewtwo-X`

- Battle Item :
 `Life-Orb`   | `Choice-Band` | `Choice-Cloak`

- EVs :
`ATK 252` `HP 252` `SPE 4`"""
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/mewtwo-megax.gif"
        color = 0xC312D2

        embed.add_field(
            name=normal_battle_str,
            value=""">   Moves : `Drain-Punch` `Earthquake` `Foul-play` `Focus-Punch  | Dream-Eater | Ice-Punch`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value="""> `Focus-punch` `Drain-punch` `Power-up-punch` `Amnesia`
> Useful for Gmax melmetal""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Mewtwo
    # 🐾────────────────────────────────────────────
    elif message == "!b 150" or message == "!bmewtwo":
        title = "Battlemon : Mewtwo"
        desc = "Variant : `MewTwo` | `Golden MewTwo`"
        color = 0xC312D2
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/mewtwo.gif"

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves :`Future-Sight` `Aura-sphere` `Ice-Beam` `Shadow-Ball | Thunderbolt | Energy-Ball`
>     EVs : `SPA 252` `HP 252` `DEF 4`
>     Item : `Choice-Specs` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=setup_sweeper_str,
            value="""> Moves : `Recover` `Bulk-Up` `Calm-mind` `Stored-power`
>     EVs : `HP 252` `DEF 128` `SPD 128`
>     Item : `Leftovers` """,
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value="""> Moves : `Recover` `Bulk-Up` `Calm-mind` `Stored-power`
>     EVs : `SPA 252` `SPD 252` `HP 4`
>     Item : `Metronome` `Twisted-spoon` """,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Mega Mewtwo Y
    # 🐾────────────────────────────────────────────
    elif message == "!b 7121" or message == "!bmmy":
        title = "Battlemon : Mega-MewTwo-Y"
        desc = """Variant : `Mega-MewTwo-Y` | `Golden MewTwo-Y`

- Battle Item :
`Choice-Specs` | `Choice-Cloak`"""
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/mewtwo-megay.gif"
        color = 0xC312D2

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves :`Future-Sight` `Aura-sphere` `Ice-Beam` `Shadow-Ball | Thunderbolt | Energy-Ball`
>     EVs : `SPA 252` `HP 252` `DEF 4`
>     Item: `Choice-Specs` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value="""> Moves : `Recover` `Bulk-Up` `Calm-mind` `Stored-power`
>     EVs : `SPA 252` `SPD 252` `HP 4`
>     Item: `Choice-Specs` | `Choice-Cloak` | `Metronome`""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #              Mew
    # 🐾────────────────────────────────────────────
    elif message == "!b 151" or message == "!bmew":
        title = "Battlemon : Mew"
        desc = "Variant : `Mew` | `Golden Mew`"
        image_url = "https://play.pokemonshowdown.com/sprites/xyani/mew.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves :`Future-Sight` `Aura-sphere` `Ice-Beam` `Shadow-Ball | Thunderbolt | Energy-Ball`
>     EVs : `SPA 252` `HP 252` `DEF 4`
>     Item : `Choice-Specs` | `Choice-Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=setup_sweeper_str,
            value="""> Moves : `Roost` `Bulk-Up` `Calm-mind` `Stored-power` | `Dragon-pulse`
>     EVs : `HP 252` `DEF 128` `SPD 128`
>     Item : `Leftovers` """,
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value="""> Moves : `Recover` `Bulk-Up` `Calm-mind` `Stored-power`
>     EVs : `SPA 252` `SPD 252` `HP 4`
>     Item : `Metronome` `Twisted-spoon`""",
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Necrozma-Dawnwings
    # 🐾────────────────────────────────────────────
    elif message == "!bned" or message == "!b 7669":
        title = "Battlemon : Necrozma-Dawnwings"
        desc = "Variant :  `Necrozma-Dawnwings`"
        image_url = (
            "https://projectpokemon.org/images/shiny-sprite/necrozma-dawn-wings.gif"
        )
        color = 0xFD007D

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Future-sight` `Aura-Sphere` `Ice-Beam` `Thunderbolt`

> EVs : `SPA 252` `HP 252` `SPE 6`

> Item :  `Choice_Specs` | `Choice_Cloak` | `Twisted_Spoon`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Necrozma-Ultra
    # 🐾────────────────────────────────────────────
    elif message == "!bneu" or message == "!b 7693":
        title = "Battlemon : Necrozma-Ultra"
        desc = "Variant :  `Necrozma-Ultra`"
        image_url = "https://images-ext-1.discordapp.net/external/9PsaLeQT4jtiMy0ldFFcZb7qG11LXMBZIUr6d86hBU8/https/play.pokemonshowdown.com/sprites/xyani/necrozma-ultra.gif?width=273&height=144"
        color = 0xFFFF05

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Photon-Geyser` `Outrage` `Power-gem` `Earth-power | Flash-cannon`

> EVs : `SPA 252` `HP 252` `SPE 4`

> Item :  `Choice_Specs` | `Choice_Scarf` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Necrozma-Duskmane
    # 🐾────────────────────────────────────────────
    elif message == "!bnem" or message == "!b 7687":
        title = "Battlemon : Necrozma-Duskmane"
        desc = "Variant :  `Necrozma-Duskmane`"
        image_url = "https://images-ext-1.discordapp.net/external/hK3Y6uOIJI5PdrpqsY725TDkSCGU2MARUbz-zvAejz0/https/play.pokemonshowdown.com/sprites/xyani/necrozma-duskmane.gif?width=164&height=135"
        color = 0xA80051

        embed.add_field(
            name=normal_battle_str,
            value=""">  Moves : `Sunsteel-Strike` `Earthquake` `Stone-Edge` `Shadow-Claw`

>  EVs :  `ATK 252` `SPD 192` `HP 64`

> Item :  `Choice_Band` | `Choice_Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Kyurem-White
    # 🐾────────────────────────────────────────────
    elif message == "!bkyuw" or message == "!b 7513":
        title = "Battlemon : Kyurem-White"
        desc = "Variant : `Kyreum-White`  | `Golden Kyurem-White`"
        image_url = "https://images-ext-1.discordapp.net/external/EK53rnZqJFHS00hUfSN47McbHYHKMZkiAdMuSlF2Zzk/https/play.pokemonshowdown.com/sprites/xyani/kyurem-white.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value=""">  Moves : `Dragon-pulse | Outrage` `Ice-Beam | Freeze-dry` `Fusion-flare` `Earth-power`
> EVs : `SPA 252` `SPE 252` `HP 4`
> Item : `Choice_Specs`  | `Choice_scarf` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    # 🐾────────────────────────────────────────────
    #           Kyurem-Black
    # 🐾────────────────────────────────────────────
    elif message == "!bkyub" or message == "!b 7510":
        title = "Battlemon : Kyurem-Black"
        desc = "Variant : `Kyreum-Black`  | `Golden Kyurem-Black`"
        image_url = "https://images-ext-1.discordapp.net/external/gPaRQLrMcDzBTTkHWpMr5Gv8KkXqYVkrAjflCtG4X48/https/play.pokemonshowdown.com/sprites/xyani/kyurem-black.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value=""">  Moves : `Outrage` `Fusion-bolt` `Iron-head` ` Ice-Beam | Roost(orb) | Stone-edge`

> EVs : `ATK 252` `HP 252` `SPE 4`
> Item : `Life-Orb` | `Choice_Band` | `Choice_Cloak`""",
            inline=False,
        )
        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )
    # 🐾────────────────────────────────────────────
    #              Kyurem
    # 🐾────────────────────────────────────────────
    elif message == "!bkyu" or message == "!b 646":
        title = "Battlemon : Kyurem"
        desc = "Variant : `Kyreum`  | `Golden Kyurem`"
        image_url = "https://images-ext-1.discordapp.net/external/EX7r8ZMfM3XYDV4frcobj8r01jACqs1n9-3gv09zxa4/https/play.pokemonshowdown.com/sprites/xyani/kyurem.gif"
        color = get_random_color()

        embed.add_field(
            name=normal_battle_str,
            value="""> Moves : `Outrage` `Freeze-Dry` `Ice-Beam` `Earth-Power`
> EVs :  `SPA 252` `SPE 252` `HP 4`
> Battle Item :  `Choice_Scarf` | `Choice_Cloak`""",
            inline=False,
        )

        embed.add_field(
            name=world_boss_str,
            value=not_available_str,
            inline=False,
        )

    embed.title = title
    embed.description = desc
    embed.color = color
    embed.set_image(url=image_url)

    embed = default_monika_library_embed(user=message.author, embed=embed)

    mons_with_buttons = [
        "!bkyu",
        "!bkyub",
        "!bkyuw",
        "!bnem",
        "!bneu",
        "!bned",
        "!bmew",
        "!bmmy",
        "!bmewtwo",
        "!bmmx",
        "!b 646",
        "!b 7510",
        "!b 7513",
        "!b 7687",
        "!b 7693",
        "!b 7669",
        "!b 151",
        "!b 7121",
        "!b 150",
        "!b 7109",
    ]

    if message.content.lower() not in mons_with_buttons:
        await send_report_embed(message)
        await message.reply(embed=embed, mention_author=False)
    else:
        await send_report_embed(message)
        await send_battle_mon_embed_with_buttons(message, embed)


# 🐾────────────────────────────────────────────
#           Send Battle Mon with Buttons
# 🐾────────────────────────────────────────────
async def send_battle_mon_embed_with_buttons(
    message: discord.Message, embed: discord.Embed
):
    if message.content.lower() in [
        "!bmmx",
        "!bmewtwo",
        "!bmmy",
        "!bmew",
        "!b 7109",
        "!b 150",
        "!b 7121",
        "!b 151",
    ]:
        view = MewtwoButtons(
            message=message.content.lower(),
            initial_message=message.content.lower(),
            author_id=message.author.id,
        )
    elif message.content.lower() in [
        "!bkyu",
        "!bkyub",
        "!bkyuw",
        "!b 646",
        "!b 7510",
        "!b 7513",
    ]:
        view = KyuremButtons(
            message=message.content.lower(),
            initial_message=message.content.lower(),
            author_id=message.author.id,
        )
    elif message.content.lower() in [
        "!bned",
        "!bneu",
        "!bnem",
        "!b 7669",
        "!b 7693",
        "!b 7687",
    ]:
        view = NecrozmaButtons(
            message=message.content.lower(),
            initial_message=message.content.lower(),
            author_id=message.author.id,
        )
    await message.reply(embed=embed, view=view, mention_author=False)


# 🐾────────────────────────────────────────────
#              Mewtwo Buttons
# 🐾────────────────────────────────────────────
class MewtwoButtons(discord.ui.View):
    BUTTONS = [
        ("Mega Mewtwo X", "!bmmx", "mega_mewtwo_x"),
        ("Mewtwo", "!bmewtwo", "mewtwo"),
        ("Mega Mewtwo Y", "!bmmy", "mega_mewtwo_y"),
        ("Mew", "!bmew", "mew"),
    ]

    def __init__(self, message: str, initial_message: str, author_id: int):
        super().__init__(timeout=120)
        self.message = message
        self.author_id = author_id
        self.initial_message = initial_message
        self.disabled_button = self._get_button_key(initial_message)
        self._add_buttons_in_order()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return False
        return True

    def _get_button_key(self, message):
        mapping = {
            "!bmmx": "mega_mewtwo_x",
            "!bmewtwo": "mewtwo",
            "!bmmy": "mega_mewtwo_y",
            "!bmew": "mew",
        }
        return mapping.get(message, None)

    def _add_buttons_in_order(self):
        # Put the initial button first
        order = [b for b in self.BUTTONS if b[2] == self.disabled_button] + [
            b for b in self.BUTTONS if b[2] != self.disabled_button
        ]
        for label, msg, custom_id in order:
            self.add_item(
                self._make_button(
                    label, msg, custom_id, disabled=(custom_id == self.disabled_button)
                )
            )

    def _make_button(self, label, msg, custom_id, disabled=False):
        async def callback(interaction: discord.Interaction):
            embed = discord.Embed()
            embed = await send_battle_mon_embed(embed=embed, message=msg)
            self.disabled_button = custom_id
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = item.custom_id == custom_id
            await interaction.edit_message(embed=embed, view=self)

        btn = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=custom_id,
            disabled=disabled,
        )
        btn.callback = callback
        return btn


# 🐾────────────────────────────────────────────
#              Kyurem Buttons
# 🐾────────────────────────────────────────────
class KyuremButtons(discord.ui.View):
    BUTTONS = [
        ("Kyurem", "!bkyu", "kyurem"),
        ("Kyurem Black", "!bkyub", "kyurem_black"),
        ("Kyurem White", "!bkyuw", "kyurem_white"),
    ]

    def __init__(self, message: str, initial_message: str, author_id: int):
        super().__init__(timeout=120)
        self.message = message
        self.author_id = author_id
        self.initial_message = initial_message
        self.disabled_button = self._get_button_key(initial_message)
        self._add_buttons_in_order()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return False
        return True

    def _get_button_key(self, message):
        mapping = {
            "!bkyu": "kyurem",
            "!bkyub": "kyurem_black",
            "!bkyuw": "kyurem_white",
        }
        return mapping.get(message, None)

    def _add_buttons_in_order(self):
        order = [b for b in self.BUTTONS if b[2] == self.disabled_button] + [
            b for b in self.BUTTONS if b[2] != self.disabled_button
        ]
        for label, msg, custom_id in order:
            self.add_item(
                self._make_button(
                    label, msg, custom_id, disabled=(custom_id == self.disabled_button)
                )
            )

    def _make_button(self, label, msg, custom_id, disabled=False):
        async def callback(interaction: discord.Interaction):
            embed = discord.Embed()
            embed = await send_battle_mon_embed(embed=embed, message=msg)
            self.disabled_button = custom_id
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = item.custom_id == custom_id
            await interaction.edit_message(embed=embed, view=self)

        btn = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=custom_id,
            disabled=disabled,
        )
        btn.callback = callback
        return btn


# 🐾────────────────────────────────────────────
#           Necrozma Buttons
# 🐾────────────────────────────────────────────
class NecrozmaButtons(discord.ui.View):
    BUTTONS = [
        ("Necrozma-Dawnwings", "!bned", "necrozma_dawnwings"),
        ("Necrozma-Ultra", "!bneu", "necrozma_ultra"),
        ("Necrozma-Duskmane", "!bnem", "necrozma_duskmane"),
    ]

    def __init__(self, message: str, initial_message: str, author_id: int):
        super().__init__(timeout=120)
        self.message = message
        self.author_id = author_id
        self.initial_message = initial_message
        self.disabled_button = self._get_button_key(initial_message)
        self._add_buttons_in_order()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return False
        return True

    def _get_button_key(self, message):
        mapping = {
            "!bned": "necrozma_dawnwings",
            "!bneu": "necrozma_ultra",
            "!bnem": "necrozma_duskmane",
        }
        return mapping.get(message, None)

    def _add_buttons_in_order(self):
        order = [b for b in self.BUTTONS if b[2] == self.disabled_button] + [
            b for b in self.BUTTONS if b[2] != self.disabled_button
        ]
        for label, msg, custom_id in order:
            self.add_item(
                self._make_button(
                    label, msg, custom_id, disabled=(custom_id == self.disabled_button)
                )
            )

    def _make_button(self, label, msg, custom_id, disabled=False):
        async def callback(interaction: discord.Interaction):
            embed = discord.Embed()
            embed = await send_battle_mon_embed(embed=embed, message=msg)
            self.disabled_button = custom_id
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = item.custom_id == custom_id
            await interaction.edit_message(embed=embed, view=self)

        btn = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=custom_id,
            disabled=disabled,
        )
        btn.callback = callback
        return btn
