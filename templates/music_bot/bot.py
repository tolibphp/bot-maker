import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from templates.base_template import BaseTemplate
from templates.music_bot.database import MusicDB
from templates.music_bot.handlers import get_routers

logger = logging.getLogger(__name__)

class MusicBot(BaseTemplate):
    def __init__(self, bot_token: str, admin_id: int, db_path: str, bot_id: int):
        super().__init__(bot_token, admin_id, db_path, bot_id)
        self.music_db = MusicDB(db_path)
        self._polling_task: asyncio.Task = None

    async def setup(self):
        await self.music_db.init_db()
        
        self.bot = Bot(
            token=self.bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        
        routers = get_routers(self.music_db, self.admin_id)
        for r in routers:
            self.dp.include_router(r)

    async def start(self):
        await self.setup()
        
        async def poll():
            try:
                logger.info(f"MusicBot #{self.bot_id} started polling")
                await self.dp.start_polling(self.bot, handle_signals=False)
            except Exception as e:
                logger.error(f"MusicBot #{self.bot_id} error: {e}")
            finally:
                await self.bot.session.close()
                logger.info(f"MusicBot #{self.bot_id} stopped")

        self._polling_task = asyncio.create_task(poll())

    async def stop(self):
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        if hasattr(self, 'bot'):
            await self.bot.session.close()

