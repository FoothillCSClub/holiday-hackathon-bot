'''
Extension for Events & Schedule
'''

from datetime import datetime

import aiohttp
import discord
from discord.ext import tasks, commands


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_data = None
        self.update_time = None
        self.fetch_schedule.start()

    def cog_unload(self):
        self.fetch_schedule.cancel()

    def get_data(self):
        return self.bot.get_cog('Data')

    @commands.command()
    async def schedule(self, ctx):
        if not self.event_data:
            await ctx.send("I'm still fetching the event data. Try again in a few seconds!")
            return

        embed = discord.Embed(
            title='Event Schedule', color=discord.Color.from_rgb(161, 219, 236),
            url=self.get_data().WEBSITE_SCHEDULE_URL
        )

        formatted_time = self.update_time.strftime('Updated at %b %d, %I:%M %p PST')
        embed.set_footer(
            text=f'{formatted_time} | More at {self.get_data().WEBSITE_URL}'
        )

        for day_info in self.event_data['schedule']:
            events_text = ''

            for event in day_info['events']:
                # TODO: add better fields
                cleaned_time = event['time'].replace('&nbsp;', '').strip()
                events_text += f'` {cleaned_time.ljust(14)} ` {event["title"]}\n'

            embed.add_field(name=day_info['day'], value=events_text, inline=False)

        await ctx.send(embed=embed)

    @tasks.loop(seconds=60.0)
    async def fetch_schedule(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.get_data().API_SCHEDULE_URL) as response:
                if response.status == 200:
                    self.update_time = datetime.now()
                    self.event_data = await response.json()
                else:
                    # TODO: better error handling
                    raise RuntimeError


def setup(bot):
    bot.add_cog(Event(bot))
