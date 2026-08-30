from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import users
from database.promocodes import use_promocode
from master_bot.states import UsePromocodeStates
from master_bot.keyboards import main_menu_kb, cancel_kb
from master_bot.emojis import PROMO_GIFT, CHECK, MONEY

router = Router()

@router.message(F.text == "Promo-kod")
async def use_promo_start(message: Message, state: FSMContext):
    await message.answer(
        f"{PROMO_GIFT} <b>Promo-kodni kiriting:</b>\n\n"
        f"Agar sizda chegirma kodi bo'lsa, uni shu yerga yozib yuboring.",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    await state.set_state(UsePromocodeStates.waiting_code)

@router.message(UsePromocodeStates.waiting_code)
async def use_promo_apply(message: Message, state: FSMContext):
    code = message.text.strip()
    user_id = message.from_user.id
    
    success, msg, reward = await use_promocode(user_id, code)
    
    if success:
        await message.answer(
            f"{CHECK} {msg}\n\n"
            f"{MONEY} Balansingizga <b>{reward} so'm</b> qo'shildi!",
            reply_markup=main_menu_kb(user_id),
            parse_mode="HTML"
        )
        # Notify admin
        from config import ADMIN_ID
        try:
            await message.bot.send_message(
                ADMIN_ID,
                f"{PROMO_GIFT} <b>Promo-kod ishlatildi!</b>\n\n"
                f"👤 User: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
                f"🔑 Kod: <code>{code}</code>\n"
                f"💰 Berildi: {reward} so'm",
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        await message.answer(
            msg,
            reply_markup=main_menu_kb(user_id)
        )
        
    await state.clear()
