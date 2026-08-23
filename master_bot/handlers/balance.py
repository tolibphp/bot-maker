from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, ADMIN_USERNAME, PAYMENT_CARD, PAYMENT_CARD_HOLDER
from database.users import get_balance
from database.payments import get_user_payments, get_user_payments_count
from master_bot.keyboards import main_menu_kb, payment_kb, payment_approve_kb, balance_kb, payment_history_kb
from master_bot.states import PaymentStates
from master_bot.emojis import MONEY, CARD, CHECK, CROSS, SCROLL, DOWN, ID, PERSON

router = Router()


@router.message(F.text == "💰 Balansim")
async def show_balance(message: Message):
    balance = await get_balance(message.from_user.id)

    text = (
        f"{MONEY} <b>Sizning balansingiz</b>\n\n"
        f"<blockquote>{MONEY} Joriy balans: <b>{balance:,} so'm</b></blockquote>"
    )

    await message.answer(text, reply_markup=balance_kb(), parse_mode="HTML")


@router.callback_query(F.data == "back_to_balance")
async def back_to_balance(callback: CallbackQuery):
    balance = await get_balance(callback.from_user.id)

    text = (
        f"{MONEY} <b>Sizning balansingiz</b>\n\n"
        f"<blockquote>{MONEY} Joriy balans: <b>{balance:,} so'm</b></blockquote>"
    )

    await callback.message.edit_text(text, reply_markup=balance_kb(), parse_mode="HTML")


@router.callback_query(F.data.startswith("payment_history:"))
async def payment_history_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    per_page = 10
    user_id = callback.from_user.id

    total = await get_user_payments_count(user_id)
    if total == 0:
        await callback.answer("Sizda hali to'lovlar tarixi yo'q.", show_alert=True)
        return

    total_pages = (total + per_page - 1) // per_page
    if page >= total_pages:
        page = total_pages - 1
    if page < 0:
        page = 0

    offset = page * per_page
    payments = await get_user_payments(user_id, limit=per_page, offset=offset)

    text = f"{SCROLL} <b>To'lovlar tarixi</b> (Jami: {total})\n\n"
    for p in payments:
        emoji = "➕" if p["amount"] > 0 else "➖"
        date_str = p["created_at"][:16]
        text += f"<blockquote>{emoji} <b>{abs(p['amount']):,} so'm</b>\n<i>{p['description'] or p['payment_type']}</i>\n📅 {date_str}</blockquote>\n"

    await callback.message.edit_text(
        text, 
        reply_markup=payment_history_kb(page, total_pages), 
        parse_mode="HTML"
    )


@router.message(F.text == "💳 Balans to'ldirish")
async def top_up_balance(message: Message):
    await message.answer(
        f"{CARD} <b>Balans to'ldirish</b>\n\n"
        f"Quyidagi kartaga pul o'tkazing:\n\n"
        f"<blockquote>{CARD} Karta: <code>{PAYMENT_CARD}</code>\n"
        f"{PERSON} Egasi: <b>{PAYMENT_CARD_HOLDER}</b>\n\n"
        f"{ID} Sizning ID: <code>{message.from_user.id}</code></blockquote>\n\n"
        f"To'lovni amalga oshirgach, quyidagi tugmani bosing {DOWN}",
        reply_markup=payment_kb(),
        parse_mode="HTML"
    )


@router.message(F.text == "💳 To'lov qildim")
async def payment_start(message: Message, state: FSMContext):
    await message.answer(
        f"{MONEY} Qancha pul to'lov qildingiz?\n\n"
        f"Summani kiriting (masalan: <code>35000</code>):",
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
        await message.answer(f"{CROSS} Noto'g'ri summa. Faqat raqam kiriting (masalan: 35000):")
        return

    await state.update_data(payment_amount=amount)
    await message.answer(
        f"<blockquote>{MONEY} Summa: <b>{amount:,} so'm</b></blockquote>\n\n"
        f"Endi to'lov chekining <b>skrinshot</b>ini yuboring:",
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
        f"{MONEY} <b>Yangi to'lov so'rovi!</b>\n\n"
        f"<blockquote>{PERSON} Foydalanuvchi: {user.full_name}\n"
        f"{ID} ID: <code>{user.id}</code>\n"
        f"{PERSON} Username: @{user.username or 'yo\'q'}\n"
        f"{MONEY} Summa: <b>{amount:,} so'm</b></blockquote>\n\n"
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
        f"{CHECK} <b>So'rov yuborildi!</b>\n\n"
        f"<blockquote>{MONEY} Summa: {amount:,} so'm\n"
        f"{CHECK} Admin tekshirgandan so'ng balansga qo'shiladi.\n\n"
        f"Savol bo'lsa: {ADMIN_USERNAME}</blockquote>",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(PaymentStates.waiting_screenshot)
async def payment_screenshot_invalid(message: Message):
    await message.answer(
        f"{CROSS} Iltimos, to'lov chekining <b>rasmini</b> (skrinshot) yuboring.",
        parse_mode="HTML"
    )
