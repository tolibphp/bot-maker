import aiosqlite
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
