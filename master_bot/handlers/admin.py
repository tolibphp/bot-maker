from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from database.users import get_users_count, get_all_users
from database.bots import get_all_bots
from database.payments import add_payment
from master_bot.keyboards import admin_panel_kb, promocodes_manage_kb, back_kb
from master_bot.states import AdminAddBalanceStates, PromocodeStates, AdminBroadcastStates, AddChannelStates
from master_bot.emojis import CROWN, CHART, PEOPLE, HORN, WRENCH, MONEY, CROSS, CHECK, DOWN, PROMO_GIFT

router = Router()

@router.message(F.text == "Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"{CROWN} <b>Admin Panel</b>\n\n"
        f"Xush kelibsiz, xo'jayin! Nimani ko'rmoqchisiz?",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"📊 Statistika", "Statistika"}))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    users_count = await get_users_count()
    bots = await get_all_bots()
    bots_count = len(bots)
    active_bots = sum(1 for b in bots if b["status"] == "active")

    await message.answer(
        f"{CHART} <b>Umumiy statistika</b>\n\n"
        f"<blockquote>{PEOPLE} Foydalanuvchilar: <b>{users_count}</b> ta\n"
        f"{WRENCH} Jami botlar: <b>{bots_count}</b> ta\n"
        f"{CHECK} Faol botlar: <b>{active_bots}</b> ta</blockquote>",
        parse_mode="HTML"
    )

@router.message(F.text.in_({"👥 Foydalanuvchilar", "Foydalanuvchilar"}))
async def show_users_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    count = await get_users_count()
    await message.answer(f"{PEOPLE} Botdagi jami foydalanuvchilar soni: <b>{count}</b> ta", parse_mode="HTML")

@router.message(lambda msg: msg.entities and any(e.type == "custom_emoji" for e in msg.entities))
async def catch_premium_emoji(message: Message):
    if message.from_user.id != int(ADMIN_ID):
        return
        
    custom_emojis = []
    if message.entities:
        for ent in message.entities:
            if ent.type == "custom_emoji":
                emoji_char = message.text[ent.offset : ent.offset + ent.length]
                custom_emojis.append((emoji_char, ent.custom_emoji_id))
                
    if custom_emojis:
        text = "✨ <b>Premium Emoji ID lari topildi:</b>\n\n"
        for char, eid in custom_emojis:
            text += f"Emoji: {char}\nKod: <code>&lt;tg-emoji emoji-id=\"{eid}\"&gt;{char}&lt;/tg-emoji&gt;</code>\n\n"
        text += "Ushbu kodlarni nusxalab menga yuboring, men kodlarga joylab chiqaman!"
        await message.answer(text, parse_mode="HTML")

@router.message(F.text.in_({"💰 Balans qo'shish", "Balans qo'shish"}))
async def add_balance_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"{MONEY} Foydalanuvchi ID raqamini kiriting:")
    await state.set_state(AdminAddBalanceStates.waiting_user_id)

@router.message(AdminAddBalanceStates.waiting_user_id)
async def process_user_id_balance(message: Message, state: FSMContext):
    try:
        uid = int(message.text.strip())
        await state.update_data(target_id=uid)
        await message.answer(f"{DOWN} Qancha summa qo'shmoqchisiz?\n(Ayirish uchun manfiy son yozing, masalan -50000)")
        await state.set_state(AdminAddBalanceStates.waiting_amount)
    except ValueError:
        await message.answer(f"{CROSS} Noto'g'ri ID. Raqam kiriting:")

