import os

from discord import Color
from discord.ext.commands import Cog

from bot.bot import HolidayBot


class Data(Cog):
    # TODO: graceful exception handling?
    DEVS = [int(elem.strip()) for elem in os.environ.get("BOT_DEVS").split(",")]
    HOST_GUILD = int(os.environ.get("BOT_HOST_GUILD"))
    ACTIVITY_CODES_CSV = os.environ.get("ACTIVITY_CODES_CSV", "postgres/sample_codes.csv")
    PRESENCE_TEXT = "hack help | https://holiday.foothillcs.club"
    WEBSITE_URL = "https://holiday.foothillcs.club"
    WEBSITE_SCHEDULE_URL = "https://holiday.foothillcs.club#schedule"
    API_SCHEDULE_URL = "https://holiday.foothillcs.club/api/schedule.json"

    HACKATHON_BLUE = Color.from_rgb(161, 219, 236)
    ZERO_WIDTH_CHAR = "​"


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Data cog."""
    bot.add_cog(Data(bot))
