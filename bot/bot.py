import asyncio
from os import environ, listdir
from pathlib import Path
from typing import Callable, List

import aiohttp
import discord
from asyncpg import create_pool
from discord import Guild, Role
from discord.ext.commands import Bot, Cog, Context
from loguru import logger


class HolidayBot(Bot):
    """Setting up all the important things."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.loop = asyncio.get_event_loop()
        self.http_session = aiohttp.ClientSession()
        self.pg_pool = self.loop.run_until_complete(
            create_pool(
                host="postgres",
                database=environ["POSTGRES_DB"],
                user=environ["POSTGRES_USER"],
                password=environ["POSTGRES_PASSWORD"],
            )
        )

    @staticmethod
    async def on_ready() -> None:
        """Updates the console when the bot is ready to use."""
        logger.info("Awaiting...")

    async def logout(self) -> None:
        """Subclassing the logout command to ensure connection(s) are closed properly."""
        await asyncio.wait_for(self.http_session.close(), 30.0, loop=self.loop)

        logger.info("Finished up closing task(s).")

        return await super().logout()

    @staticmethod
    def get_extensions() -> List[str]:
        """Gets the extensions from the extension folder."""
        exts = [
            f"bot.extensions.{ext[:-3]}"
            for ext in [x for x in listdir(Path("bot/extensions")) if x.endswith(".py")]
        ]

        return exts

    def get_data(self) -> Cog:
        """Get the data cog."""
        return self.get_cog("Data")

    def is_mod(self) -> Callable:
        """Create a mod-checking discord command check."""

        async def predicate(ctx: Context) -> bool:
            """Check if the user is a mod in the event host guild."""
            host_guild = self.get_host_guild()
            role = self.get_mod_role()
            user = host_guild.get_member(ctx.author.id)

            return True if user and role in user.roles else False

        return predicate

    def get_host_guild(self) -> Guild:
        """Get the event host guild."""
        return self.get_guild(self.get_data().HOST_GUILD)

    def get_mod_role(self) -> Role:
        """Get all hackers."""
        return discord.utils.get(self.get_host_guild().roles, name=self.get_data().MOD_ROLE_NAME)

    def get_hacker_role(self) -> Role:
        """Get all hackers."""
        return discord.utils.get(self.get_host_guild().roles, name=self.get_data().HACKER_ROLE_NAME)