@router.message(AdminAddBalanceStates.waiting_amount)
async def process_amount_balance(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        data = await state.get_data()
        target_id = data['target_id']
        
        from database.users import update_balance, get_user
        user = await get_user(target_id)
        if not user:
            await message.answer(f"{CROSS} Foydalanuvchi topilmadi!", parse_mode="HTML")
            await state.clear()
            return
            
        await update_balance(target_id, amount)
        
        await add_payment(
            user_telegram_id=target_id,
            amount=amount,
            payment_type="admin_bonus" if amount > 0 else "admin_penalty",
            description="Admin tomonidan balans o'zgartirildi"
        )
        
        await message.answer(f"{CHECK} Balans muvaffaqiyatli o'zgartirildi!", parse_mode="HTML")
        await state.clear()
        
        # Notify user
        try:
            await message.bot.send_message(
                target_id,
                f"{MONEY} <b>Admin tomonidan balans o'zgartirildi:</b>\n\n"
                f"Miqdor: {'+' if amount > 0 else ''}{amount:,} so'm\n"
                f"Hozirgi balans: {user['balance'] + amount:,} so'm",
                parse_mode="HTML"
            )
        except Exception:
            pass
            
    except ValueError:
        await message.answer(f"{CROSS} Noto'g'ri summa. Raqam kiriting:")
    
    await state.clear()

@router.message(F.text.in_({"📢 Broadcast", "Broadcast"}))
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"{HORN} <b>Xabar yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni kiriting (yoki Bekor qilish ni bosing):",
        reply_markup=back_kb(),
        parse_mode="HTML"
    )
    await state.set_state(AdminBroadcastStates.waiting_message)

