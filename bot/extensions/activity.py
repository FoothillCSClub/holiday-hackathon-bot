from dataclasses import dataclass
from datetime import datetime
from os import environ
from pathlib import Path
from random import randint
from typing import List
from csv import reader

import discord
from asyncpg import Record
from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import Cog, Context, Greedy, check, command
from discord.ext.tasks import loop

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

        # Decorate mod methods without a decorator
        self.registerall = check(self.bot.is_mod())(self.registerall)
        self.give = check(self.bot.is_mod())(self.give)
        self.take = check(self.bot.is_mod())(self.take)
        self.codes = check(self.bot.is_mod())(self.codes)

        self.populate_codes.start()

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    def cog_unload(self) -> None:
        """On cog unload, stop tasks as necessary."""
        self.populate_codes.stop()

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
    async def give(
        self, ctx: Context, points: int, users: Greedy[discord.User], *, remaining: str = ""
    ) -> None:
        """Give or take a certain number of points from a user."""
        if remaining:
            await ctx.send(f"[warning] the following was ignored: '{remaining}'")

        if len(users) == 0:
            await ctx.send("At least one user has to be specified!")
            return

        users_updated = []
        users_not_registered = []

        async with self.bot.pg_pool.acquire() as conn:
            async with conn.transaction():
                for user in users:
                    db_user = await conn.fetchrow("SELECT * FROM Users WHERE user_id = $1", user.id)

                    if not db_user:
                        users_not_registered.append(user.mention)
                        continue

                    await conn.execute(
                        "UPDATE Users SET points=$2 WHERE id=$1", db_user["id"], db_user["points"] + points
                    )
                    users_updated.append(user.mention)

        text = ""

        if len(users_updated):
            text += f"{' '.join(users_updated)} - got {points} points\n"

        if len(users_not_registered):
            text += f"{' '.join(users_not_registered)} - not registered for the hackathon!\n"

        await ctx.send(text)

    @command()
    async def take(
        self, ctx: Context, points: int, users: Greedy[discord.User], *, remaining: str = ""
    ) -> None:
        """Give or take a certain number of points from a user."""
        await self.give(ctx, points * -1, users, remaining=remaining)

    @command()
    async def registerall(self, ctx: Context, fill_random: bool = False) -> None:
        """Reset and register all @hacker for the activity competition."""
        users = await self.populate_db(fill_random)

        text = "Registered & reset: " + " ".join([f"<@{user['user_id']}>" for user in users])
        text += "\nPopulated random scores" if fill_random else "\nSet all scores to 0\n"
        embed = discord.Embed(title="Hackers", description=text)

        await ctx.send(embed=embed)

    @command()
    async def codes(self, ctx: Context) -> None:
        """List all codes."""
        async with self.bot.pg_pool.acquire() as conn:
            async with conn.transaction():
                codes = await conn.fetch("SELECT code, title, points FROM Codes")

        embed = discord.Embed(
            title="Activity Codes",
            description="\n".join([f"`{code}` {title} - {points}" for code, title, points in codes]),
            color=discord.Color.from_rgb(161, 219, 236),
        )

        await ctx.author.send(embed=embed)

    @loop(count=1)
    async def populate_codes(self) -> None:
        """Populate special codes."""
        async with self.bot.pg_pool.acquire() as conn:
            with open(self.bot.get_data().ACTIVITY_CODES_CSV, newline="") as csvfile:
                data = [
                    (item[0], item[1], int(item[2])) for item in reader(csvfile, delimiter=",", quotechar="|")
                ]

            async with conn.transaction():
                await conn.execute("DELETE FROM Codes")
                await conn.executemany("INSERT INTO Codes (code, title, points) VALUES ($1, $2, $3)", data)

    async def populate_db(self, fill_random: bool) -> List[Record]:
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
                        randint(0, 200) if fill_random else 0,
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
