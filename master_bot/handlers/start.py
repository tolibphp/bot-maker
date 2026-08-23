from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.users import add_user, add_user_with_referral, get_user, update_balance
from database.payments import add_payment
from master_bot.keyboards import main_menu_kb
from config import ADMIN_USERNAME

REFERRAL_JOIN_BONUS = 1_000  # Referrer gets 1,000 when someone joins

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text = message.text or ""

    # Check for referral deep link: /start ref_123456789
    referrer_id = None
    if " " in text:
        arg = text.split(" ", 1)[1].strip()
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg[4:])
                if referrer_id == user_id:
                    referrer_id = None  # Can't refer yourself
            except ValueError:
                referrer_id = None

    # Register user (with referral if applicable)
    if referrer_id:
        is_new = await add_user_with_referral(
            telegram_id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referred_by=referrer_id
        )

        # Give bonus to referrer only for NEW users
        if is_new and referrer_id:
            referrer = await get_user(referrer_id)
            if referrer:
                await update_balance(referrer_id, REFERRAL_JOIN_BONUS)
                await add_payment(
                    user_telegram_id=referrer_id,
                    amount=REFERRAL_JOIN_BONUS,
                    payment_type="referral_join",
                    description=f"Referral bonus: yangi user"
                )
                # Notify referrer
                try:
                    await message.bot.send_message(
                        referrer_id,
                        f"🎉 <b>Referral bonus!</b>\n\n"
                        f"👤 {message.from_user.full_name} sizning havolangiz orqali qo'shildi!\n"
                        f"💰 <b>+{REFERRAL_JOIN_BONUS:,} so'm</b> balansga qo'shildi.",
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

    await message.answer(
        "🤖 <b>Bot Maker</b> ga xush kelibsiz!\n\n"
        "Bu bot orqali siz o'zingizning Telegram botingizni yaratishingiz mumkin.\n\n"
        "🎬 <b>Mavjud shablonlar:</b>\n"
        "• Kino Bot — 35,000 so'm\n\n"
        "🎁 Birinchi 30 kun <b>BEPUL!</b>\n"
        "Keyin kuniga 5,000 so'm.",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )


@router.message(F.text == "🔙 Orqaga")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )


@router.message(F.text == "📞 Aloqa")
async def contact(message: Message):
    await message.answer(
        f"📞 <b>Aloqa</b>\n\n"
        f"Savollar va takliflar uchun admin ga yozing:\n"
        f"👤 {ADMIN_USERNAME}",
        parse_mode="HTML"
    )
