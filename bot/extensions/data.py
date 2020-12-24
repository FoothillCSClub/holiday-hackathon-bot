import os

from discord.ext.commands import Cog


class Data(Cog):
    DEVS = [int(elem.strip()) for elem in os.environ.get("BOT_DEVS").split(",")]
    PRESENCE_URL = "https://holiday.foothillcs.club"
    WEBSITE_URL = "https://holiday.foothillcs.club"
    WEBSITE_SCHEDULE_URL = "https://holiday.foothillcs.club#schedule"
    API_SCHEDULE_URL = "https://holiday.foothillcs.club/api/schedule.json"
    HOST_GUILD = int(os.environ.get("BOT_HOST_GUILD"))
