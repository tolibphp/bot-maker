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
from master_bot.emojis import BOT, MONEY, DOWN, CROSS, CHECK, PERSON, GIFT, BACK, LIST, CLOCK

router = Router()

@router.message(F.text.in_({"🤖 Bot yaratish", " Bot yaratish", "Bot yaratish"}))
async def create_bot_start(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return
        
    await message.answer(
        f"{BOT} <b>Qanday bot yaratmoqchisiz?</b>\n\n"
        f"Kerakli shablonni tanlang:",
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
            f"{CROSS} <b>Balans yetarli emas!</b>\n\n"
            f"<blockquote>{MONEY} Sizning balans: <b>{balance:,} so'm</b>\n"
            f"{MONEY} Kerakli summa: <b>{price:,} so'm</b>\n"
            f"{CROSS} Yetishmayapti: <b>{price - balance:,} so'm</b></blockquote>\n\n"
            f"Avval balansni to'ldiring.",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    await state.update_data(template_type=template_type, price=price)
    await callback.message.edit_text(
        f"{CHECK} <b>{template['name']}</b> tanlandi\n\n"
        f"<blockquote>{MONEY} Narxi: <b>{price:,} so'm</b>\n"
        f"{MONEY} Sizning balans: <b>{balance:,} so'm</b></blockquote>\n\n"
        f"{DOWN} Endi @BotFather dan olgan tokeningizni yuboring:\n\n"
        f"<i>Token misol: 123456789:ABCDefGHIjklMNOpqrsTUVwxyz</i>",
        parse_mode="HTML"
    )
    await state.set_state(CreateBotStates.waiting_token)

@router.message(CreateBotStates.waiting_token)
async def token_received(message: Message, state: FSMContext):
    token = message.text.strip()
    
    existing = await get_bot_by_token(token)
    if existing:
        await message.answer(
            f"{CROSS} Bu token allaqachon ishlatilgan!\n"
            f"Boshqa token yuboring yoki /start bosing.",
            reply_markup=cancel_kb(),
            parse_mode="HTML"
        )
        return
    
    try:
        test_bot = Bot(token=token)
        bot_info = await test_bot.get_me()
        await test_bot.session.close()
    except Exception:
        await message.answer(
            f"{CROSS} <b>Token noto'g'ri!</b>\n\n"
            f"Iltimos, to'g'ri token yuboring.\n"
            f"Token @BotFather dan olinadi.",
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
        f"{BOT} <b>Bot topildi!</b>\n\n"
        f"<blockquote>{BOT} Nomi: <b>{bot_info.first_name}</b>\n"
        f"{PERSON} Username: @{bot_info.username}\n"
        f"{MONEY} Narxi: <b>{data['price']:,} so'm</b>\n"
        f"{GIFT} Bepul davr: <b>30 kun</b></blockquote>\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=confirm_create_kb(),
        parse_mode="HTML"
    )
    await state.set_state(CreateBotStates.confirming)

@router.callback_query(F.data == "confirm_create", CreateBotStates.confirming)
async def confirm_create(callback: CallbackQuery, state: FSMContext, bot_manager=None):
    data = await state.get_data()
    if not data:
        await callback.answer("Botingiz allaqachon yaratilmoqda yoki yaratib bo'lindi!", show_alert=True)
        return
        
    user_id = callback.from_user.id
    price = data.get("price", 0)
    
    await state.clear()
    await callback.answer("Botingiz yaratilmoqda, kuting...", show_alert=False)
    
    balance = await get_balance(user_id)
    if balance < price:
        await callback.message.edit_text(f"{CROSS} Balans yetarli emas!")
        return
    
    await update_balance(user_id, -price)
    
    await add_payment(
        user_telegram_id=user_id,
        amount=-price,
        payment_type="bot_create",
        description=f"{data['template_type']} bot yaratish: @{data['bot_username']}"
    )
    
    free_until = datetime.now() + timedelta(days=FREE_TRIAL_DAYS)
    bot_db_path = os.path.join(DB_PATH, f"{data['template_type']}_{data['bot_username']}.db")
    
    bot_id = await add_bot(
        owner_telegram_id=user_id,
        bot_token=data["bot_token"],
        bot_username=data["bot_username"],
        template_type=data["template_type"],
        db_path=bot_db_path,
        free_until=free_until
    )
    
    from bot_manager import manager
    try:
        await manager.start_bot(bot_id)
        status_text = f"{CHECK} Bot muvaffaqiyatli ishga tushdi!"
    except Exception as e:
        status_text = f"{CROSS} Bot yaratildi, lekin ishga tushirishda xatolik: {e}"
    
    await callback.message.edit_text(
        f"{GIFT} <b>Tabriklaymiz!</b>\n\n"
        f"{status_text}\n\n"
        f"<blockquote>{BOT} Bot: @{data['bot_username']}\n"
        f"{LIST} Shablon: {data['template_type']}\n"
        f"{MONEY} To'landi: {price:,} so'm\n"
        f"{GIFT} Bepul davr: {FREE_TRIAL_DAYS} kun\n"
        f"{CLOCK} Bepul davr tugashi: {free_until.strftime('%d.%m.%Y')}</blockquote>\n\n"
        f"Admin panel: botingizga /start yuboring!",
        parse_mode="HTML"
    )

    from database.users import get_referrer
    REFERRAL_BOT_CREATE_BONUS = 5_000

    referrer_id = await get_referrer(user_id)
    if referrer_id:
        await update_balance(referrer_id, REFERRAL_BOT_CREATE_BONUS)
        await add_payment(
            user_telegram_id=referrer_id,
            amount=REFERRAL_BOT_CREATE_BONUS,
            payment_type="referral_bot_create",
            description=f"Referral bonus: bot yaratdi (@{data['bot_username']})"
        )
        try:
            await callback.bot.send_message(
                referrer_id,
                f"{GIFT} <b>Referral bonus!</b>\n\n"
                f"<blockquote>{BOT} Sizning referalingiz bot yaratdi: @{data['bot_username']}\n"
                f"{MONEY} <b>+{REFERRAL_BOT_CREATE_BONUS:,} so'm</b> balansga qo'shildi!</blockquote>",
                parse_mode="HTML"
            )
        except Exception:
            pass

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(f"{CROSS} Bekor qilindi.")
    await callback.message.answer(
        f"{BACK} Bosh menyu",
        reply_markup=main_menu_kb(callback.from_user.id),
        parse_mode="HTML"
    )
