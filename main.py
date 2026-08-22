import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import MASTER_TOKEN, ADMIN_ID
from database.db import init_master_db
from master_bot.handlers import get_master_router
from bot_manager import manager
from scheduler import run_scheduler

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 50)
    logger.info("🤖 Bot Maker starting...")
    logger.info("=" * 50)

    # 1. Initialize master database
    await init_master_db()
    logger.info("✅ Master database initialized")

    # 2. Create master bot
    bot = Bot(
        token=MASTER_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Register master bot handlers
    master_router = get_master_router()
    dp.include_router(master_router)
    logger.info("✅ Master bot handlers registered")

    # 4. Load all previously active bots
    await manager.load_all_bots()
    logger.info(f"✅ Loaded {manager.get_running_count()} child bots")

    # 5. Start daily payment scheduler
    scheduler_task = asyncio.create_task(run_scheduler())
    logger.info("✅ Payment scheduler started")

    # 6. Notify admin
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🤖 <b>Bot Maker ishga tushdi!</b>\n\n"
            f"✅ Aktiv botlar: {manager.get_running_count()} ta\n"
            f"⏰ Scheduler: ishlayapti"
        )
    except Exception:
        pass

    # 7. Start master bot polling
    logger.info("🚀 Master bot polling started")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        # Cleanup
        logger.info("Shutting down...")
        scheduler_task.cancel()
        await manager.stop_all_bots()
        await bot.session.close()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
