from aiogram import Bot, Dispatcher
from .database.db import DownloaderDB
from .handlers import router

async def run_bot(bot_token: str, db_path: str):
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    db = DownloaderDB(db_path)
    await db.init()
    
    dp['db'] = db
    dp.include_router(router)
    
    await dp.start_polling(bot)
