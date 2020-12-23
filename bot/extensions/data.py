"""
Cog for sharing data across bot

Usage: self.bot.get_cog('Data')
"""

from os import getenv

from discord.ext import commands


class Data(commands.Cog):
    # TODO: graceful exception handling?
    DEVS = [int(elem.strip()) for elem in getenv('BOT_DEVS').split(',')]
    HOST_GUILD = int(getenv('BOT_HOST_GUILD'))
    WEBSITE_URL = 'https://holiday.foothillcs.club'
    WEBSITE_SCHEDULE_URL = 'https://holiday.foothillcs.club#schedule'
    API_SCHEDULE_URL = 'https://holiday.foothillcs.club/api/schedule.json'


def setup(bot):
    bot.add_cog(Data())
