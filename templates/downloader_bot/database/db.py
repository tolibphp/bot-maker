import aiosqlite
import asyncio

class DownloaderDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    url TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()

    async def add_user(self, telegram_id, full_name, username):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (telegram_id, full_name, username) VALUES (?, ?, ?)",
                (telegram_id, full_name, username)
            )
            await db.commit()
            
    async def add_download(self, telegram_id, url):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO stats (telegram_id, url) VALUES (?, ?)",
                (telegram_id, url)
            )
            await db.commit()
            
    async def get_stats(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                users = (await cursor.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM stats") as cursor:
                downloads = (await cursor.fetchone())[0]
            return users, downloads
