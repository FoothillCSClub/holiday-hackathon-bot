from dataclasses import dataclass
from datetime import datetime
from os import environ
from pathlib import Path
from random import randint
from typing import List

import discord
from asyncpg import Record
from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import Cog, Context, check, command

from bot.bot import HolidayBot

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

        # Decorate .registerall() without a decorator
        self.registerall = check(self.bot.is_mod())(self.registerall)

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    @command()
    async def top(self, ctx: Context, page: int = 1) -> None:
        """View the activity competition leaderboard."""
        now = datetime.now()
        members = await self.get_top_members(page)
        filename = self.render_leaderboard_image(page, members)

        embed = discord.Embed(title="Activity Challenge", color=discord.Color.from_rgb(161, 219, 236))
        embed.set_footer(text=now.strftime("Updated at %b %d, %I:%M %p PST"))
        embed.set_image(url=f'attachment://{filename.split("/")[-1]}')

        await ctx.send(embed=embed, file=discord.File(filename))

    @command()
    async def registerall(self, ctx: Context) -> None:
        """Reset and register all @hacker for the activity competition."""
        users = await self.populate_db()

        text = "Registered & reset: " + " ".join([f"<@{user['user_id']}>" for user in users])
        embed = discord.Embed(title="Hackers", description=text)

        await ctx.send(embed=embed)

    async def populate_db(self) -> List[Record]:
        """Reset & populate the postgres Users table with @hacker members + random scores."""
        guild = self.bot.get_host_guild()
        role = discord.utils.get(guild.roles, name="hacker")

        async with self.bot.pg_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM Users")

                for member in role.members:
                    await conn.execute(
                        "INSERT INTO Users(user_id, points, special_codes) VALUES ($1, $2, $3)",
                        member.id,
                        randint(0, 200),
                        [],
                    )

            async with conn.transaction():
                users = await conn.fetch("SELECT * FROM Users")
                return users

    async def get_top_members(self, page: int) -> List[RankedMember]:
        """Get top 10 members on page X of the leaderboard."""
        guild = self.bot.get_host_guild()

        page_idx = page - 1
        page_offset = page_idx * 10

        async with self.bot.pg_pool.acquire() as conn:
            async with conn.transaction():
                hackers = await conn.fetch(
                    "SELECT * FROM Users ORDER BY points DESC LIMIT 10 OFFSET $1",
                    page_offset,
                )

        # Tuples of (rank, DB user, and Discord Guild Member)
        hacker_data = [
            (page_offset + i + 1, hacker, guild.get_member(hacker["user_id"]))
            for i, hacker in enumerate(hackers)
        ]

        return [
            RankedMember(
                rank=rank,
                username=member.name,
                display_name=member.display_name,
                score=db_user["points"],
            )
            for rank, db_user, member in hacker_data
        ]

    def render_leaderboard_image(self, page: int, members: List[RankedMember]) -> str:
        """Renders the leaderboard image."""
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
