from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from database.channels import get_channels
from master_bot.keyboards import subscription_kb
from master_bot.emojis import CHECK

router = Router()

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Check if user is subscribed to all required channels."""
    channels = await get_channels()
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
            # If bot cannot check membership (e.g., not admin, invalid channel), assume not subscribed.
            return False
    return True

async def send_subscription_message(message: Message):
    """Send message asking user to subscribe to channels."""
    channels = await get_channels()
    await message.answer(
        "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        reply_markup=subscription_kb(channels),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    if await check_subscription(callback.bot, callback.from_user.id):
        await callback.message.delete()
        
        # Optionally send a success message or just let them send /start again
        from master_bot.handlers.start import cmd_start
        # We can just simulate a start command
        callback.message.from_user = callback.from_user
        callback.message.text = "/start"
        await cmd_start(callback.message)
    else:
        await callback.answer("❌ Hali hamma kanallarga obuna bo'lmapsiz!", show_alert=True)
