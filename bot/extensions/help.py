from textwrap import dedent

from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot.bot import HolidayBot


class Help(Cog):
    """Helping out the user with commands."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot

    @command(name="help", aliases=("modhelp",))
    async def help_command(self, ctx: Context) -> None:
        """Getting help for a user."""
        moderator = await self.bot.is_mod()(ctx)
        embed = (
            Embed(
                title="Holiday Hackathon Bot",
                color=self.bot.get_data().HACKATHON_BLUE,
            )
            .set_author(name=self.bot.get_host_guild().name, icon_url=self.bot.get_host_guild().icon_url)
            .set_thumbnail(url=self.bot.user.avatar_url)
            .set_footer(text="Have any questions or feedback? Reach out to the @mods!")
        )

        if moderator and ctx.invoked_with == "modhelp":
            for cmd in self.bot.walk_commands():
                embed.add_field(
                    name=f"**{ctx.prefix}{cmd.qualified_name}**", value=f"{cmd.short_doc}", inline=False
                )
        else:
            embed.description = self.get_help_text(ctx, moderator)

        await ctx.send(embed=embed)

    def get_help_text(self, ctx: Context, moderator: bool) -> None:
        """Get clean help text."""
        data = self.bot.get_data()

        usage = (
            f"`{ctx.prefix}modhelp` for all commands"
            if moderator
            else f"`{ctx.prefix}help` to see this message"
        )

        return dedent(
            f"""
            A bot to help you out in the [holiday hackathon]({data.WEBSITE_URL})!

            :game_die: **Activity Competition**

            ```
            top       Check the challenge leaderboard
            ``` ```
            redeem    Redeem points for a code [DM ONLY]
            ```
            :pencil: **Utilities**

            ```
            profile   View your profile
            ``` ```
            schedule  Check the hackathon schedule
            ```
            :tada: **Enjoy!**

            Use {usage}.
            {data.ZERO_WIDTH_CHAR}"""
        )


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Help cog."""
    bot.add_cog(Help(bot))
