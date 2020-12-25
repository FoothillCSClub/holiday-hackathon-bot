from typing import Optional

from discord import Activity, ActivityType
from discord.ext.commands import Cog, Context, command, errors
from loguru import logger

from bot.bot import HolidayBot


class Admin(Cog):
    """Admin utilities cog."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        """Changes presence when the bot is ready to be used."""
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.playing, name=self.bot.get_data().PRESENCE_TEXT)
        )

    def cog_check(self, ctx: Context) -> bool:
        """Checks if the user is a developer before letting them use the commands in this cog."""
        return ctx.author.id in self.bot.get_data().DEVS

    @command(aliases=("r",))
    async def reload(self, ctx: Context, ext_name: Optional[str]) -> None:
        """Reloads cog(s)."""
        for extension in set([f"bot.extensions.{ext_name}"] if ext_name else self.bot.get_extensions()):
            try:
                self.bot.reload_extension(extension)
                logger.info(f"Reloaded {extension}.")

            except errors.ExtensionNotLoaded:
                self.bot.load_extension(extension)
                logger.info(f"Loaded {extension}.")

        await ctx.send(
            f"Extension '{ext_name}' was reloaded." if ext_name else "All extensions were reloaded."
        )


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Admin cog."""
    bot.add_cog(Admin(bot))
