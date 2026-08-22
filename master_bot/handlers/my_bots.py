from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.bots import get_user_bots, get_bot, update_bot_status, delete_bot
from master_bot.keyboards import my_bots_kb, bot_manage_kb, main_menu_kb

router = Router()


@router.message(F.text == "📋 Mening botlarim")
async def my_bots(message: Message):
    bots = await get_user_bots(message.from_user.id)
    
    if not bots:
        await message.answer(
            "📋 <b>Mening botlarim</b>\n\n"
            "Sizda hali bot yo'q.\n"
            "🤖 <i>Bot yaratish</i> tugmasini bosing.",
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        f"📋 <b>Mening botlarim</b> ({len(bots)} ta)\n\n"
        f"Boshqarish uchun botni tanlang:",
        reply_markup=my_bots_kb(bots),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("mybot:"))
async def bot_details(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        await callback.answer("Bot topilmadi!", show_alert=True)
        return
    
    status_emoji = "✅ Ishlayapti" if bot["status"] == "active" else "⛔ To'xtatilgan"
    
    # Calculate free days remaining
    free_until = datetime.fromisoformat(bot["free_until"]) if bot["free_until"] else None
    if free_until and free_until > datetime.now():
        days_left = (free_until - datetime.now()).days
        trial_text = f"🎁 Bepul davr: {days_left} kun qoldi"
    else:
        trial_text = "💰 Kunlik to'lov: 5,000 so'm"
    
    await callback.message.edit_text(
        f"🤖 <b>@{bot['bot_username']}</b>\n\n"
        f"📋 Shablon: {bot['template_type']}\n"
        f"📊 Status: {status_emoji}\n"
        f"{trial_text}\n"
        f"📅 Yaratilgan: {bot['created_at'][:10]}",
        reply_markup=bot_manage_kb(bot_id, bot["status"]),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("bot_stop:"))
async def stop_bot(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        await callback.answer("Bot topilmadi!", show_alert=True)
        return
    
    from bot_manager import manager
    await manager.stop_bot(bot_id)
    await update_bot_status(bot_id, "stopped")
    
    await callback.message.edit_text(
        f"⏹ <b>@{bot['bot_username']}</b> to'xtatildi.",
        reply_markup=bot_manage_kb(bot_id, "stopped"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("bot_start:"))
async def start_bot(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        await callback.answer("Bot topilmadi!", show_alert=True)
        return
    
    from bot_manager import manager
    try:
        await manager.start_bot(bot_id)
        await update_bot_status(bot_id, "active")
        await callback.message.edit_text(
            f"▶️ <b>@{bot['bot_username']}</b> ishga tushdi!",
            reply_markup=bot_manage_kb(bot_id, "active"),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Xatolik: {e}",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("bot_delete:"))
async def delete_bot_handler(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        await callback.answer("Bot topilmadi!", show_alert=True)
        return
    
    from bot_manager import manager
    await manager.stop_bot(bot_id)
    await delete_bot(bot_id)
    
    await callback.message.edit_text(
        f"🗑 <b>@{bot['bot_username']}</b> o'chirildi.",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_bots")
async def back_to_bots(callback: CallbackQuery):
    bots = await get_user_bots(callback.from_user.id)
    if not bots:
        await callback.message.edit_text("📋 Sizda bot yo'q.")
        return
    await callback.message.edit_text(
        f"📋 <b>Mening botlarim</b> ({len(bots)} ta)",
        reply_markup=my_bots_kb(bots),
        parse_mode="HTML"
    )
