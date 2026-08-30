from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.music_bot.keyboards import admin_main_kb, user_main_kb, subscription_kb, MUSIC_EMOJI

def create_start_router(db, admin_id: int):
    router = Router()
    
    async def check_sub(bot, user_id: int):
        if user_id == admin_id:
            return True
        channels = await db.get_channels()
        if not channels:
            return True
        for ch in channels:
            try:
                member = await bot.get_chat_member(ch["channel_id"], user_id)
                if member.status in ['left', 'kicked', 'restricted']:
                    return False
            except Exception:
                return False
        return True

    @router.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        is_sub = await check_sub(message.bot, message.from_user.id)
        if not is_sub:
            channels = await db.get_channels()
            await message.answer(
                "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=subscription_kb(channels)
            )
            return

        if message.from_user.id == admin_id:
            await message.answer(
                f"{MUSIC_EMOJI} <b>Admin Panelga xush kelibsiz!</b>",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"{MUSIC_EMOJI} <b>VK Music Bot</b> ga xush kelibsiz!\n\n"
                f"Qo'shiq yoki san'atkor nomini yuboring yoki quyidagi tugmani bosing:",
                reply_markup=user_main_kb(),
                parse_mode="HTML"
            )

    @router.callback_query(F.data == "check_sub")
    async def check_sub_cb(callback: CallbackQuery):
        is_sub = await check_sub(callback.bot, callback.from_user.id)
        if not is_sub:
            await callback.answer("❌ Hali hamma kanallarga a'zo bo'lmadingiz!", show_alert=True)
            return
            
        await callback.message.delete()
        if callback.from_user.id == admin_id:
            await callback.message.answer("✅ Obuna tasdiqlandi!", reply_markup=admin_main_kb())
        else:
            await callback.message.answer(
                f"{MUSIC_EMOJI} <b>Obuna tasdiqlandi!</b>\n\nEndi qidirishingiz mumkin:",
                reply_markup=user_main_kb(),
                parse_mode="HTML"
            )

    return router
