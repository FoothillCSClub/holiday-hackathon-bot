from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot.bot import HolidayBot


class Help(Cog):
    """Helping out the user with commands."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot

    @command(name="help")
    async def help_command(self, ctx: Context) -> None:
        """Getting help for a user."""
        embed = Embed(title="__Holiday Hackathon Bot__")
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        moderator = await self.bot.is_mod()(ctx)

        for cmd in self.bot.walk_commands():
            if ((cmd.hidden or not cmd.enabled) and not moderator) or cmd.qualified_name == "help":
                continue

            embed.add_field(
                name=f"**{ctx.prefix}{cmd.qualified_name}**", value=f"{cmd.short_doc}", inline=False
            )

        await ctx.send(embed=embed)


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Help cog."""
    bot.add_cog(Help(bot))
