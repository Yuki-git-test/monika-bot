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


# 🍬 Helper: Format the role list into an embed-friendly description
def format_role_description(line: list[tuple[str, discord.Role]]) -> str:
    parts = []
    for emoji, role in line:
        parts.append(f"{emoji} {role.mention}")
    return "\n".join(parts)


class ToggleRoleButton(Button):
    def __init__(self, role: discord.Role, label: str, emoji: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"toggle_role_{role.id}",
        )
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        role = self.role
        try:
            if role in member.roles:
                await member.remove_roles(role)
                pretty_log(f"Removed role {role.name} from {member.display_name}")
                await interaction.response.send_message(
                    f"Removed role **{role.mention}** from you", ephemeral=True
                )
            else:
                await member.add_roles(role)
                pretty_log(f"Added role {role.name} to {member.display_name}")
                await interaction.response.send_message(
                    f"Added role **{role.mention}** to you", ephemeral=True
                )
        except Exception as e:
            pretty_log(
                f"Error toggling role {role.name} for {member.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while trying to update your roles.", ephemeral=True
            )


class Server_Booster_Only_Button(Button):
    def __init__(self, role: discord.Role, label: str, emoji: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"server_booster_only_{role.id}",
        )
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        role = self.role
        SPECIAL_ROLE_IDS = [
            VN_ALLSTARS_ROLES.server_booster,
            VN_ALLSTARS_ROLES.top_monthly_grinder,
            VN_ALLSTARS_ROLES.diamond_donator,
            VN_ALLSTARS_ROLES.legendary_donator,
            VN_ALLSTARS_ROLES.shiny_donator,
            VN_ALLSTARS_ROLES.staff,
        ]
        try:
            if role in member.roles:
                await member.remove_roles(role)
                pretty_log(f"Removed role {role.name} from {member.display_name}")
                await interaction.response.send_message(
                    f"Removed role **{role.mention}** from you", ephemeral=True
                )
            else:
                if any(member.get_role(rid) for rid in SPECIAL_ROLE_IDS):
                    await member.add_roles(role)
                    pretty_log(f"Added role {role.name} to {member.display_name}")
                    await interaction.response.send_message(
                        f"Added role **{role.mention}** to you", ephemeral=True
                    )
                else:
                    special_roles_desc = ", ".join(
                        [f"<@&{rid}>" for rid in SPECIAL_ROLE_IDS]
                    )
                    await interaction.response.send_message(
                        f"You need to have at least one of the following roles to get **{role.mention}**: {special_roles_desc}",
                        ephemeral=True,
                    )
        except Exception as e:
            pretty_log(
                f"Error toggling role {role.name} for {member.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while trying to update your roles.", ephemeral=True
            )


