import os

base_dir = 'templates/music_bot'
os.makedirs(base_dir, exist_ok=True)
os.makedirs(os.path.join(base_dir, 'handlers'), exist_ok=True)

with open(os.path.join(base_dir, '__init__.py'), 'w') as f:
    pass

with open(os.path.join(base_dir, 'handlers', '__init__.py'), 'w') as f:
    f.write('''from .start import create_start_router
from .admin import create_admin_router
from .search import create_search_router

def get_routers(db, admin_id):
    return [
        create_start_router(db, admin_id),
        create_admin_router(db, admin_id),
        create_search_router(db, admin_id)
    ]
''')

with open(os.path.join(base_dir, 'bot.py'), 'w') as f:
    f.write('''import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .database import MusicDB
from .handlers import get_routers

logger = logging.getLogger(__name__)

async def start_bot(token: str, db_path: str, admin_id: int):
    bot = Bot(token=token)
    db = MusicDB(db_path)
    await db.init_db()
    
    dp = Dispatcher(storage=MemoryStorage())
    routers = get_routers(db, admin_id)
    for router in routers:
        dp.include_router(router)
        
    logger.info(f"Music Bot started polling with admin_id={admin_id}")
    try:
        await dp.start_polling(bot, handle_signals=False)
    finally:
        await bot.session.close()
''')

with open(os.path.join(base_dir, 'database.py'), 'w') as f:
    f.write('''import aiosqlite
import os

class MusicDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def _get_db(self):
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        return db

    async def init_db(self):
        db = await self._get_db()
        try:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    is_banned BOOLEAN DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE NOT NULL,
                    channel_name TEXT
                );
                
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_id TEXT UNIQUE NOT NULL,
                    telegram_file_id TEXT NOT NULL,
                    title TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.commit()
        finally:
            await db.close()

    async def add_user(self, telegram_id: int, username: str, full_name: str):
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                (telegram_id, username, full_name)
            )
            await db.commit()
        finally:
            await db.close()

    async def get_users_count(self) -> int:
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            res = await cursor.fetchone()
            return res[0] if res else 0
        finally:
            await db.close()

    async def get_all_users(self):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM users")
            return await cursor.fetchall()
        finally:
            await db.close()

    async def get_channels(self):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM channels")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def add_channel(self, channel_id: str, channel_name: str = None):
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR IGNORE INTO channels (channel_id, channel_name) VALUES (?, ?)",
                (channel_id, channel_name)
            )
            await db.commit()
        finally:
            await db.close()

    async def delete_channel(self, ch_id: int):
        db = await self._get_db()
        try:
            await db.execute("DELETE FROM channels WHERE id = ?", (ch_id,))
            await db.commit()
        finally:
            await db.close()

    async def get_cached_audio(self, youtube_id: str):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM downloads WHERE youtube_id = ?", (youtube_id,))
            return await cursor.fetchone()
        finally:
            await db.close()

    async def cache_audio(self, youtube_id: str, telegram_file_id: str, title: str):
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR REPLACE INTO downloads (youtube_id, telegram_file_id, title) VALUES (?, ?, ?)",
                (youtube_id, telegram_file_id, title)
            )
            await db.commit()
        finally:
            await db.close()
''')

with open(os.path.join(base_dir, 'states.py'), 'w') as f:
    f.write('''from aiogram.fsm.state import State, StatesGroup

class BroadcastStates(StatesGroup):
    waiting_message = State()

class AddChannelStates(StatesGroup):
    waiting_channel = State()
''')

with open(os.path.join(base_dir, 'keyboards.py'), 'w') as f:
    f.write('''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

MUSIC_EMOJI = '<tg-emoji emoji-id="5933952676151695799">🎧🎵</tg-emoji>'
DOWN_EMOJI = '<tg-emoji emoji-id="5463107823946717464">⬇️</tg-emoji>'

def admin_main_kb():
    buttons = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✅ Majburiy obuna")],
        [KeyboardButton(text="📢 Broadcast")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def cancel_admin_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

def channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"🗑 {ch['channel_name'] or ch['channel_id']}", callback_data=f"delch:{ch['id']}")])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_main_kb():
    buttons = [
        [InlineKeyboardButton(text="🔍 Qidirish", switch_inline_query_current_chat="")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subscription_kb(channels: list):
    buttons = []
    for ch in channels:
        channel_id = ch["channel_id"]
        name = ch["channel_name"] or channel_id
        url = f"https://t.me/{channel_id[1:]}" if channel_id.startswith("@") else f"https://t.me/{channel_id}"
        buttons.append([InlineKeyboardButton(text=f"📢 {name}", url=url)])
    buttons.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
''')
