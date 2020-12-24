from typing import Optional

from discord import Activity, ActivityType
from discord.ext.commands import Cog, Context, command, errors
from loguru import logger

from bot.bot import HolidayBot
from data import Data


class Admin(Cog):
    """Admin utilities cog."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot

    async def on_ready(self) -> None:
        """Changes presence when the bot is ready to be used."""
        await self.bot.change_presence(activity=Activity(type=ActivityType.playing, name=Data.PRESENCE_URL))

    def cog_check(self, ctx: Context) -> bool:
        """Checks if the user is a developer before letting them use the commands in this cog."""
        return ctx.author.id in Data.DEVS

    @command(aliases=("r",))
    async def reload(self, ctx: Context, ext_name: Optional[str]) -> None:
        """Reloads cog(s)."""
        for extension in set(self.bot.get_extensions() or ext_name):
            try:
                self.bot.reload_extension(extension)
                logger.info(f"Reloaded {extension}.")

            except errors.ExtensionNotLoaded:
                self.bot.load_extension(extension)
                logger.info(f"Loaded {extension}.")

        await ctx.send("Extensions are done (re)loading.")


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Admin cog."""
    bot.add_cog(Admin(bot))
