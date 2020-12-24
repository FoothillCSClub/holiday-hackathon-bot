from dataclasses import dataclass
from datetime import datetime
from os import environ
from pathlib import Path
from random import randint
from typing import List

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import Cog, Context, command

from bot.bot import HolidayBot

HOST_GUILD = int(environ.get("BOT_HOST_GUILD"))

REGULAR = ImageFont.truetype("assets/fonts/Nunito/Nunito-Regular.ttf", 24)
BOLD = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 24)
EXTRABOLD = ImageFont.truetype("assets/fonts/Nunito/Nunito-ExtraBold.ttf", 24)


@dataclass
class RankedMember:
    """A dataclass for a player in the hackathon leaderboard."""

    rank: int
    username: str
    display_name: str
    score: int


class Activity(Cog):
    """Extension for Activity Challenge."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot
        self.outdir = environ.get("BOT_OUTPUT_DIR") or "output"

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    @command()
    async def top(self, ctx: Context, page: int = 1) -> None:
        """Renders a leaderboard of all the top points of players."""
        now = datetime.now()
        members = self.get_top_members(page)
        filename = self.render_top_image(page, members)

        embed = discord.Embed(title="Activity Challenge", color=discord.Color.from_rgb(161, 219, 236))
        embed.set_footer(text=now.strftime("Updated at %b %d, %I:%M %p PST"))
        embed.set_image(url=f'attachment://{filename.split("/")[-1]}')

        await ctx.send(embed=embed, file=discord.File(filename))

    def get_top_members(self, page: int) -> List[RankedMember]:
        """Gets the top members from the leaderboard."""
        # TODO: cleanup method
        guild = self.bot.get_guild(HOST_GUILD)
        role = next((role for role in guild.roles if role.name == "hacker"))
        hackers = [(hacker, randint(0, 200)) for hacker in role.members]

        return [
            RankedMember(
                rank=((page - 1) * 10) + i + 1,
                username=hacker[0].name,
                display_name=hacker[0].display_name,
                score=hacker[1],
            )
            for i, hacker in enumerate(
                sorted(
                    hackers[(page - 1) * 10 : page * 10],
                    key=lambda data: data[1],
                    reverse=True,
                )
            )
        ]

    def render_top_image(self, page: int, members: List[RankedMember]) -> str:
        """Renders the top image."""
        height = 600
        width = 580
        outfile = f"{self.outdir}/activity_top_{page}.png"

        image = Image.new(mode="RGBA", size=(height, width), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        step_size = int(image.height / 10)
        box_padding = 6
        box_height = 52
        content_padding = 24
        content_offset_y = 10

        y = 4

        for person in members:
            # Draw bounding rectangle
            draw.rectangle(
                [(box_padding, y), (width - box_padding, y + box_height)],
                fill=(73, 76, 81),
            )

            content_y = y + content_offset_y

            # Show rank number: '#' then '24'
            draw.text(
                (content_padding, content_y),
                "#",
                font=BOLD,
                fill=(200, 200, 200),
            )
            draw.text(
                (content_padding + 18, content_y),
                str(person.rank),
                font=BOLD,
                fill=(200, 200, 200),
            )

            # Show display name (or username, if default)
            name_x = content_padding + 58
            draw.text(
                (name_x, content_y),
                person.display_name,
                font=EXTRABOLD,
            )

            # Show username, if different from display name
            if person.username != person.display_name:
                length = draw.textlength(
                    person.display_name,
                    font=EXTRABOLD,
                )
                draw.text(
                    (name_x + length + 8, content_y),
                    f"@{person.username}",
                    font=REGULAR,
                )

            # Show score, right aligned
            draw.text(
                (width - content_padding, content_y),
                str(person.score),
                font=BOLD,
                fill=(118, 181, 214),
                anchor="ra",
            )

            y += step_size

        del draw

        image.save(outfile)

        del image

        return outfile


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Activity cog."""
    bot.add_cog(Activity(bot))
