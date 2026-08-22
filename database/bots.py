from database.db import get_db
from datetime import datetime


async def add_bot(
    owner_telegram_id: int,
    bot_token: str,
    bot_username: str,
    template_type: str,
    db_path: str,
    free_until: datetime
):
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO bots 
            (owner_telegram_id, bot_token, bot_username, template_type, db_path, free_until)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (owner_telegram_id, bot_token, bot_username, template_type, db_path,
             free_until.isoformat())
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_bot(bot_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_bot_by_token(token: str):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM bots WHERE bot_token = ?", (token,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_user_bots(owner_telegram_id: int):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM bots WHERE owner_telegram_id = ? ORDER BY created_at DESC",
            (owner_telegram_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_all_active_bots():
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM bots WHERE status = 'active'"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_all_bots():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM bots ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_bots_count():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM bots")
        row = await cursor.fetchone()
        return row["count"] if row else 0
    finally:
        await db.close()


async def get_active_bots_count():
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM bots WHERE status = 'active'"
        )
        row = await cursor.fetchone()
        return row["count"] if row else 0
    finally:
        await db.close()


async def update_bot_status(bot_id: int, status: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bots SET status = ? WHERE id = ?",
            (status, bot_id)
        )
        await db.commit()
    finally:
        await db.close()


async def update_last_payment(bot_id: int):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bots SET last_payment_at = ? WHERE id = ?",
            (datetime.now().isoformat(), bot_id)
        )
        await db.commit()
    finally:
        await db.close()


async def delete_bot(bot_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM bots WHERE id = ?", (bot_id,))
        await db.commit()
    finally:
        await db.close()


async def get_bots_needing_payment():
    """Get active bots whose free trial has expired."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM bots 
            WHERE status = 'active' 
            AND free_until < ?""",
            (datetime.now().isoformat(),)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()
