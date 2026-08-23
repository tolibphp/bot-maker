from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, ADMIN_USERNAME, PAYMENT_CARD, PAYMENT_CARD_HOLDER
from database.users import get_balance
from database.payments import get_user_payments
from master_bot.keyboards import main_menu_kb, payment_kb, payment_approve_kb
from master_bot.states import PaymentStates

router = Router()


@router.message(F.text == "💰 Balansim")
async def show_balance(message: Message):
    balance = await get_balance(message.from_user.id)
    payments = await get_user_payments(message.from_user.id, limit=5)

    text = (
        f"💰 <b>Balansim</b>\n\n"
        f"💵 Joriy balans: <b>{balance:,} so'm</b>\n"
    )

    if payments:
        text += "\n📜 <b>Oxirgi operatsiyalar:</b>\n"
        for p in payments:
            emoji = "➕" if p["amount"] > 0 else "➖"
            text += f"{emoji} {abs(p['amount']):,} so'm — {p['description'] or p['payment_type']}\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "💳 Balans to'ldirish")
async def top_up_balance(message: Message):
    await message.answer(
        f"💳 <b>Balans to'ldirish</b>\n\n"
        f"🏦 Quyidagi kartaga pul o'tkazing:\n\n"
        f"💳 Karta: <code>{PAYMENT_CARD}</code>\n"
        f"👤 Egasi: <b>{PAYMENT_CARD_HOLDER}</b>\n\n"
        f"🆔 Sizning ID: <code>{message.from_user.id}</code>\n\n"
        f"To'lovni amalga oshirgach, quyidagi tugmani bosing ⬇️",
        reply_markup=payment_kb(),
        parse_mode="HTML"
    )


@router.message(F.text == "💳 To'lov qildim")
async def payment_start(message: Message, state: FSMContext):
    await message.answer(
        "💰 Qancha pul to'lov qildingiz?\n\n"
        "Summani kiriting (masalan: <code>35000</code>):",
        parse_mode="HTML"
    )
    await state.set_state(PaymentStates.waiting_amount)


@router.message(PaymentStates.waiting_amount)
async def payment_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip().replace(",", "").replace(" ", "").replace(".", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Noto'g'ri summa. Faqat raqam kiriting (masalan: 35000):")
        return

    await state.update_data(payment_amount=amount)
    await message.answer(
        f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
        f"📸 Endi to'lov chekining <b>skrinshot</b>ini yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(PaymentStates.waiting_screenshot)


@router.message(PaymentStates.waiting_screenshot, F.photo)
async def payment_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data["payment_amount"]
    user = message.from_user

    # Send to admin for approval
    admin_text = (
        f"💳 <b>Yangi to'lov so'rovi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.full_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Username: @{user.username or 'yo\'q'}\n"
        f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
        f"Tasdiqlaysizmi?"
    )

    try:
        await message.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=payment_approve_kb(user.id, amount),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>So'rov yuborildi!</b>\n\n"
        f"💰 Summa: {amount:,} so'm\n"
        f"⏳ Admin tekshirgandan so'ng balansga qo'shiladi.\n\n"
        f"📞 Savol bo'lsa: {ADMIN_USERNAME}",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(PaymentStates.waiting_screenshot)
async def payment_screenshot_invalid(message: Message):
    await message.answer(
        "❌ Iltimos, to'lov chekining <b>rasmini</b> (skrinshot) yuboring.",
        parse_mode="HTML"
    )
