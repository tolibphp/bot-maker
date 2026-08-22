import os
from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import TEMPLATES, BOT_CREATE_PRICE, FREE_TRIAL_DAYS, DB_PATH
from database.users import get_balance, update_balance
from database.bots import add_bot, get_bot_by_token
from database.payments import add_payment
from master_bot.keyboards import templates_kb, confirm_create_kb, main_menu_kb, cancel_kb
from master_bot.states import CreateBotStates

router = Router()


@router.message(F.text == "🤖 Bot yaratish")
async def create_bot_start(message: Message, state: FSMContext):
    await message.answer(
        "🤖 <b>Bot yaratish</b>\n\n"
        "Quyidagi shablonlardan birini tanlang:",
        reply_markup=templates_kb(),
        parse_mode="HTML"
    )
    await state.set_state(CreateBotStates.choosing_template)


@router.callback_query(F.data.startswith("template:"), CreateBotStates.choosing_template)
async def template_chosen(callback: CallbackQuery, state: FSMContext):
    template_type = callback.data.split(":")[1]
    template = TEMPLATES.get(template_type)
    
    if not template:
        await callback.answer("Shablon topilmadi!", show_alert=True)
        return
    
    balance = await get_balance(callback.from_user.id)
    price = template["price"]
    
    if balance < price:
        await callback.message.edit_text(
            f"❌ <b>Balans yetarli emas!</b>\n\n"
            f"💰 Sizning balans: <b>{balance:,} so'm</b>\n"
            f"💲 Kerakli summa: <b>{price:,} so'm</b>\n"
            f"📉 Yetishmayapti: <b>{price - balance:,} so'm</b>\n\n"
            f"💳 Avval balansni to'ldiring.",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    await state.update_data(template_type=template_type, price=price)
    await callback.message.edit_text(
        f"✅ <b>{template['name']}</b> tanlandi\n\n"
        f"💲 Narxi: <b>{price:,} so'm</b>\n"
        f"💰 Sizning balans: <b>{balance:,} so'm</b>\n\n"
        f"Endi @BotFather dan olgan tokeningizni yuboring:\n\n"
        f"📝 <i>Token misol: 123456789:ABCDefGHIjklMNOpqrsTUVwxyz</i>",
        parse_mode="HTML"
    )
    await state.set_state(CreateBotStates.waiting_token)


@router.message(CreateBotStates.waiting_token)
async def token_received(message: Message, state: FSMContext):
    token = message.text.strip()
    
    # Check if token is already used
    existing = await get_bot_by_token(token)
    if existing:
        await message.answer(
            "❌ Bu token allaqachon ishlatilgan!\n"
            "Boshqa token yuboring yoki /start bosing.",
            reply_markup=cancel_kb(),
            parse_mode="HTML"
        )
        return
    
    # Validate token via Telegram API
    try:
        test_bot = Bot(token=token)
        bot_info = await test_bot.get_me()
        await test_bot.session.close()
    except Exception:
        await message.answer(
            "❌ <b>Token noto'g'ri!</b>\n\n"
            "Iltimos, to'g'ri token yuboring.\n"
            "Token @BotFather dan olinadi.",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    await state.update_data(
        bot_token=token,
        bot_username=bot_info.username,
        bot_name=bot_info.first_name
    )
    
    await message.answer(
        f"🤖 <b>Bot topildi!</b>\n\n"
        f"📛 Nomi: <b>{bot_info.first_name}</b>\n"
        f"👤 Username: @{bot_info.username}\n"
        f"💲 Narxi: <b>{data['price']:,} so'm</b>\n"
        f"🎁 Bepul davr: <b>30 kun</b>\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=confirm_create_kb(),
        parse_mode="HTML"
    )
    await state.set_state(CreateBotStates.confirming)


@router.callback_query(F.data == "confirm_create", CreateBotStates.confirming)
async def confirm_create(callback: CallbackQuery, state: FSMContext, bot_manager=None):
    data = await state.get_data()
    user_id = callback.from_user.id
    price = data["price"]
    
    # Check balance again
    balance = await get_balance(user_id)
    if balance < price:
        await callback.message.edit_text("❌ Balans yetarli emas!")
        await state.clear()
        return
    
    # Deduct balance
    await update_balance(user_id, -price)
    
    # Record payment
    await add_payment(
        user_telegram_id=user_id,
        amount=-price,
        payment_type="bot_create",
        description=f"{data['template_type']} bot yaratish: @{data['bot_username']}"
    )
    
    # Create bot record
    free_until = datetime.now() + timedelta(days=FREE_TRIAL_DAYS)
    bot_db_path = os.path.join(DB_PATH, f"kino_bot_{data['bot_username']}.db")
    
    bot_id = await add_bot(
        owner_telegram_id=user_id,
        bot_token=data["bot_token"],
        bot_username=data["bot_username"],
        template_type=data["template_type"],
        db_path=bot_db_path,
        free_until=free_until
    )
    
    # Start the bot via bot_manager
    # bot_manager is injected via middleware or passed from main
    from bot_manager import manager
    try:
        await manager.start_bot(bot_id)
        status_text = "✅ Bot muvaffaqiyatli ishga tushdi!"
    except Exception as e:
        status_text = f"⚠️ Bot yaratildi, lekin ishga tushirishda xatolik: {e}"
    
    await callback.message.edit_text(
        f"🎉 <b>Tabriklaymiz!</b>\n\n"
        f"{status_text}\n\n"
        f"🤖 Bot: @{data['bot_username']}\n"
        f"📋 Shablon: {data['template_type']}\n"
        f"💸 To'landi: {price:,} so'm\n"
        f"🎁 Bepul davr: {FREE_TRIAL_DAYS} kun\n"
        f"📅 Bepul davr tugashi: {free_until.strftime('%d.%m.%Y')}\n\n"
        f"Admin panel: botingizga /start yuboring!",
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=main_menu_kb(callback.from_user.id),
        parse_mode="HTML"
    )
