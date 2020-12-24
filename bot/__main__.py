import time
from os import environ, getenv

from discord import Intents
from loguru import logger

from bot.bot import HolidayBot

environ["TZ"] = "America/Los_Angeles"
time.tzset()

intents = Intents.default()
intents.members = True
prefix = getenv("BOT_PREFIX", default="hack ")

bot = HolidayBot(
    # NOTE: this assumes the prefix is a word
    command_prefix=(prefix[0].lower() + prefix[1:], prefix[0].upper() + prefix[1:]),
    case_insensitive=True,
    intents=intents,
)

for extension in bot.get_extensions():
    bot.load_extension(extension)
    logger.info(f'Loaded extension "{extension}"')

bot.run(environ.get("BOT_TOKEN"), bot=True, reconnect=True)
