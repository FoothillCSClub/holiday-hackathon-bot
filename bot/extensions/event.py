from datetime import datetime

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, Context, command

from bot.bot import HolidayBot


class Event(Cog):
    """Extension for Events & Schedule."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot
        self.event_data = None
        self.update_time = None
        self.fetch_schedule.start()

    def cog_unload(self) -> None:
        """Cancels the schedule updater."""
        self.fetch_schedule.cancel()

    @command()
    async def schedule(self, ctx: Context) -> None:
        """Check the hackathon event schedule."""
        if not self.event_data:
            await ctx.send("I'm still fetching the event data. Try again in a few seconds!")
            return

        formatted_time = self.update_time.strftime("Updated at %b %d, %I:%M %p PST")
        embed = (
            discord.Embed(
                title="Hackathon Event Schedule",
                description=(
                    f"- **[See more at our website]({self.bot.get_data().WEBSITE_SCHEDULE_URL})**\n"
                    f"- **[Add the Google Calendar]({self.bot.get_data().GCAL_LINK})**"
                ),
                color=self.bot.get_data().HACKATHON_BLUE,
            )
            .set_author(name=self.bot.get_host_guild().name, icon_url=self.bot.get_host_guild().icon_url)
            .set_footer(text=f"{formatted_time} | More at {self.bot.get_data().WEBSITE_URL}")
        )

        for day_info in self.event_data["schedule"]:
            events_text = ""

            for event in day_info["events"]:
                # TODO: add better fields
                cleaned_time = event["time"].replace("&nbsp;", "").strip()
                events_text += f'` {cleaned_time.ljust(14)} ` {event["title"]}\n'

            embed.add_field(name=day_info["day"], value=events_text, inline=False)

        await ctx.send(embed=embed)

    @tasks.loop(seconds=60.0)
    async def fetch_schedule(self) -> None:
        """Fetches the schedule from the hackathon website."""
        async with self.bot.http_session.get(self.bot.get_data().API_SCHEDULE_URL) as response:
            if response.status == 200:
                self.update_time = datetime.now()
                self.event_data = await response.json()
            else:
                # TODO: better error handling
                raise RuntimeError


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Event cog."""
    bot.add_cog(Event(bot))
