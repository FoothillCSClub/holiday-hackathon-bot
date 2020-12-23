from os import getenv

from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.members = True

prefixes = ('hack ', 'Hack ')
extensions = ['admin', 'activity', 'data', 'event']


def start_bot():
    bot = commands.Bot(command_prefix=prefixes, intents=intents)

    for name in extensions:
        bot.load_extension(f'bot.extensions.{name}')

    bot.run(getenv('BOT_TOKEN'))


if __name__ == '__main__':
    start_bot()
