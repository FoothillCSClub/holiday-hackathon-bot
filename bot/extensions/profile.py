from os import environ
from pathlib import Path
from typing import List, Tuple

from asyncpg import Record
from discord import File, Member, User
from discord.ext.commands import Cog, Context, command
from PIL import Image, ImageDraw, ImageFont

from bot.bot import HolidayBot

BOLD_LARGE = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 32)
BOLD = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 28)
REGULAR = ImageFont.truetype("assets/fonts/Nunito/Nunito-Regular.ttf", 20)


class Profile(Cog):
    """Extension for profile."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot
        self.outdir = environ.get("BOT_OUTPUT_DIR") or "output"

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    @command()
    async def profile(self, ctx: Context, user: User = None) -> None:
        """View your profile."""
        user = user or ctx.author
        host_guild = self.bot.get_host_guild()
        member = host_guild.get_member(user.id)

        if not member:
            await ctx.send('User not found!')
            return

        user_data, codes = await self.get_member_data(member)

        if not user_data:
            await ctx.send(f'{user.mention} is not registered for the hackathon!')
            return

        filename = self.render_profile_image(member, user_data, codes)

        await ctx.send('**Your hacker profile**', file=File(filename))

    async def get_member_data(self, member: Member) -> Tuple[Record, List[Record]]:
        """Get activity data for a user."""
        async with self.bot.pg_pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT points
                FROM Users
                WHERE user_id = $1
                """, member.id
            )
            # NOTE: For now, we don't fetch the codes
            # because 'recent activity' list is not currently shown
            # codes = await conn.fetch(
            #     """
            #     SELECT Codes.title
            #     FROM Users
            #     JOIN Codes
            #     ON Codes.code = ANY (Users.special_codes)
            #     WHERE user_id = $1
            #     """, member.id
            # )

        # return user, codes
        return user, None

    def render_profile_image(self, member: Member, user: Record, codes: List[Record]) -> str:
        """Renders the profile image."""
        outfile = f"{self.outdir}/profile_{member.name}.png"

        image = Image.open("assets/img/profile_card_bg.png")
        draw = ImageDraw.Draw(image)

        width, height = image.size
        has_display_name = member.name != member.display_name

        # Display name
        draw.text(
            (width / 2, 70 if has_display_name else 80),
            member.display_name,
            font=BOLD_LARGE,
            fill=(20, 20, 20),
            anchor='ma'
        )

        # Username, if different from display name
        if has_display_name:
            draw.text(
                (width / 2, 120),
                '@' + member.name,
                font=REGULAR,
                fill=(50, 50, 50),
                anchor='ma'
            )

        # Points
        draw.text(
            (width / 2, 170 if has_display_name else 150),
            f"{user['points'] or 'No'} points{' yet' if not user['points'] else ''}",
            font=BOLD,
            fill=(20, 20, 20),
            anchor='ma'
        )

        del draw

        image.save(outfile)

        del image

        return outfile


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Profile cog."""
    bot.add_cog(Profile(bot))
