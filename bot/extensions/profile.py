from os import environ
from pathlib import Path
from typing import List, Optional, Tuple
from random import randint

from asyncpg import Record
from discord import File, Member, User
from discord.ext.commands import Cog, Context, command
from PIL import Image, ImageDraw, ImageFont

from bot.bot import HolidayBot
from bot.utils import get_max_str

BOLD_LARGEST = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 28)
BOLD_LARGE = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 26)
BOLD = ImageFont.truetype("assets/fonts/Nunito/Nunito-Bold.ttf", 24)
REGULAR = ImageFont.truetype("assets/fonts/Nunito/Nunito-Regular.ttf", 18)


class Profile(Cog):
    """Extension for profile."""

    def __init__(self, bot: HolidayBot) -> None:
        self.bot = bot
        self.outdir = environ.get("BOT_OUTPUT_DIR") or "output"

        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    @command()
    async def profile(self, ctx: Context, user: Optional[User], *, flags: str = "") -> None:
        """View your profile."""
        flags = flags.split(" ")
        user = user or ctx.author
        host_guild = self.bot.get_host_guild()
        member = host_guild.get_member(user.id)

        if not member:
            await ctx.send("User not found!")
            return

        user_data, codes = await self.get_member_data(member)

        if not user_data:
            await ctx.send(f"{user.mention} is not registered for the hackathon!")
            return

        filename = self.render_profile_image(
            member,
            user_data,
            codes,
            flags=flags,
        )

        await ctx.send(
            f"**{'Your hacker' if user == ctx.author else 'Hacker'} profile**", file=File(filename)
        )

    async def get_member_data(self, member: Member) -> Tuple[Record, List[Record]]:
        """Get activity data for a user."""
        async with self.bot.pg_pool.acquire() as conn:
            # TODO: optimize this query or find an alterative method to calculate rank
            user = await conn.fetchrow(
                """
                SELECT
                    points,
                    (
                        SELECT COUNT(user_id)
                        FROM users as inner_users
                        WHERE (inner_users.points > users.points)
                           OR (inner_users.points = users.points AND inner_users.user_id > users.user_id)
                    ) + 1 as rank
                FROM Users
                WHERE user_id = $1
                """,
                member.id,
            )
            # NOTE: Fetching codes is currently disabled
            # because the 'recent activity' list is not shown
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

    def render_profile_image(
        self, member: Member, user: Record, codes: List[Record], flags: List[str]
    ) -> str:
        """Renders the profile image."""
        animated = "static" not in flags
        center = "left" not in flags

        outfile = f"{self.outdir}/profile_{member.name}.{'gif' if animated else 'png'}"

        image = Image.open("assets/img/profile_card_bg.png")
        draw = ImageDraw.Draw(image)
        width, height = image.size

        if center:
            has_display_name = member.name != member.display_name

            # Display name
            draw.text(
                (width / 2, 70 if has_display_name else 80),
                member.display_name,
                font=BOLD_LARGEST,
                fill=(20, 20, 20),
                anchor="ma",
            )

            # Username, if different from display name
            if has_display_name:
                draw.text((width / 2, 120), f"@{member.name}", font=REGULAR, fill=(50, 50, 50), anchor="ma")

            # Points & rank
            draw.text(
                (width / 2, 170 if has_display_name else 150),
                f"{user['points'] or 'No'} points{' yet' if not user['points'] else ''} · #{user['rank']}",
                font=BOLD,
                fill=(20, 20, 20),
                anchor="ma",
            )

        else:
            # Display name
            display_name, _ = get_max_str(BOLD_LARGE, member.display_name, width - 20 - 60)
            draw.text((20, 110), display_name, font=BOLD_LARGE, fill=(20, 20, 20), anchor="ls")
            # Rank
            draw.text((width - 20, 110), f"#{user['rank']}", font=BOLD, fill=(50, 50, 50), anchor="rs")

            # Points
            points_str = f"{user['points'] or 'No'} points"
            points_str_len = REGULAR.getlength(points_str)
            draw.text(
                (width - 20, 140),
                points_str,
                font=REGULAR,
                fill=(20, 20, 20),
                anchor="ra",
            )

            # Username
            username_str, _ = get_max_str(REGULAR, f"@{member.name}", width - 20 * 2 - points_str_len - 4)
            draw.text((20, 140), username_str, font=REGULAR, fill=(50, 50, 50))

        del draw

        if animated:
            points = []
            scatter_amount = 20
            min_radius = 6
            max_radius = 10

            # Create initial points for snow
            for i in range(0, width, int(width / 4)):
                for j in range(0, height, int(height / 4)):
                    points.append(
                        (
                            i + randint(-1 * scatter_amount, scatter_amount),
                            j + randint(-1 * scatter_amount * 2, scatter_amount * 2),
                            randint(min_radius, max_radius),
                            randint(80, 130),
                        )
                    )

            frames = []

            # Create snow animation frames
            for i in range(10):
                overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)

                # Draw points for snow
                for x, y, radius, opacity in points:
                    offset_x = randint(-10, 10)
                    offset_y = i * 13
                    offset_y = randint(offset_y - 5, offset_y + 5)

                    draw.ellipse(
                        (
                            ((x + offset_x) % width - radius, (y + offset_y) % height - radius),
                            ((x + offset_x) % width + radius, (y + offset_y) % height + radius),
                        ),
                        fill=(255, 255, 255, opacity),
                    )

                del draw

                frames.append(Image.alpha_composite(image, overlay))

            frames[0].save(
                outfile,
                save_all=True,
                append_images=frames[1:],
                optimize=False,
                duration=300,
                loop=0,
            )
        else:
            image.save(outfile)

        return outfile


def setup(bot: HolidayBot) -> None:
    """The necessary function for loading the Profile cog."""
    bot.add_cog(Profile(bot))
