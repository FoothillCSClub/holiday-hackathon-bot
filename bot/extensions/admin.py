"""
Extension for Admin Utilities
"""

import os
import sys
import time
import traceback

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.bot.before_invoke(self.before_invoke)

    def get_data(self):
        return self.bot.get_cog('Data')

    def cog_check(self, ctx):
        return ctx.author.id in self.get_data().DEVS

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[bot] We have logged in as {self.bot.user}')
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="https://holiday.foothillcs.club"
            )
        )

    # async def before_invoke(self, ctx):
    #     print(f'[command] "{ctx.author}" invoked "{ctx.command.name}" with "{ctx.message.content}"')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # TODO: properly handle the full range of errors
        await ctx.send('Well, we hit an error.')
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(aliases=['r'])
    async def reload(self, ctx, ext_name: str = ''):
        if not ext_name:
            await ctx.send('No extension name specified')
            return

        try:
            self.bot.reload_extension(f'bot.extensions.{ext_name}')
            await ctx.send('Reloaded!')
        except commands.errors.ExtensionNotLoaded:
            await ctx.send('Extension not loaded')


def setup(bot):
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    bot.add_cog(Admin(bot))
