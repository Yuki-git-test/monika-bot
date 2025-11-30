import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from constants.aesthetic import *
from constants.vn_allstars_constants import (
    MONIKA_EMBED_COLOR,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.essentials.pretty_defer import pretty_defer
from utils.essentials.role_checks import is_staff_member
from utils.logs.pretty_log import pretty_log


# 🍭──────────────────────────────
#   🎀 Modal: Staff Post Send
# 🍭──────────────────────────────
class Staff_Message_Send_Modal(Modal):
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.Member,
        channel: discord.TextChannel,
        ping_role: discord.Role = None,
    ):
        super().__init__(title="Message Details")
        self.bot = bot
        self.user = user
        self.channel = channel
        self.ping_role = ping_role

        self.content_input = TextInput(
            style=discord.TextStyle.paragraph,
            required=False,
            label="Message Content",
            placeholder="Enter the content of the message to send (Message Outside of Embed)",
            max_length=2000,
        )

        self.embed_title_input = TextInput(
            required=False,
            label="Embed Title",
            placeholder="Enter the title of the embed (Optional)",
            max_length=256,
        )

        self.embed_description_input = TextInput(
            style=discord.TextStyle.paragraph,
            required=False,
            label="Embed Description",
            placeholder="Enter the description of the embed (Optional)",
            max_length=4000,
        )

        # Return if there is no input fields
        self.add_item(self.content_input)
        self.add_item(self.embed_title_input)
        self.add_item(self.embed_description_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Return if there is no inputted fields
        if (
            not self.content_input.value.strip()
            and not self.embed_title_input.value.strip()
            and not self.embed_description_input.value.strip()
        ):
            await interaction.response.send_message(
                "❌ You must provide at least one of the fields to send a message.",
                ephemeral=True,
            )
            return

        # Defer response
        loader = await pretty_defer(
            interaction=interaction,
            content="Sending your message...",
            ephemeral=True,
        )

        # Create embed if title or description is provided
        embed = None
        if (
            self.embed_title_input.value.strip()
            or self.embed_description_input.value.strip()
        ):
            title = self.embed_title_input.value.strip() or None
            description = self.embed_description_input.value.strip() or None
            embed = discord.Embed(
                title=title,
                description=description,
                color=MONIKA_EMBED_COLOR,
            )

        # Prepare content with optional role mention
        input_content = self.content_input.value.strip() or None
        content = None
        if input_content and self.ping_role:
            content = f"{self.ping_role.mention} {input_content}"
        elif input_content:
            content = input_content
        elif self.ping_role:
            content = self.ping_role.mention

        # Send the message to the specified channel
        try:
            await self.channel.send(content=content, embed=embed)
            await loader.success(
                content=f"Message successfully sent to {self.channel.mention}.",
            )
            pretty_log(
                tag="success",
                message=f"📤 Staff member {self.user} sent a message to {self.channel.name} ({self.channel.id})",
            )
        except Exception as e:
            await loader.error(
                content=f"❌ Failed to send message to {self.channel.mention}: {e}",
            )
            pretty_log(
                message=f"❌ Failed to send message to {self.channel.name} ({self.channel.id}): {e}",
                tag="error",
            )


# 🍭──────────────────────────────
#   🎀 Func: Staff Message Send
# 🍭──────────────────────────────
async def message_send_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    ping_role: discord.Role = None,
):

    # Check if the user is a staff member
    staff_member = await is_staff_member(interaction=interaction)
    if not staff_member:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.", ephemeral=True
        )
        return

    # Create and send the modal
    try:
        modal = Staff_Message_Send_Modal(
            bot=bot,
            user=interaction.user,
            channel=channel,
            ping_role=ping_role,
        )
        await interaction.response.send_modal(modal)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to open the message send modal: {e}", ephemeral=True
        )
        pretty_log(
            message=f"❌ Failed to open message send modal for {interaction.user} ({interaction.user.id}): {e}",
            tag="error",
        )
