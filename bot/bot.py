import asyncio
from os import listdir
from pathlib import Path
from typing import List

import aiohttp
from discord import Activity, ActivityType
from discord.ext.commands import Bot
from loguru import logger

PRESENCE_URL = "https://holiday.foothillcs.club"


class HolidayBot(Bot):
    """Setting up all the important things."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.loop = asyncio.get_event_loop()
        self.http_session = aiohttp.ClientSession()

    async def on_ready(self) -> None:
        """Updates the console when the bot is ready to use."""
        await self.change_presence(activity=Activity(type=ActivityType.playing, name=PRESENCE_URL))

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
