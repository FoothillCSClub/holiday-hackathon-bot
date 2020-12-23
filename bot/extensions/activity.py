"""
Extension for Activity Challenge 
"""

from os import getenv
from typing import List
from datetime import datetime
from random import randint
from dataclasses import dataclass
from pathlib import Path

import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw


class Font:
    regular = ImageFont.truetype('assets/fonts/Nunito/Nunito-Regular.ttf', 24)
    bold = ImageFont.truetype('assets/fonts/Nunito/Nunito-Bold.ttf', 24)
    extrabold = ImageFont.truetype('assets/fonts/Nunito/Nunito-ExtraBold.ttf', 24)


@dataclass
class RankedMember:
    rank: int
    username: str
    display_name: str
    score: int


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.outdir = getenv('BOT_OUTPUT_DIR') or 'output'

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    def get_data(self):
        return self.bot.get_cog('Data')

    @commands.command()
    async def top(self, ctx, page: int = 1):
        now = datetime.now()
        members = self.get_top_members(page)
        filename = self.render_top_image(page, members)

        embed = discord.Embed(
            title='Activity Challenge',
            color=discord.Color.from_rgb(161, 219, 236)
        )
        embed.set_footer(text=now.strftime('Updated at %b %d, %I:%M %p PST'))
        embed.set_image(url=f'attachment://{filename.split("/")[-1]}')

        await ctx.send(embed=embed, file=discord.File(filename))

    def get_top_members(self, page: int) -> List[RankedMember]:
        # TODO: cleanup method
        guild = self.bot.get_guild(self.get_data().HOST_GUILD)
        role = next((role for role in guild.roles if role.name == 'hacker'))
        hackers = [(hacker, randint(0, 200)) for hacker in role.members]

        return [
            RankedMember(
                rank=((page-1) * 10) + i + 1,
                username=hacker[0].name,
                display_name=hacker[0].display_name,
                score=hacker[1],
            ) for i, hacker in enumerate(
                sorted(
                    hackers[(page-1)*10:page*10],
                    key=lambda data: data[1],
                    reverse=True
                )
            )
        ]

    def render_top_image(self, page: int, members: List[RankedMember]) -> str:
        height = 600
        width = 580
        outfile = f'{self.outdir}/activity_top_{page}.png'

        image = Image.new(mode='RGBA', size=(height, width), color=(0, 0, 0, 0))
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
                fill=(73, 76, 81)
            )

            content_y = y + content_offset_y

            # Show rank number: '#' then '24'
            draw.text(
                (content_padding, content_y),
                '#',
                font=Font.bold,
                fill=(200, 200, 200),
            )
            draw.text(
                (content_padding + 18, content_y),
                str(person.rank),
                font=Font.bold,
                fill=(200, 200, 200),
            )

            # Show display name (or username, if default)
            name_x = content_padding + 58
            draw.text(
                (name_x, content_y),
                person.display_name,
                font=Font.extrabold,
            )

            # Show username, if different from display name
            if person.username != person.display_name:
                length = draw.textlength(
                    person.display_name,
                    font=Font.extrabold,
                )
                draw.text(
                    (name_x + length + 8, content_y),
                    f'@{person.username}',
                    font=Font.regular,
                )

            # Show score, right aligned
            draw.text(
                (width - content_padding, content_y),
                str(person.score),
                font=Font.bold,
                fill=(118, 181, 214),
                anchor='ra',
            )

            y += step_size

        del draw

        image.save(outfile)

        del image

        return outfile


def setup(bot):
    bot.add_cog(Activity(bot))
