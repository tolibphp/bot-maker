import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from templates.base_template import BaseTemplate
from templates.stars_bot.database import StarsDB
from templates.stars_bot.handlers.user import create_user_router
from templates.stars_bot.handlers.admin import create_admin_router

logger = logging.getLogger(__name__)

class StarsBot(BaseTemplate):
    def __init__(self, bot_token: str, admin_id: int, db_path: str, bot_id: int):
        super().__init__(bot_token, admin_id, db_path, bot_id)
        self.stars_db = StarsDB(db_path)
        self._polling_task: asyncio.Task = None

    async def setup(self):
        await self.stars_db.init_db()
        
        self.bot = Bot(
            token=self.bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        
        admin_router = create_admin_router(self.stars_db, self.admin_id)
        user_router = create_user_router(self.stars_db, self.admin_id)
        
        self.dp.include_router(admin_router)
        self.dp.include_router(user_router)

    async def start(self):
        await self.setup()
        
        try:
            await self.bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        
        self._polling_task = asyncio.create_task(
            self._run_polling(),
            name=f"stars_bot_{self.bot_id}"
        )
        logger.info(f"StarsBot #{self.bot_id} started polling")

    async def _run_polling(self):
        try:
            await self.dp.start_polling(self.bot)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"StarsBot #{self.bot_id} polling error: {e}")

    async def stop(self):
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        
        if hasattr(self, 'dp') and self.dp:
            await self.dp.stop_polling()
        
        if hasattr(self, 'bot') and self.bot:
            await self.bot.session.close()
        
        logger.info(f"StarsBot #{self.bot_id} stopped")
