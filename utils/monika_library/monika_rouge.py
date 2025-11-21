import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log
from utils.monika_library.library import (
    default_monika_library_embed,
    get_random_color,
    send_report_embed,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   ⚔️ Monika Rouge Embed ⚔️
#   "Ah, so you wish to learn about Meow Rouge?"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_monika_rouge_main_embed(message: discord.Message):
    user = message.author
    color = get_random_color()
    embed = build_monika_rouge_sub_embed(
        topic="starter",
        color=color,
    )
    embed = default_monika_library_embed(user=user, embed=embed)
    embed.color = color
    view = MonikaRogueButtons(author_id=user.id, color=color)
    view.disable_initial_starter()
    await message.reply(embed=embed, view=view, mention_author=False)
    await send_report_embed(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔥 Monika Rogue Sub-Embeds Builder 🔥
#   "Here's some more detailed info on that topic!"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_monika_rouge_sub_embed(
    topic: str,
    color,
):

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Rogue Starter Mons Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if topic == "starter":
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        starter_embed = discord.Embed(title="Monika Rogue Starter Mons", color=color)
        starter_embed.add_field(
            name="Starter Mons Guide",
            value="""> Fire-type starters are among the strongest choices when beginning your MeowRogue runs.
> They offer excellent type coverage across most biomes and can snowball effectively when paired with the right moves.
> While you can pick any starter you like, this guide focuses on the most efficient and recommended ones for early and long-term success.""",
            inline=False,
        )
        starter_embed.add_field(
            name="Recommended Starter Pokémon",
            value="""> * Fuecoco
> * Chimchar
> * Cyndaquil
> * Charmander
> * Mudkip *(for water coverage)*
> * Beldum *(for strong late-game potential)*
-
> Fire-types like Fuecoco, Chimchar, and Cyndaquil are generally preferred due to their performance across multiple biome types. Mudkip and Beldum are great additions to round out your early team.""",
            inline=False,
        )
        starter_embed.add_field(
            name="*",
            value="""> * Fuecoco starts off somewhat slow but quickly becomes powerful thanks to its excellent movepool and signature move **Torch Song**, which boosts Special Attack each time it's used.
> * Chimchar and **Cyndaquil** can both learn **Burning Jealousy**, which is a powerful special move that punishes opponents who have stat boosts. These two also have flexible movepools that can support either physical or special playstyles.
> * *To optimize your starters:

> * Use `;move (pokemon-name)` to check what moves they can learn
> * Prioritize **Nasty Plot** or **Swords Dance** using the **Status Machine**
> * Once a setup move is learned, use the **Power Machine** to add coverage moves like:""",
            inline=False,
        )
        starter_embed.add_field(
            name="Example Movesets",
            value="""> **Fuecoco**: `torch-song`
> **Chimchar**:
>  * `earthquake`
>  * `metal claw`
>  * `shadow claw`
>  * `fire punch`
>  * `burning jealousy`

> * Physical Build: `swords dance + fire punch`
> * Special Build: `nasty plot + burning jealousy`

For Challenges guide, `!ch mr` or `!mrch`""",
            inline=False,
        )
        starter_embed.set_image(url=image_url)
        return starter_embed
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Rogue Endless/HC Guide 🔥
    # ━━━━━━━━━
    elif topic == "endless/hc":
        title = "Monika's Endless/HC guide"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        endless_embed = discord.Embed(title=title, color=color)
        endless_embed.add_field(
            name="Team Options",
            value="""> * **Team 1** – Arceus + Corviknight + 4 Golden Pokémon
>   * Stable and safe option
>   * Averages **\~200 waves per hour**
>   * Switch to Corviknight when facing **Ground-types** while Arceus is in lead
-
> * **Team 2** – Xerneas + Corviknight + 4 Golden Pokémon
>   * Higher risk, faster pace
>   * Averages **250+ waves per hour**
>   * Switch to Corviknight when facing **Steel** or **Poison-types** that are **1.5x your level or higher**""",
            inline=False,
        )

        endless_embed.add_field(
            name="Run Strategy",
            value="""> * It is recommended to **end the run after reaching wave 2000** and start over again.
> * This is to optimize **ticket farming** and avoid major scaling risks.
-
> - **Wave Scaling** increases as follows:
>   * After wave 200 → Levels increase by **1.5x**
>   * After wave 300 → Levels scale between **1.1x and 2.5x**""",
            inline=False,
        )
        endless_embed.add_field(
            name="Feathers and Upgrades",
            value="""> - **Upgrade all 6 feathers** on both Arceus and Corviknight **before wave 300**.
>   * This is critical to survive scaling and boost performance in long runs.""",
            inline=False,
        )
        endless_embed.add_field(
            name="Priority Items – Wave End Rewards",
            value="""> * Always pick these when available:
>   * Rogue Coin
>   * Golden Ticket
>   * Shiny Ticket""",
            inline=False,
        )

        endless_embed.add_field(
            name="Before Wave 200 – Max These First >",
            value="""> * Treasure Hunter (**2 Max Stacks**)
> * Overload (**5 Max Stacks**)
> * Glutton (**2 Max Stacks**)
> * Amulet Coin (**10 Max Stacks**)
> * Shiny Charm (**10 Max Stacks**)
> * Max Mushroom (**3 Stacks**) to unlock Gmax
> * EXP Share (**25 Max Stacks**)
-
> * Choose one of the following based on which is closest to full:
>   * EXP Charm
>   * Mega Bracelet
>   * Dynamax Band
>   * Golden Razz Berry
-
> * Ball Priority (**All 99 Max Stacks**):
>   * Premier Ball
>   - Master Ball *(pick 1 before PRB in case of Golden)*
>   * Ultra Ball
>   * Great Ball
>   * Poké Ball
>   * Candy Jar""",
            inline=False,
        )
        endless_embed.add_field(
            name="After Wave 200 – Remaining Items >",
            value="""> * Pick up any of the items above that aren’t yet maxed.
-
> * Then follow this **pickup priority order**:
>   * X-Defense
>   * Candy Jar (continue stacking to 99)
>   * Prize Ticket
>   * X-Sp. Defense
-
> * **Reroll Strategy** if you're missing priority items:
>   * 4 rerolls every 10 waves until wave 600
>   * 3 rerolls every 10 waves until wave 1000
>   * 2 rerolls every 10 waves until wave 1500
-
> * If **X-Defense exceeds 125+ stacks**, prioritize:
>   * Candy Jars
>   * Prize Ticket
>   * Then return to X-Defense
For Challenges guide, `!ch mr` or `!mrch`""",
            inline=False,
        )
        endless_embed.set_image(url=image_url)
        return endless_embed

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Rogue Items Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif topic == "items":
        title = "Monika's Rogue Items"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        desc = """> * Amulet Coin — Increases Pokédollars earned from all sources by 10% (Max Stack: 10)
> - Golden Razz Berry — Increases Legendary Pokémon encounter rate by 5% (Max Stack: 10)
> * Shiny Charm — Boosts Luck by 5% (Max Stack: 10)
-
> - Treasure Hunter — +1 free item offered every wave (Max Stack: 2)
> * Glutton — +1 healing item every wave (Max Stack: 2)
> - Overload — +5% chance to triple your damage (Max Stack: 5)
-
> * Mega Bracelet — Enables Mega encounters; Mega Stones appear as item rewards for your team’s evolutions. Each bracelet adds +5% Mega encounter rate (Max Stack: 10)
> - Dynamax Band — Enables Gigantamax encounters; Max Mushrooms appear as item rewards. Each band adds +5% Dynamax encounter rate (Max Stack: 10)
> * Max Mushroom — Used to transform certain Pokémon into their Gigantamax variant for the rest of your run (Requires 3 mushrooms)
-
> - EXP. Charm — Boosts EXP earned by 20% (Max Stack: 10)
> * EXP. Share — Distributes full EXP across your team; adds +5% EXP earned per stack (Max Stack: 25)
> - Candy Jar — Increases levels earned from Rare Candies by 1 (Max Stack: 99)
> * Rare Candy — Increases your leading Pokémon’s level by 1
-
> - Rogue Coin — Receive a Rogue Coin to spend in the MeowRogue shop
> * Golden Ticket — Exchange for a chance at obtaining a Golden Pokémon for use in future runs
> - Shiny Ticket — Exchange for a chance at obtaining a Shiny Pokémon for use in future runs
> * Prize Ticket — Exchange for a chance at obtaining certain Pokémon for use in future runs
-
> * Status Machine — Adds a random status move to your leading Pokémon's moveset. If it already has 4 moves, you can choose one to replace
> - Power Machine — Adds a random physical or special move to your leading Pokémon's moveset. If it already has 4 moves, you can choose one to replace
-
> * X. Attack — Temporarily raises your team's ATK stage by +2
> - X. Defense — Temporarily raises your team's DEF stage by +2
> * X. Sp. Atk — Temporarily raises your team's Sp. ATK stage by +2
> - X. Sp. Def — Temporarily raises your team's Sp. DEF stage by +2
> * X. Speed — Temporarily raises your team's SPEED stage by +2
> - X. Accuracy x5 — Temporarily raises your team's ACCURACY stage by +2 for 5 waves
> * Dire Hit — Temporarily raises your team's critical hit rate stage by +1 (max stage: 4)
-
> * Big Pearl — Grants 5,000 coins to your balance
> * Big Nugget — Grants 5,000 coins to your balance
> - Comet Shard — Grants 10,000 coins to your balance
> * Star Piece — Grants 2,500 coins to your balance
-
> * **Moomoo Milk** — Heals leading Pokémon by 100 HP
> * **Super Potion** — Heals 60 HP or 20% of max HP (whichever is higher)
> * **Potion** — Heals 20 HP or 5% of max HP (whichever is higher)
> * **Max Potion** — Fully restores HP of the leading Pokémon
> * **Full Restore** — Fully restores HP and cures all status conditions
> * **Energy Powder** — Heals 50 HP, but lowers friendship
> * **Lemonade** — Heals 80 HP
> * **Energy Root** — Heals 200 HP, but lowers friendship
> * **Soda Pop** — Heals 50 HP
> * **Hyper Potion** — Heals 120 HP or 50% of max HP (whichever is higher)
> * **Full Heal** — Removes all status effects on your leading Pokémon
-
> * **Muscle Feather** — +42 ATK EVs to leading Pokémon
> * **Genius Feather** — +42 Sp. ATK EVs to leading Pokémon
> * **Health Feather** — +42 HP EVs to leading Pokémon
> * **Swift Feather** — +42 SPEED EVs to leading Pokémon
> * **Resist Feather** — +42 DEF EVs to leading Pokémon
> * **Clever Feather** — +42 Sp. DEF EVs to leading Pokémon
-
> *Note: The EV cap per stat is 252. You can max out an EV with just 6 feathers per stat.*"""
        items_embed = discord.Embed(title=title, description=desc, color=color)
        items_embed.set_image(url=image_url)
        return items_embed

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Rogue Upgrades Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif topic == "upgrades":
        title = "Monika's Rogue Upgrades"
        desc = """## Upgrades:
It is recommended to upgrade in the following order..."""
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        upgrades_embed = discord.Embed(title=title, description=desc, color=color)
        upgrades_embed.set_image(url=image_url)
        upgrades_embed.add_field(
            name="1. Get exp-share level 1",
            value="> - This will make sure u don't have re-roll the wave rewards and you can keep your rest of the team same as the lead Pokemon.",
            inline=False,
        )

        upgrades_embed.add_field(
            name="2. Coin Master Max (10 levels)",
            value="> - Each level increases your wave coin rewards by 5%. upgrading this to max will help doing other upgrades faster.",
            inline=False,
        )
        upgrades_embed.add_field(
            name="3. Healthy Start Max (5 levels)",
            value="> - `Healthy Start` increases the base stats of Pokemon selected before you start your run by 5% on each level. Currently all base stats increase are working except hp (Will be added later in mr).",
            inline=False,
        )

        upgrades_embed.add_field(
            name="4. Crutches",
            value="> - Crutches increases your points with which you can pick pokemon before each run by +1 for each level. level of crutches upgrade depends on your requirement (Recommended lvl 5 crutches so you can get Arceus/Xerneas + Corviknight+ 4 golden Pokemon later on into hardcore runs).",
            inline=False,
        )
        upgrades_embed.add_field(
            name="5. Lucky Charm Max (10 Levels)",
            value="""> - Lucky charms max will help you increase your luck by +1 for each level.
> - What is Luck? - Every % of luck you have boosts your coins earned every wave as well as Golden, Shiny, & Legendary rates.
> - For every Shiny  in your team, your luck increases by 5%
> - For every Golden in your team, your luck increases by 10%""",
            inline=False,
        )
        upgrades_embed.add_field(
            name="6. Haggler Max (5 Levels)",
            value="> - 5% reduced cost for shop items per level.",
            inline=False,
        )

        upgrades_embed.add_field(
            name="7. What Next?",
            value="""> you can upgrade `EXP-share` and `Large-pack` max after doing all this as it will be helpful later in hardcore runs.


For Challenges guide, `!ch mr` or `!mrch`""",
            inline=False,
        )

        return upgrades_embed

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Rogue Main Teams Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif topic == "main teams":
        title = "Monika's Rogue Main Carry mons"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        main_teams_embed = discord.Embed(title=title, color=color)
        main_teams_embed.set_image(url=image_url)
        main_teams_embed.add_field(
            name="Classic Mode",
            value="""> * Classic mode is relatively easy to complete.
> * Use a **Fire-type starter Pokémon** such as Fuecoco, Chimchar, or Cyndaquil.
> * Equip them with **setup moves** like `Swords Dance` or `Nasty Plot`, then add strong offensive moves using the `Power-machine`
> * These setups alone are enough to comfortably clear the full run.""",
            inline=False,
        )

        main_teams_embed.add_field(
            name="Endless Mode",
            value="""> * You can start with the **same carry Pokémon** that worked in Classic mode.
> * During the run, prioritize catching the following:
>   * **Arceus**
>   * **Xerneas**
>   * **Elgyem** or **Beheeyem**
>   * Any of the **Rookidee line** (for access to Corviknight)
> * These Pokémon will carry you through the later waves and challenges more consistently.""",
            inline=False,
        )

        main_teams_embed.add_field(
            name="Hardcore Mode",
            value="""> * The same carry core applies here: **Arceus**, **Xerneas**, **Beheeyem**, and **Corviknight**.
> * These Pokémon are required to handle certain Hardcore-specific challenges.
> * Start with high-luck, high-power setups and build around these staples as you catch and evolve them throughout the run.""",
            inline=False,
        )
        main_teams_embed.add_field(
            name="Recommended Movesets",
            value="""> - **Arceus** *(equip Zap Plate via wave-end reward)*
>   * `Meteor Beam`, `Stored Power`, `Cosmic Power`, `Recover`
> - **Beheeyem** *(Useful for a specific Hardcore challenge)*
>  * Same moveset as Arceus
> - **Corviknight** | **Gmax-Corviknight** *(Get Dynamax-band and find 3x max-mushroon))*
>   * `Roost`, `Power Trip`, `Bulk Up`, `Max Quake`
> - **Xerneas**
>   * `Moonblast`, `Draining Kiss`, `Psychic`, `Geomancy`
For Challenges guide, `!ch mr` or `!mrch`""",
            inline=False,
        )
        return main_teams_embed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔥 Monika Rogue Buttons View 🔥
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MonikaRogueButtons(discord.ui.View):
    def __init__(self, author_id: int, color):
        super().__init__(timeout=120)
        self.color = color
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "These buttons aren't for you!", ephemeral=True
            )
            return False

    @discord.ui.button(label="Starter Mons", style=discord.ButtonStyle.primary)
    async def starter_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_embed(
            topic="starter",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Endless/HC Guide", style=discord.ButtonStyle.primary)
    async def endless_hc_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_embed(
            topic="endless/hc",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Items", style=discord.ButtonStyle.primary)
    async def items_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_embed(
            topic="items",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Upgrade", style=discord.ButtonStyle.primary)
    async def upgrades_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_embed(
            topic="upgrades",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Main Teams", style=discord.ButtonStyle.primary)
    async def main_teams_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_embed(
            topic="main teams",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    def disable_initial_starter(self):
        for child in self.children:
            if hasattr(child, "label") and child.label == "Starter Mons":
                child.disabled = True
            else:
                child.disabled = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔥 Monika Rogue Send Rouge Challenges Embed 🔥
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_monika_rogue_challenges_embed(message:discord.Message):
    user = message.author
    color = get_random_color()
    embed = build_monika_rouge_sub_challenges_embed(
        topic="classic",
        color=color,
    )
    embed = default_monika_library_embed(user=user, embed=embed)
    embed.color = color
    view = MonikaRogueChallengesButtons(author_id=user.id, color=color)
    view.disable_initial_classic()
    await message.reply(embed=embed, view=view, mention_author=False)
    await send_report_embed(message)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔥 Monika Rogue Challenges Embed Builder 🔥
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_monika_rouge_sub_challenges_embed(topic: str, color):

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Classic Challenges Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if topic == "classic":
        title = "Monika Rogue Classic Challenges"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        desc = """> ## 1. Complete Classic Mode without using any Healing Items
> * Use **Xerneas** (heal with `Draining Kiss`) or **Arceus** (heal with `Recover`)
> * Avoid picking up healing items or triggering Glutton passive
-
> ## 2. Complete Classic Mode using Just 1 Pokémon
> * Use **Xerneas** or **Arceus** as your solo carry
> * Start with only 1 Pokémon in your party
-
> ## 3. Complete Classic Mode while Having Caught 10 Pokémon
> * Start your run with **6 Pokémon** already selected
> * This prevents **level scaling** increases when catching more Pokémon
> * Catch 4 additional Pokémon during the run to hit 10
-
> ## 4. Complete Classic Mode with ONLY Charizard Forms
> * Allowed Forms:
>   * **Charizard**
>   * **Mega Charizard X / Y**
>   * **Gigantamax Charizard**
> * Shiny variants **do not count**
> * Recommended Moveset (farm in Endless):
>   * `Solar Beam` / `Max Overgrowth`
>   * `Max Wildfire` / `Max Flare` / `Max Darkness`
>   * `Max Airstream`
>   * `Roost`
-
> ## 5. Complete Classic Mode with ONLY Water-Type Pokémon
> * Use **Arceus** with **Splash Plate**
> * Alternatively, use any **Water-type Legendary**
> * Equip setup moves like `Cosmic Power` or `Calm Mind`
-
> ## 6. Complete Classic Mode with ONLY Dragon-Type Pokémon
> * Use **Arceus** with **Draco Plate**
> * Alternatively, use any **Dragon-type Legendary**
> * Stack setup moves to carry the run

> ## 7. Catch a Legendary Pokémon in a Classic Run
> * RNG-dependent — just keep playing until a Legendary spawns
> * Use Master Ball or high-tier Balls to secure it
-
> ## 8. Heal 25,000 Health from Shop Items in a Classic Run
> * Use **Xerneas**, **Arceus**, or **Beheeyem**
> * Take intentional **burn** or **poison** early by stalling with setup moves
> * Drop HP to low levels, then heal at **every wave end shop**
> * Repeat this each wave until 25,000 HP healed total
"""
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Endless Challenges Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif topic == "endless":
        title = "Monika Rogue Endless Challenges"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        desc = """> ## 1. Reach Wave 500
> * Can be done using **Arceus-Electric** or **Xerneas** paired with **Corviknight**
> * Standard carry core setup for early Endless success
-
> ## 2. Reach Wave 1,000
> * Use the same team from Challenge 1
> * You may also include all 3: **Arceus**, **Xerneas**, and **Corviknight**
-
> ## 3. End a Run on Wave 2,000+ with at Most 3 Pokémon on Your Team
> * Use **Arceus**, **Xerneas**, and **Corviknight** — do not catch additional Pokémon
> * If you have **not yet caught a Golden Pokémon**, avoid catching one until after this challenge
> * If you do catch a Golden before finishing this challenge, you must restart it from the beginning
-
> ## 4+. Catch Pokémon of Various Rarities in an Endless Run
> * These challenges involve catching **Shiny**, **Golden**, **Legendary**, or **Gmax** Pokémon
> * Simply use a **Master Ball** when you encounter one to complete these
"""

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   🔥 Monika Hardcore Challenges Guide 🔥
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif topic == "hardcore":
        title = "Monika Rogue Hard Core Challenges"
        image_url = "https://cdn.discordapp.com/attachments/1380006264897015849/1381777440233488467/end2.png?ex=6851fa85&is=6850a905&hm=57887b42917742eb5ffce20d856d4ee02da17f675bc5fdce8ed90e56a5416a1c&"
        desc = """> ## 1. Reach Wave 250
> * Can be done using **Arceus** or **Xerneas** alone
> * You can also use **Corviknight** to complete challenges 1, 2, and 3 in the same run
> * Recommended to first complete using **Arceus** only to clear both challenge 1 and 2 safely
-
> ## 2. Reach Wave 250 with Only 1 Pokémon on Your Team on Every Wave
> * Use **Arceus** or **Xerneas**
> * Avoid adding any other Pokémon during the run
-
> ## 3. Reach Wave 250 Without Using (or Catching) Any Legendary, Shiny, Golden, Mega, or Gigantamax Pokémon
> * Use a team of **Charizard**, **Beheeyem**, and **Corviknight**
> * Start with **Charizard** as your main carry until it faints
> * Use **Beheeyem** as your new main lead and **Corviknight** as backup
> *Beheeyem or Clefable can use the same moveset as Arceus. You can also try with Charmander + Corviknight only.
-
> ## 4. Reach Wave 500 Without Taking Any Overloads
> * Use **Xerneas** or **Arceus** with **Corviknight**
> * Avoid picking up the Overload item at all during the run
-
> ## 5. Reach Wave 500 Without Any Pokémon on Your Team Fainting
> * Use the same team as in Challenge 4: **Xerneas**/**Arceus** + **Corviknight**
> * Make sure no team member faints at any point during the run"""

    challenge_embed = discord.Embed(title=title, description=desc, color=color)
    challenge_embed.set_image(url=image_url)
    return challenge_embed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🔥 Monika Rogue Challenges Buttons View 🔥
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MonikaRogueChallengesButtons(discord.ui.View):
    def __init__(self, author_id: int, color):
        super().__init__(timeout=120)
        self.color = color
        self.author_id = author_id
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "These buttons aren't for you!", ephemeral=True
            )
            return False
    @discord.ui.button(label="Classic", style=discord.ButtonStyle.primary)
    async def classic_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_challenges_embed(
            topic="classic",
            color=self.color,
        )
        #disable this button, and enable others
        for child in self.children:
            child.disabled = child == button

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Endless", style=discord.ButtonStyle.primary)
    async def endless_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_challenges_embed(
            topic="endless",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="HC", style=discord.ButtonStyle.primary)
    async def hardcore_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = build_monika_rouge_sub_challenges_embed(
            topic="hardcore",
            color=self.color,
        )
        for child in self.children:
            child.disabled = child == button
        await interaction.response.edit_message(embed=embed, view=self)

    def disable_initial_classic(self):
        for child in self.children:
            if hasattr(child, "label") and child.label == "Classic":
                child.disabled = True
            else:
                child.disabled = False