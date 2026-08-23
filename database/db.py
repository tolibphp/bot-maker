import aiosqlite
import os
from config import DB_PATH


async def get_db():
    """Get connection to master database."""
    os.makedirs(DB_PATH, exist_ok=True)
    db = await aiosqlite.connect(os.path.join(DB_PATH, "master.db"))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    return db


async def init_master_db():
    """Create master database tables."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 0,
                referred_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_telegram_id INTEGER NOT NULL,
                bot_token TEXT NOT NULL,
                bot_username TEXT,
                template_type TEXT DEFAULT 'kino',
                status TEXT DEFAULT 'active',
                db_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                free_until TIMESTAMP,
                last_payment_at TIMESTAMP,
                FOREIGN KEY (owner_telegram_id) REFERENCES users(telegram_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                payment_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_telegram_id) REFERENCES users(telegram_id)
            );
        """)
        await db.commit()

        # Add referred_by column if it doesn't exist (migration for existing DBs)
        try:
            await db.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
            await db.commit()
        except Exception:
            pass  # Column already exists

    finally:
        await db.close()
