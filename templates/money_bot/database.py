import aiosqlite
import os

class MoneyDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA journal_mode=WAL")
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    referred_by INTEGER,
                    is_verified INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_referred_by ON users(referred_by);
                CREATE INDEX IF NOT EXISTS idx_balance ON users(balance DESC);

                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    name TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            
            # Default settings
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ref_bonus', '5000')")
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('min_withdraw', '25000')")
            await db.commit()

    async def add_user(self, telegram_id: int, username: str = None, referred_by: int = None) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
            if await cursor.fetchone():
                await db.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (username, telegram_id))
                await db.commit()
                return False
            
            await db.execute(
                "INSERT INTO users (telegram_id, username, referred_by, is_verified) VALUES (?, ?, ?, 0)",
                (telegram_id, username, referred_by)
            )
            await db.commit()
            return True

    async def verify_user(self, telegram_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET is_verified = 1 WHERE telegram_id = ?", (telegram_id,))
            await db.commit()

    async def get_user_by_username(self, username: str):
        username = username.replace("@", "").lower()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE LOWER(username) = ?", (username,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_user(self, telegram_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_balance(self, telegram_id: int, amount: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
                (amount, telegram_id)
            )
            if amount > 0:
                await db.execute(
                    "UPDATE users SET total_earned = total_earned + ? WHERE telegram_id = ?",
                    (amount, telegram_id)
                )
            await db.commit()

    async def get_referral_count(self, telegram_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users WHERE referred_by = ? AND is_verified = 1", (telegram_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_top_users(self, limit: int = 10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT telegram_id, username, total_earned FROM users ORDER BY total_earned DESC LIMIT ?", 
                (limit,)
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def get_setting(self, key: str) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_setting(self, key: str, value: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    async def get_channels(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM channels")
            return [dict(r) for r in await cursor.fetchall()]

    async def add_channel(self, channel_id: int, name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO channels (channel_id, name) VALUES (?, ?)", (channel_id, name))
            await db.commit()

    async def delete_channel(self, channel_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            await db.commit()

    async def get_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return row[0] if row else 0
