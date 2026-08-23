from database.db import get_db


async def add_user(telegram_id: int, username: str = None, full_name: str = None):
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
            (telegram_id, username, full_name)
        )
        await db.commit()
    finally:
        await db.close()


async def get_user(telegram_id: int):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        await db.close()


async def get_all_users():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_users_count():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        return row["count"] if row else 0
    finally:
        await db.close()


async def get_balance(telegram_id: int) -> int:
    user = await get_user(telegram_id)
    return user["balance"] if user else 0


async def update_balance(telegram_id: int, amount: int):
    """Add amount to balance. Use negative amount to deduct."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()
    finally:
        await db.close()


async def set_balance(telegram_id: int, amount: int):
    """Set exact balance."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET balance = ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()
    finally:
        await db.close()


async def add_user_with_referral(telegram_id: int, username: str = None,
                                  full_name: str = None, referred_by: int = None):
    """Add user with referral info. Returns True if NEW user, False if exists."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        existing = await cursor.fetchone()
        if existing:
            return False  # User already exists

        await db.execute(
            "INSERT INTO users (telegram_id, username, full_name, referred_by) VALUES (?, ?, ?, ?)",
            (telegram_id, username, full_name, referred_by)
        )
        await db.commit()
        return True  # New user
    finally:
        await db.close()


async def get_referral_count(telegram_id: int) -> int:
    """Count how many users were referred by this user."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE referred_by = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
        return row["count"] if row else 0
    finally:
        await db.close()


async def get_referrer(telegram_id: int):
    """Get the referrer's telegram_id for this user."""
    user = await get_user(telegram_id)
    if user and user.get("referred_by"):
        return user["referred_by"]
    return None
