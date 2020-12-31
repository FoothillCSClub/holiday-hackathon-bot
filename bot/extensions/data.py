import os

from discord import Color
from discord.ext.commands import Cog

from bot.bot import HolidayBot


class Data(Cog):
    # TODO: graceful exception handling?
    DEVS = [int(elem.strip()) for elem in os.environ.get("BOT_DEVS").split(",")]
    HOST_GUILD = int(os.environ.get("BOT_HOST_GUILD"))
    HACKER_ROLE_NAME = os.environ.get("BOT_HACKER_ROLE_NAME")
    MOD_ROLE_NAME = os.environ.get("BOT_MOD_ROLE_NAME")
    ACTIVITY_CODES_CSV = os.environ.get("ACTIVITY_CODES_CSV", "postgres/sample_codes.csv")
    PRESENCE_TEXT = "hack help | https://holiday.foothillcs.club"
    WEBSITE_URL = "https://holiday.foothillcs.club"
    WEBSITE_SCHEDULE_URL = "https://holiday.foothillcs.club#schedule"
    API_SCHEDULE_URL = "https://holiday.foothillcs.club/api/schedule.json"
    GCAL_LINK = "https://calendar.google.com/calendar/embed?src=fp5hg8aq83k3ic6cgumncc9ivs%40group.calendar.google.com&ctz=America%2FLos_Angeles"

    HACKATHON_BLUE = Color.from_rgb(161, 219, 236)
    ZERO_WIDTH_CHAR = "​"


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Data cog."""
    bot.add_cog(Data(bot))