@router.message(AdminBroadcastStates.waiting_message)
async def broadcast_send(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await admin_panel(message)
        return

    users = await get_all_users()
    sent = 0
    failed = 0
    for u in users:
        try:
            await message.copy_to(u["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
            
    await message.answer(
        f"{CHECK} <b>Xabar yuborildi!</b>\n\n"
        f"Muvaffaqiyatli: {sent}\nBloklaganlar: {failed}",
        parse_mode="HTML"
    )
    await state.clear()
    await admin_panel(message)

@router.message(F.text.in_({"🔧 Barcha botlar", "Barcha botlar"}))
async def admin_all_bots(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    bots = await get_all_bots()
    if not bots:
        await message.answer(f"{WRENCH} Hozircha tizimda botlar yo'q.", parse_mode="HTML")
        return
        
    text = f"{WRENCH} <b>Barcha yaratilgan botlar:</b>\n\n"
    
    for i, bot in enumerate(bots, 1):
        username = bot.get("bot_username", "Noma'lum")
        template = bot.get("template_type", "Noma'lum")
        status = bot.get("status", "unknown")
        
        status_emoji = CHECK if status == "active" else CROSS
        text += f"{i}. <b>@{username}</b> | Shablon: <i>{template}</i> | Holat: {status_emoji} {status}\n"
        
        if i % 30 == 0:
            await message.answer(text, parse_mode="HTML")
            text = ""
            
    if text:
        await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data.startswith("pay_approve:"))
async def approve_payment(callback: CallbackQuery):
    _, user_id_str, amount_str = callback.data.split(":")
    user_id = int(user_id_str)
    amount = int(amount_str)

    from database.users import update_balance
    await update_balance(user_id, amount)
    
    await add_payment(
        user_telegram_id=user_id,
        amount=amount,
        payment_type="deposit",
        description="Balans to'ldirildi"
    )

    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{CHECK} <b>TASDIQLANDI</b>",
        parse_mode="HTML"
    )
    
    try:
        await callback.bot.send_message(
            user_id, 
            f"{CHECK} <b>To'lov tasdiqlandi!</b>\n\nBalansingizga {amount:,} so'm qo'shildi.", 
            parse_mode="HTML"
        )
    except:
        pass

@router.callback_query(F.data.startswith("pay_reject:"))
async def reject_payment(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{CROSS} <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )

    try:
        await callback.bot.send_message(
            user_id, 
            f"{CROSS} To'lov chekingiz admin tomonidan rad etildi.\n\nSavollar bo'lsa adminga murojaat qiling.", 
            parse_mode="HTML"
        )
    except:
        pass

# ==========================================
#  ✅ MAJBURIY OBUNA (Kanal qo'shish/o'chirish)
# ==========================================
@router.message(F.text == "Majburiy obuna")
async def manage_sub_channels(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    from database.channels import get_channels
    from master_bot.keyboards import channels_manage_kb
    
    channels = await get_channels()

    text = (
        "✅ <b>Majburiy obuna (Master Bot)</b>\n\n"
        "Bu kanallar foydalanuvchi Master botdan foydalanish uchun\n"
        "<b>obuna bo'lishi shart</b> bo'lgan kanallar.\n\n"
    )
    if channels:
        text += "<b>Qo'shilgan kanallar:</b>\n"
        for ch in channels:
            text += f"✅ {ch['channel_name'] or ch['channel_id']}\n"
        text += "\nO'chirish uchun bosing 👇"
    else:
        text += "⚠️ Majburiy obuna yo'q.\nUser tekshiruvsiz foydalanadi."

    await message.answer(
        text,
        reply_markup=channels_manage_kb(channels),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    from master_bot.states import AddChannelStates
    await callback.message.edit_text(
        "✅ <b>Majburiy obuna kanal qo'shish</b>\n\n"
        "Kanal username ni kiriting:\n"
        "Misol: <code>@mychannel</code>\n\n"
        "⚠️ Bot kanalda admin bo'lishi kerak!",
        parse_mode="HTML"
    )
    await state.set_state(AddChannelStates.waiting_channel)

@router.message(AddChannelStates.waiting_channel)
async def add_channel_save(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    from database.channels import add_channel
    channel_id = message.text.strip()
    try:
        chat = await message.bot.get_chat(channel_id)
        channel_name = chat.title
    except Exception:
        channel_name = channel_id

    await add_channel(channel_id, channel_name)
    
    from master_bot.keyboards import admin_panel_kb
    await message.answer(
        f"✅ <b>{channel_name}</b> majburiy obunaga qo'shildi!",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data.startswith("delch:"))
async def delete_sub_channel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    from database.channels import delete_channel, get_channels
    from master_bot.keyboards import channels_manage_kb
    
    ch_id = int(callback.data.split(":")[1])
    await delete_channel(ch_id)
    
    channels = await get_channels()
    text = "✅ Kanal o'chirildi.\n\n"
    if channels:
        for ch in channels:
            text += f"✅ {ch['channel_name'] or ch['channel_id']}\n"
    else:
        text += "⚠️ Majburiy obuna kanallar yo'q."
        
    await callback.message.edit_text(
        text, reply_markup=channels_manage_kb(channels), parse_mode="HTML"
    )
from database.promocodes import create_promocode, get_all_promocodes, delete_promocode

# ==========================================
#  PROMOCODES (Admin)
# ==========================================
@router.message(F.text == "Promo-kodlar")
async def manage_promocodes(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    promos = await get_all_promocodes()
    text = "🎁 <b>Promo-kodlar</b>\n\n"
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
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text(
        "🎁 <b>Yangi Promo-kod</b>\n\n"
        "Kod nomini kiriting (faqat harf va raqamlar, probelsiz):\n"
        "Masalan: <code>YANGIYIL</code>",
        parse_mode="HTML"
    )
    await state.set_state(PromocodeStates.waiting_code)

@router.message(PromocodeStates.waiting_code)
async def add_promo_code(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
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
    if message.from_user.id != ADMIN_ID:
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
    if message.from_user.id != ADMIN_ID:
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
            f"✅ <b>Promo-kod yaratildi!</b>\n\n"
            f"🎁 Kod: <code>{code}</code>\n"
            f"💸 Beriladigan pul: {reward} so'm\n"
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
    if callback.from_user.id != ADMIN_ID:
        return
    promo_id = int(callback.data.split(":")[1])
    await delete_promocode(promo_id)
    
    promos = await get_all_promocodes()
    await callback.message.edit_text(
        "✅ Promo-kod o'chirildi.\n\n🎁 Qolgan kodlar ro'yxati:",
        reply_markup=promocodes_manage_kb(promos),
        parse_mode="HTML"
    )

