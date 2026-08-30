import re

with open('master_bot/handlers/user.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from database.promocodes import use_promocode' not in content:
    content = content.replace('from database import users', 'from database import users\nfrom database.promocodes import use_promocode')

if 'from master_bot.states import' in content:
    content = content.replace('CreateBotStates, PaymentStates', 'CreateBotStates, PaymentStates, UsePromocodeStates')

user_promo_handlers = '''
    # ==========================================
    #  PROMOCODE (User)
    # ==========================================
    @router.message(F.text == "Promo-kod")
    async def use_promo_start(message: Message, state: FSMContext):
        if await users.is_banned(message.from_user.id):
            return
            
        await message.answer(
            "🎁 <b>Promo-kodni kiriting:</b>\\n\\n"
            "Agar sizda chegirma kodi bo'lsa, uni shu yerga yozib yuboring.",
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
                f"{msg}\\n\\n"
                f"💸 Balansingizga <b>{reward} so'm</b> qo'shildi!",
                reply_markup=main_menu_kb(user_id),
                parse_mode="HTML"
            )
            # Notify admin
            from config import ADMIN_ID
            try:
                await message.bot.send_message(
                    ADMIN_ID,
                    f"🎁 <b>Promo-kod ishlatildi!</b>\\n\\n"
                    f"👤 User: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\\n"
                    f"🎟 Kod: <code>{code}</code>\\n"
                    f"💸 Berildi: {reward} so'm",
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
'''

# insert before return router
content = content.replace('    return router', user_promo_handlers + '\n    return router')

with open('master_bot/handlers/user.py', 'w', encoding='utf-8') as f:
    f.write(content)

