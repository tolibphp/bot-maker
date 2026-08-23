import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from templates.base_template import BaseTemplate
from templates.downloader_bot.database.db import DownloaderDB
from templates.downloader_bot.handlers.main import router

logger = logging.getLogger(__name__)

class DownloaderBot(BaseTemplate):
    def __init__(self, bot_token: str, admin_id: int, db_path: str, bot_id: int):
        super().__init__(bot_token, admin_id, db_path, bot_id)
        self.down_db = DownloaderDB(db_path)
        self._polling_task: asyncio.Task = None

    async def setup(self):
        """Initialize database and setup dispatcher."""
        await self.down_db.init()
        
        self.bot = Bot(
            token=self.bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Inject dependencies
        self.dp['db'] = self.down_db
        
        # Register routers
        self.dp.include_router(router)

    async def start(self):
        """Start bot polling."""
        await self.setup()
        
        try:
            await self.bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        
        self._polling_task = asyncio.create_task(
            self._run_polling(),
            name=f"downloader_bot_{self.bot_id}"
        )
        logger.info(f"DownloaderBot #{self.bot_id} started polling")

    async def _run_polling(self):
        """Run polling with error handling."""
        try:
            await self.dp.start_polling(self.bot)
        except asyncio.CancelledError:
            logger.info(f"DownloaderBot #{self.bot_id} polling cancelled")
        except Exception as e:
            logger.error(f"DownloaderBot #{self.bot_id} polling error: {e}")

    async def stop(self):
        """Stop bot polling."""
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        
        if self.dp:
            await self.dp.stop_polling()
        
        if self.bot:
            await self.bot.session.close()
        
        logger.info(f"DownloaderBot #{self.bot_id} stopped")
