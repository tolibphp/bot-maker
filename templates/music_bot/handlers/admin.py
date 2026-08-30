from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
import asyncio

from templates.music_bot.keyboards import admin_main_kb, cancel_admin_kb, channels_manage_kb
from templates.music_bot.states import BroadcastStates, AddChannelStates

def create_admin_router(db, admin_id: int):
    router = Router()

    def is_admin(message: Message) -> bool:
        return message.from_user.id == admin_id

    @router.message(F.text == "📊 Statistika")
    async def cmd_stats(message: Message):
        if not is_admin(message): return
        count = await db.get_users_count()
        await message.answer(
            f"📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchilar: {count} ta",
            parse_mode="HTML"
        )

    @router.message(F.text == "✅ Majburiy obuna")
    async def cmd_channels(message: Message):
        if not is_admin(message): return
        channels = await db.get_channels()
        await message.answer(
            "📢 <b>Majburiy obuna kanallari:</b>",
            reply_markup=channels_manage_kb(channels),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_channel")
    async def cb_add_channel(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id != admin_id: return
        await callback.message.edit_text(
            "Kanal ID si yoki Usernameni kiriting (masalan: @kanal_username yoki -100123...):\n\n"
            "⚠️ Eslatma: Bot kanalda admin bo'lishi shart!"
        )
        await state.set_state(AddChannelStates.waiting_channel)

    @router.message(AddChannelStates.waiting_channel)
    async def process_add_channel(message: Message, state: FSMContext):
        if not is_admin(message): return
        channel_id = message.text.strip()
        try:
            chat = await message.bot.get_chat(channel_id)
            await db.add_channel(str(chat.id), chat.title)
            await message.answer(f"✅ {chat.title} kanali qo'shildi!", reply_markup=admin_main_kb())
        except Exception:
            await message.answer("❌ Kanal topilmadi yoki bot admin emas!", reply_markup=admin_main_kb())
        await state.clear()

    @router.callback_query(F.data.startswith("delch:"))
    async def cb_del_channel(callback: CallbackQuery):
        if callback.from_user.id != admin_id: return
        ch_id = int(callback.data.split(":")[1])
        await db.delete_channel(ch_id)
        channels = await db.get_channels()
        await callback.message.edit_text("✅ Kanal o'chirildi.", reply_markup=channels_manage_kb(channels))

    @router.message(F.text == "📢 Broadcast")
    async def cmd_broadcast(message: Message, state: FSMContext):
        if not is_admin(message): return
        await message.answer("Xabarni yuboring:", reply_markup=cancel_admin_kb())
        await state.set_state(BroadcastStates.waiting_message)

    @router.message(F.text == "❌ Bekor qilish")
    async def cmd_cancel(message: Message, state: FSMContext):
        if not is_admin(message): return
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_kb())

    @router.message(BroadcastStates.waiting_message)
    async def process_broadcast(message: Message, state: FSMContext):
        if not is_admin(message): return
        users = await db.get_all_users()
        await message.answer(f"⏳ Xabar yuborish boshlandi... (Jami {len(users)} ta)", reply_markup=admin_main_kb())
        await state.clear()
        
        success = 0
        for u in users:
            try:
                await message.copy_to(u["telegram_id"])
                success += 1
                await asyncio.sleep(0.05)
            except TelegramAPIError:
                pass
        
        await message.answer(f"✅ Xabar {success} kishiga muvaffaqiyatli yetkazildi.")

    return router
