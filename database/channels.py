from database.db import get_db

async def add_channel(channel_id: str, channel_name: str = None):
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO channels (channel_id, channel_name) VALUES (?, ?)",
            (channel_id, channel_name)
        )
        await db.commit()
    finally:
        await db.close()

async def get_channels():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM channels")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()

async def delete_channel(channel_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        await db.commit()
    finally:
        await db.close()
