import time
from os import environ

from discord import Intents
from loguru import logger

from bot.bot import HolidayBot

environ["TZ"] = "America/Los_Angeles"
time.tzset()

intents = Intents.default()
intents.members = True

bot = HolidayBot(
    command_prefix="hack ",
    case_insensitive=False,
    intents=intents,
)

for extension in bot.get_extensions():
    bot.load_extension(extension)
    logger.info(f'Loaded extension "{extension}"')

bot.run(environ.get("BOT_TOKEN"), bot=True, reconnect=True)
