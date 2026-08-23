from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import TEMPLATES
from database.bots import get_user_bots, get_bot, update_bot_status, delete_bot
from master_bot.keyboards import my_bots_kb, bot_manage_kb, main_menu_kb
from master_bot.emojis import LIST, BOT, WRENCH, CHECK, STOP, CROSS, BACK, DOWN, MONEY, GIFT

router = Router()

@router.message(F.text == "📋 Mening botlarim")
async def my_bots_menu(message: Message):
    bots = await get_user_bots(message.from_user.id)
    if not bots:
        await message.answer(f"{LIST} Sizda hali botlar yo'q.", parse_mode="HTML")
        return

    await message.answer(
        f"{LIST} <b>Sizning botlaringiz:</b>",
        reply_markup=my_bots_kb(bots),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_bots")
async def back_to_bots_list(callback: CallbackQuery):
    bots = await get_user_bots(callback.from_user.id)
    if not bots:
        await callback.message.edit_text(f"{LIST} Sizda hali botlar yo'q.", parse_mode="HTML")
        return
    await callback.message.edit_text(
        f"{LIST} <b>Sizning botlaringiz:</b>",
        reply_markup=my_bots_kb(bots),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("mybot:"))
async def manage_bot(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        await callback.answer("Bot topilmadi!", show_alert=True)
        return

    status = "Faol" if bot["status"] == "active" else "To'xtatilgan"
    status_emoji = CHECK if bot["status"] == "active" else STOP
    username = f"@{bot['bot_username']}" if bot['bot_username'] else "Noma'lum"

    text = (
        f"{BOT} <b>Botingiz:</b> {username}\n"
        f"<blockquote>{WRENCH} Shablon: <b>{TEMPLATES[bot['template_type']]['name']}</b>\n"
        f"Holati: {status_emoji} <b>{status}</b></blockquote>\n\n"
        f"Nimani o'zgartirmoqchisiz?"
    )

    await callback.message.edit_text(
        text,
        reply_markup=bot_manage_kb(bot_id, bot["status"]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("bot_stop:"))
async def bot_stop_action(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        return
        
    from bot_manager import manager
    await manager.stop_bot(bot_id)
    await update_bot_status(bot_id, "inactive")
    
    await callback.answer("Bot to'xtatildi", show_alert=True)
    await manage_bot(callback)

@router.callback_query(F.data.startswith("bot_start:"))
async def bot_start_action(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        return
        
    from bot_manager import manager
    try:
        await manager.start_bot(bot_id)
        await callback.answer("Bot ishga tushirildi", show_alert=True)
    except Exception:
        await callback.answer("Xatolik! Token ishlamayapti", show_alert=True)
        
    await manage_bot(callback)

@router.callback_query(F.data.startswith("bot_delete:"))
async def bot_del_action(callback: CallbackQuery):
    bot_id = int(callback.data.split(":")[1])
    bot = await get_bot(bot_id)
    
    if not bot or bot["owner_telegram_id"] != callback.from_user.id:
        return
        
    from bot_manager import manager
    await manager.stop_bot(bot_id)
    await delete_bot(bot_id)
    
    await callback.answer("Bot o'chirildi", show_alert=True)
    await back_to_bots_list(callback)
