import sys
import traceback

from discord.ext import commands
from discord.ext.commands import Cog, Context

from bot.bot import HolidayBot


class Warnings(Cog):
    """Warning the user about specific actions taken."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, e: commands.CommandError) -> None:
        """When the command has an error, this event is triggered."""
        if hasattr(ctx.command, "on_error"):
            return

        e = getattr(e, "original", e)

        if isinstance(e, commands.DisabledCommand):
            msg = "Command not currently enabled."

        elif isinstance(e, commands.UserInputError):
            msg = f"Command received bad argument: {e}."

        elif isinstance(e, commands.NotOwner):
            msg = "You do not have enough permissions for this command."

        elif isinstance(e, commands.CommandOnCooldown):
            msg = f"{e}."

        elif isinstance(e, commands.CheckFailure):
            msg = "You do not have enough permissions to run this command."

        elif isinstance(e, commands.MissingPermissions):
            msg = "Bot does not have enough permissions for this command."

        elif isinstance(e, commands.CommandNotFound):
            msg = f"Command not found! Use `{ctx.prefix}help` to list all available commands."

        else:
            msg = f"{type(e).__name__}: {e}"

        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

        await ctx.send(msg)


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Warning cog."""
    bot.add_cog(Warnings(bot))
