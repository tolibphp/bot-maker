from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import subscription_kb


async def check_subscription(bot: Bot, user_id: int, kino_db: KinoDB) -> bool:
    """Check if user is subscribed to all required channels."""
    channels = await kino_db.get_channels()
    if not channels:
        return True  # No channels required
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(
                chat_id=channel["channel_id"],
                user_id=user_id
            )
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            # If bot can't check (not admin in channel), skip
            continue
    return True


async def send_subscription_message(message: Message, kino_db: KinoDB):
    """Send message asking user to subscribe to channels."""
    channels = await kino_db.get_channels()
    await message.answer(
        "❌ <b>Kanallarimizga obuna bo'ling!</b>\n\n"
        "Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'lishingiz kerak:",
        reply_markup=subscription_kb(channels),
        parse_mode="HTML"
    )