class General_Roles_Button(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji="🎀",
            custom_id="general_roles_button",
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            user = interaction.user
            view, embed = build_general_roles_embed(guild, user)
            if view and embed:
                await interaction.response.send_message(
                    embed=embed,
                    view=view,
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "An error occurred while building the roles embed.",
                    ephemeral=True,
                )
                pretty_log(
                    "error",
                    f"Failed to build General Roles Embed for {interaction.user.display_name}",
                )
        except Exception as e:
            pretty_log(
                f"Error in General Roles Button callback for {interaction.user.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while processing your request.", ephemeral=True
            )


def build_general_roles_embed(guild: discord.Guild, user: discord.Member):
    try:
        view = discord.ui.View(timeout=None)

        # Server Roles
        annoucements_role = guild.get_role(VN_ALLSTARS_ROLES.announcments)

        # Pokemeow Roles
        giveaway_role = guild.get_role(VN_ALLSTARS_ROLES.giveaways)
        golden_hour_role = guild.get_role(VN_ALLSTARS_ROLES.golden_hour_ping)
        lottery_role = guild.get_role(VN_ALLSTARS_ROLES.lottery)
        drops_role = guild.get_role(VN_ALLSTARS_ROLES.drops)
        incense_role = guild.get_role(VN_ALLSTARS_ROLES.incense_ping)
        meow_promo_team = guild.get_role(VN_ALLSTARS_ROLES.meow_promo)
        ee_spawn_ping = guild.get_role(VN_ALLSTARS_ROLES.ee_spawn_ping)
        daily_ping = guild.get_role(VN_ALLSTARS_ROLES.daily_ping)
        calm_waters = guild.get_role(VN_ALLSTARS_ROLES.calm_waters)
        shiny_bonus = guild.get_role(VN_ALLSTARS_ROLES.shiny_bonus)
        os_lotto_ping = guild.get_role(VN_ALLSTARS_ROLES.os_lotto_ping)

        games = guild.get_role(VN_ALLSTARS_ROLES.games)

        as_spawn_ping = guild.get_role(VN_ALLSTARS_ROLES.as_spawn_ping)
        as_rare_spawn_ping = guild.get_role(VN_ALLSTARS_ROLES.as_rare_spawn_hunter)

        roles = []
        # Server Roles
        if annoucements_role:
            view.add_item(
                ToggleRoleButton(
                    role=annoucements_role,
                    label="Announcements",
                    emoji="📢",
                )
            )
            roles.append(("📢", annoucements_role))

        # Pokemeow Roles
        if giveaway_role:
            view.add_item(
                ToggleRoleButton(
                    role=giveaway_role,
                    label="Giveaways",
                    emoji="🎁",
                )
            )
            roles.append(("🎁", giveaway_role))

        if golden_hour_role:
            view.add_item(
                ToggleRoleButton(
                    role=golden_hour_role,
                    label="Golden Hour Ping",
                    emoji="🐟",
                )
            )
            roles.append(("🐟", golden_hour_role))
        if calm_waters:
            view.add_item(
                ToggleRoleButton(
                    role=calm_waters,
                    label="Calm Waters Ping",
                    emoji="🌊",
                )
            )
            roles.append(("🌊", calm_waters))

        if lottery_role:
            view.add_item(
                ToggleRoleButton(
                    role=lottery_role,
                    label="Lottery",
                    emoji="🎟️",
                )
            )
            roles.append(("🎟️", lottery_role))
        if os_lotto_ping:
            view.add_item(
                ToggleRoleButton(
                    role=os_lotto_ping,
                    label="OS Lotto Ping",
                    emoji="🎰",
                )
            )
            roles.append(("🎰", os_lotto_ping))

        if drops_role:
            view.add_item(
                ToggleRoleButton(
                    role=drops_role,
                    label="Drops",
                    emoji="🎊",
                )
            )
            roles.append(("🎊", drops_role))

        if incense_role:
            view.add_item(
                ToggleRoleButton(
                    role=incense_role,
                    label="Incense Ping",
                    emoji="💠",
                )
            )
            roles.append(("💠", incense_role))
        if daily_ping:
            view.add_item(
                ToggleRoleButton(
                    role=daily_ping,
                    label="Daily Ping",
                    emoji="📅",
                )
            )
            roles.append(("📅", daily_ping))
        if shiny_bonus:
            view.add_item(
                ToggleRoleButton(
                    role=shiny_bonus,
                    label="Shiny Bonus Ping",
                    emoji="✨",
                )
            )
            roles.append(("✨", shiny_bonus))

        if meow_promo_team:
            emoji = VN_ALLSTARS_EMOJIS.vna_golden
            view.add_item(
                ToggleRoleButton(
                    role=meow_promo_team,
                    label="Meow Promo Team",
                    emoji=emoji,
                )
            )
            roles.append((emoji, meow_promo_team))

        if games:
            emoji = "🎮"
            view.add_item(
                ToggleRoleButton(
                    role=games,
                    label="Games",
                    emoji=emoji,
                )
            )
            roles.append((emoji, games))
        if ee_spawn_ping:
            emoji = VN_ALLSTARS_EMOJIS.vna_gmax
            view.add_item(
                ToggleRoleButton(
                    role=ee_spawn_ping,
                    label="EE Spawn Ping",
                    emoji=emoji,
                )
            )
            roles.append((emoji, ee_spawn_ping))

        if as_spawn_ping:
            emoji = VN_ALLSTARS_EMOJIS.vna_pokeball
            view.add_item(
                ToggleRoleButton(
                    role=as_spawn_ping,
                    label="AS Spawn Ping",
                    emoji=emoji,
                )
            )
            roles.append((emoji, as_spawn_ping))

        if as_rare_spawn_ping:
            emoji = VN_ALLSTARS_EMOJIS.premierball
            view.add_item(
                Server_Booster_Only_Button(
                    role=as_rare_spawn_ping,
                    label="AS Rare Spawn Hunter",
                    emoji=emoji,
                )
            )
            roles.append((emoji, as_rare_spawn_ping))

        if roles:
            desc = format_role_description(roles)
        else:
            desc = "No roles available at the moment."

        title = "🎀 General Roles"
        embed = discord.Embed(
            title=title,
            description=desc,
            color=EMBED_COLOR,
        )

        return view, embed

    except Exception as e:
        pretty_log("error", f"Error building General Roles Embed: {e}")
        return None, None
