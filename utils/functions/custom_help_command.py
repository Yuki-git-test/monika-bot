import discord
from discord.ext import commands



class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        desc = (
            "- `!bt` - Battle Tower Strats\n"
            "- `!mc` - Mega Chamber Battle Guide\n"
            "- `!wb` - World Boss Strats\n"
            "- `!tr` or `!trainer` - PokéMeow Trainer IDs for EV Training\n"
            "- `!exp` or `!explore` - PokéMeow Explore Secrets Guide\n"
        )
        embed = discord.Embed(
            title="Autoresponder List",
            description=desc,
        )
        ctx = self.context
        await ctx.reply(embed=embed, mention_author=False)
