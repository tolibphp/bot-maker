from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database.users import get_user, get_all_users, get_users_count, update_balance
from database.bots import get_all_bots, get_bots_count, get_active_bots_count, get_all_active_bots, update_bot_status
from database.payments import get_total_revenue, get_today_revenue, add_payment
from master_bot.keyboards import admin_panel_kb, main_menu_kb
from master_bot.states import AdminAddBalanceStates, AdminBroadcastStates

router = Router()


def admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID:
            return
        return await func(message, *args, **kwargs)
    wrapper.__name__ = func.__name__
    # Preserve aiogram filter attributes
    if hasattr(func, '__wrapped__'):
        wrapper.__wrapped__ = func.__wrapped__
    return wrapper


@router.message(F.text == "👑 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "👑 <b>Admin Panel</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Statistika")
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users_count = await get_users_count()
    bots_count = await get_bots_count()
    active_bots = await get_active_bots_count()
    total_rev = await get_total_revenue()
    today_rev = await get_today_revenue()
    
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users_count}</b>\n"
        f"🤖 Jami botlar: <b>{bots_count}</b>\n"
        f"✅ Aktiv botlar: <b>{active_bots}</b>\n\n"
        f"💰 Jami daromad: <b>{total_rev:,} so'm</b>\n"
        f"📅 Bugungi daromad: <b>{today_rev:,} so'm</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.message(F.text == "👥 Foydalanuvchilar")
async def users_list(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = await get_all_users()
    if not users:
        await message.answer("👥 Foydalanuvchilar yo'q.", reply_markup=admin_panel_kb())
        return
    
    text = f"👥 <b>Foydalanuvchilar</b> ({len(users)} ta)\n\n"
    for u in users[:50]:  # limit to 50
        text += (
            f"🆔 <code>{u['telegram_id']}</code> — "
            f"{u['full_name'] or 'Nomsiz'} — "
            f"💰 {u['balance']:,} so'm\n"
        )
    
    await message.answer(text, reply_markup=admin_panel_kb(), parse_mode="HTML")


@router.message(F.text == "💰 Balans qo'shish")
async def add_balance_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "💰 <b>Balans qo'shish</b>\n\n"
        "Foydalanuvchi Telegram ID sini kiriting:",
        parse_mode="HTML"
    )
    await state.set_state(AdminAddBalanceStates.waiting_user_id)


@router.message(AdminAddBalanceStates.waiting_user_id)
async def add_balance_user_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    user = await get_user(user_id)
    if not user:
        await message.answer(
            "❌ Foydalanuvchi topilmadi.\n"
            "Bu ID bilan hech kim botga /start bosmagan.",
            reply_markup=admin_panel_kb()
        )
        await state.clear()
        return
    
    await state.update_data(target_user_id=user_id, target_user=user)
    await message.answer(
        f"👤 Foydalanuvchi: <b>{user['full_name']}</b>\n"
        f"💰 Joriy balans: <b>{user['balance']:,} so'm</b>\n\n"
        f"Qo'shiladigan summani kiriting (so'mda):",
        parse_mode="HTML"
    )
    await state.set_state(AdminAddBalanceStates.waiting_amount)


@router.message(AdminAddBalanceStates.waiting_amount)
async def add_balance_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        amount = int(message.text.strip().replace(",", "").replace(" ", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Noto'g'ri summa. Musbat raqam kiriting.")
        return
    
    data = await state.get_data()
    user_id = data["target_user_id"]
    
    await update_balance(user_id, amount)
    await add_payment(
        user_telegram_id=user_id,
        amount=amount,
        payment_type="deposit",
        description=f"Admin tomonidan qo'shildi"
    )
    
    # Notify user
    try:
        from aiogram import Bot
        bot = Bot.get_current()
        if bot:
            await bot.send_message(
                user_id,
                f"💰 Balansga <b>{amount:,} so'm</b> qo'shildi!\n"
                f"Admin tomonidan.",
                parse_mode="HTML"
            )
    except Exception:
        pass
    
    await message.answer(
        f"✅ <b>{amount:,} so'm</b> qo'shildi!\n"
        f"👤 {data['target_user']['full_name']} (ID: {user_id})",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(F.text == "📢 Broadcast")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n\n"
        "<i>Bekor qilish uchun 🔙 Orqaga bosing</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminBroadcastStates.waiting_message)


@router.message(AdminBroadcastStates.waiting_message)
async def broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = await get_all_users()
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await message.copy_to(user["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
    
    await message.answer(
        f"📢 <b>Broadcast yakunlandi!</b>\n\n"
        f"✅ Yuborildi: {sent}\n"
        f"❌ Xatolik: {failed}",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(F.text == "🔧 Barcha botlar")
async def all_bots(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    bots = await get_all_bots()
    if not bots:
        await message.answer("🤖 Hali bot yo'q.", reply_markup=admin_panel_kb())
        return
    
    text = f"🔧 <b>Barcha botlar</b> ({len(bots)} ta)\n\n"
    for b in bots[:50]:
        status_emoji = "✅" if b["status"] == "active" else "⛔"
        text += (
            f"{status_emoji} @{b['bot_username']} — "
            f"Egasi: <code>{b['owner_telegram_id']}</code> — "
            f"{b['template_type']}\n"
        )
    
    await message.answer(text, reply_markup=admin_panel_kb(), parse_mode="HTML")
