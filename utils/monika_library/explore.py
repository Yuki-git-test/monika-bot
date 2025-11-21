import discord
from discord.ext import commands
from discord.ui import Button, View

from constants.explore import *
from utils.logs.pretty_log import pretty_log
from utils.monika_library.library import (
    default_monika_library_embed,
    get_random_color,
    send_report_embed,
)


def map_label(secret_key: str) -> str:
    # Remove all non-numeric suffix, default to 1 if none found
    import re

    match = re.search(r"(\d+)$", secret_key)
    map_num = int(match.group(1)) if match else 1
    return f"Map {map_num}"


class SecretSelectionView(View):
    """
    💙 Interactive view with buttons for each secret in a map.

    Only the user with matching user_id can interact to switch secrets.

    Clicking a secret button updates the embed to show that secret's info,
    and disables that secret's button to show it’s active.
    """

    def __init__(self, exp_helper, explore_map: str, current_secret: str, user_id: int):
        super().__init__(timeout=None)  # persistent view, no timeout
        self.exp_helper = exp_helper
        self.map_key = explore_map
        self.current_secret = current_secret
        self.user_id = user_id

        # Load all secrets for this map, e.g. {"sg1": "...", "sg2": "..."}
        self.secrets = self.exp_helper.list_secrets(self.map_key)

        # Add one button per secret to the view
        for secret_key in self.secrets.keys():
            self.add_item(self.make_button(secret_key))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """👮 Allow only the authorized user to interact with buttons."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Sorry, this button isn't for you! 💢", ephemeral=True
            )
            return False
        return True

    def make_button(self, secret_key):
        """🎛️ Create a button for a secret, disabling it if it's currently selected."""
        label = map_label(secret_key)

        button = Button(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"secret_{secret_key}",
            disabled=(secret_key == self.current_secret),  # disable currently selected
        )

        async def callback(interaction: discord.Interaction):
            try:
                self.current_secret = secret_key
                self.clear_items()
                for sk in self.secrets.keys():
                    self.add_item(self.make_button(sk))

                # Rebuild the embed for the newly selected secret
                embed = await build_sub_secret_embed(
                    self.exp_helper, self.map_key, self.current_secret
                )

                await interaction.response.edit_message(embed=embed, view=self)
            except Exception:
                await interaction.response.send_message(
                    "An error occurred while switching secrets. Please try again later.",
                    ephemeral=True,
                )

        button.callback = callback
        return button


async def send_main_explore_embed(
    message: discord.Message,
):
    """
    🎀 Build the main secret embed and the button view for navigating secrets in a map.

    Parameters:
    - guild: Discord guild to get icon or other guild-related info.
    - explore_map: The map key, e.g. 'sg', 'sf', 'sw', 'su'.
    - user_id: Discord user ID allowed to interact with the buttons.

    Returns:
    - If the map has no secrets (like 'su'), returns just the embed.
    - Otherwise returns a tuple: (embed, SecretSelectionView, None)
    """

    user_id = message.author.id
    content = message.content.lower()
    explore_map = content.strip("!ex")
    exp_helper = ExploreHelper(EXPLORE_DICT)

    # For initial display, pick the first secret key available or a sensible default
    secret_keys = list(exp_helper.list_secrets(explore_map).keys())
    initial_secret = secret_keys[0] if secret_keys else None
    # If map is 'su' (underwater) or has no secrets, return embed only

    desc = exp_helper.get_text(explore_map)
    color = exp_helper.get_color(explore_map)
    header_icon = exp_helper.get_header_icon(explore_map)
    footer_icon = exp_helper.get_footer_icon(explore_map)
    header_text = exp_helper.get_header_text(explore_map)
    footer_text = exp_helper.get_footer_text(explore_map)
    image_url = exp_helper.get_image(explore_map, explore_map)

    embed = discord.Embed(description=desc, color=color)
    embed.set_author(name=header_text, icon_url=header_icon)
    embed.set_footer(text=footer_text, icon_url=footer_icon)
    embed.set_image(url=image_url)

    embed = default_monika_library_embed(user=message.author, embed=embed)
    embed.color = color
    await send_report_embed(message)

    if explore_map == "su":
        await message.reply(embed=embed, mention_author=False)
    else:
        view = SecretSelectionView(exp_helper, explore_map, initial_secret, user_id)
        await message.reply(embed=embed, view=view, mention_author=False)


async def build_sub_secret_embed(exp_helper, explore_map: str, secret_key: str):
    """
    ✨ Build a Discord embed for a specific secret in a map.

    Parameters:
    - exp_helper: SDExploreHelper instance to fetch data from your secrets dict.
    - explore_map: The map key (e.g., 'sg', 'sf', 'sw', 'su') — identifies which map.
    - secret_key: The specific secret key within the map (e.g., 'sg1', 'sf2').

    Returns:
    - discord.Embed ready to send with the secret's text, colors, and icons.
    """
    secret_text = exp_helper.list_secrets(explore_map).get(
        secret_key, "No secret found. 💨"
    )
    color = exp_helper.get_color(explore_map)
    header_icon = exp_helper.get_header_icon(explore_map)
    footer_icon = exp_helper.get_footer_icon(explore_map)
    header_text = exp_helper.get_header_text(explore_map)
    footer_text = exp_helper.get_footer_text(explore_map)
    image_url = exp_helper.get_image(map_key=explore_map, image_key=secret_key)

    embed = discord.Embed(
        description=secret_text,
        color=color,
    )
    embed.set_author(name=header_text, icon_url=header_icon)
    embed.set_footer(text=footer_text, icon_url=footer_icon)
    embed.set_image(url=image_url)

    return embed
