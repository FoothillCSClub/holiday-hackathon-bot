import os

from discord.ext.commands import Cog

from bot.bot import HolidayBot


class Data(Cog):
    # TODO: graceful exception handling?
    DEVS = [int(elem.strip()) for elem in os.environ.get("BOT_DEVS").split(",")]
    HOST_GUILD = int(os.environ.get("BOT_HOST_GUILD"))
    PRESENCE_TEXT = "https://holiday.foothillcs.club"
    WEBSITE_URL = "https://holiday.foothillcs.club"
    WEBSITE_SCHEDULE_URL = "https://holiday.foothillcs.club#schedule"
    API_SCHEDULE_URL = "https://holiday.foothillcs.club/api/schedule.json"


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Data cog."""
    bot.add_cog(Data(bot))
