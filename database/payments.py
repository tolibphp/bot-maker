from database.db import get_db


async def add_payment(
    user_telegram_id: int,
    amount: int,
    payment_type: str,
    description: str = ""
):
    """Add a payment record.
    payment_type: 'deposit', 'bot_create', 'daily_fee', 'refund'
    """
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO payments (user_telegram_id, amount, payment_type, description)
            VALUES (?, ?, ?, ?)""",
            (user_telegram_id, amount, payment_type, description)
        )
        await db.commit()
    finally:
        await db.close()


async def get_user_payments(user_telegram_id: int, limit: int = 20):
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM payments 
            WHERE user_telegram_id = ? 
            ORDER BY created_at DESC LIMIT ?""",
            (user_telegram_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_total_revenue():
    """Get total revenue (bot_create + daily_fee payments)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT COALESCE(SUM(ABS(amount)), 0) as total 
            FROM payments 
            WHERE payment_type IN ('bot_create', 'daily_fee')"""
        )
        row = await cursor.fetchone()
        return row["total"] if row else 0
    finally:
        await db.close()


async def get_today_revenue():
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT COALESCE(SUM(ABS(amount)), 0) as total 
            FROM payments 
            WHERE payment_type IN ('bot_create', 'daily_fee')
            AND DATE(created_at) = DATE('now')"""
        )
        row = await cursor.fetchone()
        return row["total"] if row else 0
    finally:
        await db.close()
