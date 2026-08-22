from aiogram import Router, F
from aiogram.types import Message

from config import ADMIN_ID
from database.users import get_balance
from database.payments import get_user_payments
from master_bot.keyboards import main_menu_kb

router = Router()


@router.message(F.text == "💰 Balansim")
async def show_balance(message: Message):
    balance = await get_balance(message.from_user.id)
    payments = await get_user_payments(message.from_user.id, limit=5)
    
    text = (
        f"💰 <b>Balansim</b>\n\n"
        f"💵 Joriy balans: <b>{balance:,} so'm</b>\n"
    )
    
    if payments:
        text += "\n📜 <b>Oxirgi operatsiyalar:</b>\n"
        for p in payments:
            emoji = "➕" if p["amount"] > 0 else "➖"
            text += f"{emoji} {abs(p['amount']):,} so'm — {p['description'] or p['payment_type']}\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "💳 Balans to'ldirish")
async def top_up_balance(message: Message):
    await message.answer(
        f"💳 <b>Balans to'ldirish</b>\n\n"
        f"Balansni to'ldirish uchun admin ga yozing:\n"
        f"👤 <a href='tg://user?id={ADMIN_ID}'>Admin</a>\n\n"
        f"📝 <b>Qanday qilish:</b>\n"
        f"1. Admin ga pul o'tkazing\n"
        f"2. Chekni admin ga yuboring\n"
        f"3. Admin balansni qo'shadi\n\n"
        f"🆔 Sizning ID: <code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )
