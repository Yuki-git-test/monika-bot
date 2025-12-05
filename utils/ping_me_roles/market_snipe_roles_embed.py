import discord
from discord.ui import Button, View

from constants.vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.logs.pretty_log import pretty_log
from utils.visuals.colors import get_random_monika_color

EMBED_COLOR = 0xFF9999
from .general_roles_embed import Server_Booster_Only_Button, format_role_description


class Market_Snipe_Role_Button(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji="🎯",
            custom_id="market_snipe_role_button",
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            user = interaction.user
            view, embed = build_market_snipe_roles_embed(guild, user)
            if view and embed:
                await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "An error occurred while building the Market Snipe roles embed.",
                    ephemeral=True,
                )
        except Exception as e:
            pretty_log("error", f"Error in Market Snipe Role Button callback: {e}")
            await interaction.response.send_message(
                "An unexpected error occurred.", ephemeral=True
            )


def build_market_snipe_roles_embed(guild: discord.Guild, user: discord.Member):
    try:
        view = discord.ui.View(timeout=None)

        # Get roles
        common_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.common_snipe)
        uncommon_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.uncommon_snipe)
        rare_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.rare_snipe)
        super_rare_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.super_rare_snipe)
        legendary_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.legendary_snipe)
        shiny_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.shiny_snipe)
        golden_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.golden_snipe)
        gigantamax_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.gmax_snipe)
        event_exclusive_snipe_role = guild.get_role(
            VN_ALLSTARS_ROLES.eventexclusives_snipe
        )
        paldean_snipe_role = guild.get_role(VN_ALLSTARS_ROLES.paldean_snipe)

        roles = []
        if common_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.common
            view.add_item(
                Server_Booster_Only_Button(common_snipe_role, "Common Snipe", emoji)
            )
            roles.append((emoji, common_snipe_role))

        if uncommon_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.uncommon
            role = uncommon_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Uncommon Snipe", emoji))
            roles.append((emoji, role))

        if rare_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_rare
            role = rare_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Rare Snipe", emoji))
            roles.append((emoji, role))

        if super_rare_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_superrare
            role = super_rare_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Super Rare Snipe", emoji))
            roles.append((emoji, role))

        if legendary_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_legendary
            role = legendary_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Legendary Snipe", emoji))
            roles.append((emoji, role))

        if shiny_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_shiny
            role = shiny_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Shiny Snipe", emoji))
            roles.append((emoji, role))

        if golden_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_golden
            role = golden_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Golden Snipe", emoji))
            roles.append((emoji, role))

        if gigantamax_snipe_role:
            emoji = VN_ALLSTARS_EMOJIS.vna_gmax
            role = gigantamax_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Gigantamax Snipe", emoji))
            roles.append((emoji, role))

        if event_exclusive_snipe_role:
            emoji = "🍒"
            role = event_exclusive_snipe_role
            view.add_item(
                Server_Booster_Only_Button(role, "Event Exclusive Snipe", emoji)
            )
            roles.append((emoji, role))
            
        if paldean_snipe_role:
            emoji = "🌋"
            role = paldean_snipe_role
            view.add_item(Server_Booster_Only_Button(role, "Paldean Snipe", emoji))
            roles.append((emoji, role))

        if roles:
            desc = format_role_description(roles)
        else:
            desc = "No Market Snipe roles are currently available."

        title = "🎯 Market Snipe Roles"
        embed = discord.Embed(
            title=title,
            description=desc,
            color=EMBED_COLOR,
        )
        return view, embed

    except Exception as e:
        pretty_log("error", f"Error building Market Snipe roles embed: {e}")
        return None, None
