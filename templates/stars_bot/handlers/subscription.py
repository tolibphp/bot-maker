from aiogram import Bot
from aiogram.types import Message
from templates.stars_bot.database import StarsDB
from templates.stars_bot.keyboards import subscription_kb

async def check_subscription(bot: Bot, user_id: int, stars_db: StarsDB) -> bool:
    """Check if user is subscribed to all mandatory channels."""
    channels = await stars_db.get_channels()
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

async def send_subscription_message(message: Message, stars_db: StarsDB):
    channels = await stars_db.get_channels()
    await message.answer(
        "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        reply_markup=subscription_kb(channels),
        parse_mode="HTML"
    )
