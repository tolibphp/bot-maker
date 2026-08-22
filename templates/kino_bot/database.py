import aiosqlite
import os


class KinoDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def _get_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        return db

    async def init_db(self):
        db = await self._get_db()
        try:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    is_banned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    file_id TEXT NOT NULL,
                    caption TEXT,
                    views INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE NOT NULL,
                    channel_name TEXT
                );
            """)
            await db.commit()
        finally:
            await db.close()

    # ---- Users ----
    async def add_user(self, telegram_id: int, username: str = None, full_name: str = None):
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                (telegram_id, username, full_name)
            )
            await db.commit()
        finally:
            await db.close()

    async def get_user(self, telegram_id: int):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await db.close()

    async def is_banned(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        return bool(user and user["is_banned"])

    async def ban_user(self, telegram_id: int):
        db = await self._get_db()
        try:
            await db.execute("UPDATE users SET is_banned = 1 WHERE telegram_id = ?", (telegram_id,))
            await db.commit()
        finally:
            await db.close()

    async def unban_user(self, telegram_id: int):
        db = await self._get_db()
        try:
            await db.execute("UPDATE users SET is_banned = 0 WHERE telegram_id = ?", (telegram_id,))
            await db.commit()
        finally:
            await db.close()

    async def get_all_users(self):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_users_count(self) -> int:
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT COUNT(*) as count FROM users")
            row = await cursor.fetchone()
            return row["count"] if row else 0
        finally:
            await db.close()

    async def get_today_users_count(self) -> int:
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')"
            )
            row = await cursor.fetchone()
            return row["count"] if row else 0
        finally:
            await db.close()

    # ---- Movies ----
    async def _next_code(self) -> str:
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT MAX(id) as max_id FROM movies")
            row = await cursor.fetchone()
            next_id = (row["max_id"] or 0) + 1
            return f"{next_id:04d}"
        finally:
            await db.close()

    async def add_movie(self, name: str, category_id: int, file_id: str, caption: str = None) -> str:
        code = await self._next_code()
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT INTO movies (code, name, category_id, file_id, caption) VALUES (?, ?, ?, ?, ?)",
                (code, name, category_id, file_id, caption)
            )
            await db.commit()
            return code
        finally:
            await db.close()

    async def get_movie_by_code(self, code: str):
        db = await self._get_db()
        try:
            # Remove # prefix if present
            code = code.lstrip("#").strip()
            cursor = await db.execute("SELECT * FROM movies WHERE code = ?", (code,))
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await db.close()

    async def search_movies(self, query: str, limit: int = 10):
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM movies WHERE name LIKE ? LIMIT ?",
                (f"%{query}%", limit)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_recent_movies(self, limit: int = 10):
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM movies ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_top_movies(self, limit: int = 10):
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM movies ORDER BY views DESC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_movies_by_category(self, category_id: int):
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM movies WHERE category_id = ? ORDER BY created_at DESC",
                (category_id,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_all_movies(self, page: int = 0, per_page: int = 10):
        db = await self._get_db()
        try:
            offset = page * per_page
            cursor = await db.execute(
                "SELECT * FROM movies ORDER BY id DESC LIMIT ? OFFSET ?",
                (per_page, offset)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_movies_count(self) -> int:
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT COUNT(*) as count FROM movies")
            row = await cursor.fetchone()
            return row["count"] if row else 0
        finally:
            await db.close()

    async def delete_movie(self, code: str):
        db = await self._get_db()
        try:
            code = code.lstrip("#").strip()
            await db.execute("DELETE FROM movies WHERE code = ?", (code,))
            await db.commit()
        finally:
            await db.close()

    async def increment_views(self, movie_id: int):
        db = await self._get_db()
        try:
            await db.execute("UPDATE movies SET views = views + 1 WHERE id = ?", (movie_id,))
            await db.commit()
        finally:
            await db.close()

    # ---- Categories ----
    async def add_category(self, name: str):
        db = await self._get_db()
        try:
            await db.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
            await db.commit()
        finally:
            await db.close()

    async def get_categories(self):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM categories ORDER BY name")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def get_category(self, category_id: int):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await db.close()

    async def delete_category(self, category_id: int):
        db = await self._get_db()
        try:
            await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            await db.commit()
        finally:
            await db.close()

    # ---- Channels ----
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

    async def get_channels(self):
        db = await self._get_db()
        try:
            cursor = await db.execute("SELECT * FROM channels")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def delete_channel(self, channel_id: int):
        db = await self._get_db()
        try:
            await db.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
            await db.commit()
        finally:
            await db.close()
