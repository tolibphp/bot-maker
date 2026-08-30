from database.db import get_db

async def create_promocode(code: str, reward_amount: int, usage_limit: int):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO promocodes (code, reward_amount, usage_limit) VALUES (?, ?, ?)" ,
            (code.upper(), reward_amount, usage_limit)
        )
        await db.commit()
        return True
    except Exception:
        return False
    finally:
        await db.close()

async def get_all_promocodes():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM promocodes ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()

async def delete_promocode(promo_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM promocodes WHERE id = ?", (promo_id,))
        await db.execute("DELETE FROM promocode_usages WHERE promocode_id = ?", (promo_id,))
        await db.commit()
    finally:
        await db.close()

async def use_promocode(user_id: int, code: str):
    db = await get_db()
    try:
        code = code.upper()
        cursor = await db.execute("SELECT * FROM promocodes WHERE code = ?", (code,))
        promo = await cursor.fetchone()
        
        if not promo:
            return False, "❌ Bunday promo-kod mavjud emas yoki noto'g'ri yozdingiz.", 0
            
        promo = dict(promo)
        if not promo["is_active"]:
            return False, "❌ Ushbu promo-kod faol emas.", 0
            
        if promo["used_count"] >= promo["usage_limit"]:
            return False, "❌ Ushbu promo-kodning limiti tugagan.", 0
            
        cursor = await db.execute(
            "SELECT id FROM promocode_usages WHERE user_telegram_id = ? AND promocode_id = ?",
            (user_id, promo["id"])
        )
        usage = await cursor.fetchone()
        
        if usage:
            return False, "❌ Siz bu promo-koddan avval foydalangansiz!", 0
            
        await db.execute(
            "INSERT INTO promocode_usages (user_telegram_id, promocode_id) VALUES (?, ?)",
            (user_id, promo["id"])
        )
        await db.execute(
            "UPDATE promocodes SET used_count = used_count + 1 WHERE id = ?",
            (promo["id"],)
        )
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
            (promo["reward_amount"], user_id)
        )
        await db.commit()
        return True, "✅ Promo-kod muvaffaqiyatli ishlatildi!", promo["reward_amount"]
        
    finally:
        await db.close()
