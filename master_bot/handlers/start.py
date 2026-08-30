from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, ADMIN_USERNAME, TEMPLATES
from database.users import add_user_with_referral, add_user, get_user, update_balance
from database.payments import add_payment
from master_bot.keyboards import main_menu_kb
from master_bot.emojis import BOT, MOVIE, STAR, CASH, GIFT, BACK, PHONE, CHECK, PERSON, MONEY, INBOX

router = Router()

REFERRAL_JOIN_BONUS = 1_000

@router.message(CommandStart())
async def cmd_start(message: Message):
    from master_bot.handlers.subscription import check_subscription, send_subscription_message
    if not await check_subscription(message.bot, message.from_user.id):
        await send_subscription_message(message)
        return

    user_id = message.from_user.id
    text = message.text or ""

    # Referral logic
    referrer_id = None
    if " " in text:
        arg = text.split(" ", 1)[1].strip()
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg[4:])
                if referrer_id == user_id:
                    referrer_id = None
            except ValueError:
                pass

    user = await get_user(user_id)
    if not user:
        is_new = await add_user_with_referral(
            telegram_id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referred_by=referrer_id
        )
        
        if is_new and referrer_id:
            ref_user = await get_user(referrer_id)
            if ref_user:
                await update_balance(referrer_id, REFERRAL_JOIN_BONUS)
                await add_payment(
                    user_telegram_id=referrer_id,
                    amount=REFERRAL_JOIN_BONUS,
                    payment_type="referral_join",
                    description=f"Referral bonus: yangi user"
                )
                try:
                    await message.bot.send_message(
                        referrer_id,
                        f"{GIFT} <b>Referral bonus!</b>\n\n"
                        f"<blockquote>{PERSON} {message.from_user.full_name} sizning havolangiz orqali qo'shildi!\n"
                        f"{MONEY} <b>+{REFERRAL_JOIN_BONUS:,} so'm</b> balansga qo'shildi.</blockquote>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
    else:
        await add_user(
            telegram_id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )

    # Build dynamic template list
    template_list = ""
    for tmpl_id, tmpl in TEMPLATES.items():
        template_list += f"🔹 <b>{tmpl['name']}</b> — {tmpl['price']:,} so'm\n"

    await message.answer(
        f"{BOT} <b>Bot Maker Xizmatiga Xush Kelibsiz!</b>\n\n"
        f"Bu yerda siz hech qanday dasturlash bilimisiz, bir necha soniya ichida o'z Telegram botingizni yarata olasiz.\n\n"
        f"<blockquote><b>Mavjud Shablonlar:</b>\n"
        f"{template_list}\n"
        f"{GIFT} <i>Siz yaratgan har qanday bot dastlabki 30 kun mutlaqo BEPUL ishlaydi!</i>\n"
        f"Keyin oylik yoki kunlik tarif bo'yicha hisoblanadi.</blockquote>\n\n"
        f"👇 <b>Marhamat, quyidagi tugmalar orqali xizmatlardan foydalaning:</b>",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"🔙 Orqaga", "Orqaga"}))
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{BACK} Asosiy menyu",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"📞 Aloqa", "Aloqa"}))
async def contact(message: Message):
    await message.answer(
        f"{PHONE} <b>Aloqa</b>\n\n"
        f"<blockquote>Savollar va takliflar uchun adminga yozing:\n"
        f"{PERSON} {ADMIN_USERNAME}</blockquote>",
        parse_mode="HTML"
    )
