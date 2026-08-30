import re

with open('master_bot/handlers/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we import what we need
if 'from database.promocodes import' not in content:
    content = content.replace('from database import users', 'from database import users\nfrom database.promocodes import create_promocode, get_all_promocodes, delete_promocode')

if 'from master_bot.states import' in content:
    content = content.replace('AdminAddBalanceStates,', 'AdminAddBalanceStates, PromocodeStates,')

if 'from master_bot.keyboards import' in content:
    content = content.replace('admin_panel_kb,', 'admin_panel_kb, promocodes_manage_kb,')

admin_promo_handlers = '''
    # ==========================================
    #  PROMOCODES (Admin)
    # ==========================================
    @router.message(F.text == "🎁 Promo-kodlar")
    async def manage_promocodes(message: Message):
        if not is_admin(message):
            return
        
        promos = await get_all_promocodes()
        text = "🎁 <b>Promo-kodlar</b>\\n\\n"
        if not promos:
            text += "Hali hech qanday promo-kod yaratilmagan."
        else:
            text += "Quyida yaratilgan kodlar ro'yxati:"
            
        await message.answer(
            text,
            reply_markup=promocodes_manage_kb(promos),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_promocode")
    async def add_promo_start(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🎁 <b>Yangi Promo-kod</b>\\n\\n"
            "Kod nomini kiriting (faqat harf va raqamlar, probelsiz):\\n"
            "Masalan: <code>YANGIYIL</code>",
            parse_mode="HTML"
        )
        await state.set_state(PromocodeStates.waiting_code)

    @router.message(PromocodeStates.waiting_code)
    async def add_promo_code(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        code = message.text.strip().upper()
        if " " in code:
            await message.answer("❌ Kodda probel bo'lishi mumkin emas. Qaytadan kiriting:")
            return
        await state.update_data(promo_code=code)
        
        await message.answer("💸 Bu kod foydalanuvchiga qancha balans beradi? (Masalan: 5000):")
        await state.set_state(PromocodeStates.waiting_reward)

    @router.message(PromocodeStates.waiting_reward)
    async def add_promo_reward(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        try:
            reward = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting:")
            return
            
        await state.update_data(promo_reward=reward)
        await message.answer("👥 Ushbu koddan jami nechta odam foydalana oladi? (Limitni kiriting):")
        await state.set_state(PromocodeStates.waiting_limit)

    @router.message(PromocodeStates.waiting_limit)
    async def add_promo_limit(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        try:
            limit = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting:")
            return
            
        data = await state.get_data()
        code = data.get("promo_code")
        reward = data.get("promo_reward")
        
        success = await create_promocode(code, reward, limit)
        if success:
            await message.answer(
                f"✅ <b>Promo-kod yaratildi!</b>\\n\\n"
                f"🎁 Kod: <code>{code}</code>\\n"
                f"💸 Beriladigan pul: {reward} so'm\\n"
                f"👥 Limit: {limit} ta odam",
                reply_markup=admin_panel_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Xatolik yuz berdi. Balki bunday kod allaqachon bordir?",
                reply_markup=admin_panel_kb()
            )
        await state.clear()

    @router.callback_query(F.data.startswith("delpromo:"))
    async def del_promo(callback: CallbackQuery):
        promo_id = int(callback.data.split(":")[1])
        await delete_promocode(promo_id)
        
        promos = await get_all_promocodes()
        await callback.message.edit_text(
            "✅ Promo-kod o'chirildi.\\n\\n🎁 Qolgan kodlar ro'yxati:",
            reply_markup=promocodes_manage_kb(promos),
            parse_mode="HTML"
        )
'''

# insert before return router
content = content.replace('    return router', admin_promo_handlers + '\n    return router')

with open('master_bot/handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

