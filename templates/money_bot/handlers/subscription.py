from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from templates.money_bot.database import MoneyDB
from templates.money_bot.keyboards import subscription_kb

async def check_subscription(bot: Bot, user_id: int, money_db: MoneyDB) -> bool:
    """Check if user is subscribed to all mandatory channels."""
    channels = await money_db.get_channels()
    if not channels:
        return True
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(
                chat_id=channel["channel_id"],
                user_id=user_id
            )
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            # If bot is not admin in channel, skip
            continue
    return True

async def send_subscription_message(message: Message, money_db: MoneyDB):
    channels = await money_db.get_channels()
    await message.answer(
        "❌ <b>Kanallarimizga obuna bo'ling!</b>\n\n"
        "Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'lishingiz kerak:",
        reply_markup=subscription_kb(channels),
        parse_mode="HTML"
    )

async def send_subscription_callback(callback: CallbackQuery, money_db: MoneyDB):
    channels = await money_db.get_channels()
    await callback.message.answer(
        "❌ <b>Kanallarimizga obuna bo'ling!</b>\n\n"
        "Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'lishingiz kerak:",
        reply_markup=subscription_kb(channels),
        parse_mode="HTML"
    )
