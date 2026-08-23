from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import channel_link_kb, subscription_kb
from templates.kino_bot.handlers.subscription import check_subscription, send_subscription_message


def create_user_router(kino_db: KinoDB, admin_id: int) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        await kino_db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )

        # Check ban
        if await kino_db.is_banned(message.from_user.id):
            await message.answer("🚫 Siz bloklangansiz.")
            return

        # Check subscription
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return

        # Admin gets admin panel
        if message.from_user.id == admin_id:
            from templates.kino_bot.keyboards import admin_main_kb
            await message.answer(
                "👑 <b>Admin Panel</b>\n\n"
                "Salom, Admin! Botni boshqarish uchun quyidagi tugmalardan foydalaning.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
            return

        # Professional user greeting — minimal, clean
        name = message.from_user.full_name or message.from_user.username or "Foydalanuvchi"
        movies_count = await kino_db.get_movies_count()

        channels = await kino_db.get_channels()
        kb = channel_link_kb(channels) if channels else None

        await message.answer(
            f"👋 Assalomu alaykum <b>{name}</b>, "
            f"botimizga xush kelibsiz!\n\n"
            f"🎬 Botimizda <b>{movies_count}</b> ta kino mavjud.\n\n"
            f"✍🏻 <b>Kino kodini yuboring...</b>",
            reply_markup=kb,
            parse_mode="HTML"
        )

    @router.message(F.text == "👤 User rejimi")
    async def user_mode(message: Message):
        if message.from_user.id != admin_id:
            return

        name = message.from_user.full_name or "Admin"
        movies_count = await kino_db.get_movies_count()
        channels = await kino_db.get_channels()
        kb = channel_link_kb(channels) if channels else None

        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            f"👋 Assalomu alaykum <b>{name}</b>, "
            f"botimizga xush kelibsiz!\n\n"
            f"🎬 Botimizda <b>{movies_count}</b> ta kino mavjud.\n\n"
            f"✍🏻 <b>Kino kodini yuboring...</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        if kb:
            await message.answer("👇", reply_markup=kb)

    @router.callback_query(F.data == "check_sub")
    async def check_sub_callback(callback: CallbackQuery):
        if await check_subscription(callback.bot, callback.from_user.id, kino_db):
            await callback.message.delete()

            if callback.from_user.id == admin_id:
                from templates.kino_bot.keyboards import admin_main_kb
                await callback.message.answer(
                    "👑 Admin Panel",
                    reply_markup=admin_main_kb(),
                    parse_mode="HTML"
                )
            else:
                name = callback.from_user.full_name or "Foydalanuvchi"
                movies_count = await kino_db.get_movies_count()
                channels = await kino_db.get_channels()
                kb = channel_link_kb(channels) if channels else None

                await callback.message.answer(
                    f"👋 Assalomu alaykum <b>{name}</b>, "
                    f"botimizga xush kelibsiz!\n\n"
                    f"🎬 Botimizda <b>{movies_count}</b> ta kino mavjud.\n\n"
                    f"✍🏻 <b>Kino kodini yuboring...</b>",
                    reply_markup=kb,
                    parse_mode="HTML"
                )
        else:
            await callback.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

    # --- Handle ANY text as movie code ---
    @router.message(F.text)
    async def handle_text(message: Message):
        # Skip admin commands
        if message.from_user.id == admin_id:
            # Don't intercept admin panel button presses
            admin_commands = [
                "➕ Kino qo'shish", "📋 Kinolar ro'yxati",
                "📁 Kategoriya boshqarish", "✅ Majburiy obuna",
                "📢 Broadcast", "📊 Statistika",
                "🚫 Ban / Unban", "👤 User rejimi"
            ]
            if message.text in admin_commands:
                return  # Let admin router handle it

        # Check ban
        if await kino_db.is_banned(message.from_user.id):
            await message.answer("🚫 Siz bloklangansiz.")
            return

        # Check subscription
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return

        query = message.text.strip()

        # Try as movie code first
        movie = await kino_db.get_movie_by_code(query)

        if movie:
            await kino_db.increment_views(movie["id"])
            caption = (
                f"🎬 <b>{movie['name']}</b>\n\n"
                f"📌 Kod: <code>#{movie['code']}</code>\n"
                f"👁 Ko'rishlar: {movie['views'] + 1}"
            )
            if movie.get("caption"):
                caption += f"\n\n{movie['caption']}"

            try:
                await message.answer_video(movie["file_id"], caption=caption, parse_mode="HTML")
            except Exception:
                try:
                    await message.answer_document(movie["file_id"], caption=caption, parse_mode="HTML")
                except Exception:
                    await message.answer(f"❌ Faylni yuborishda xatolik yuz berdi.")
        else:
            # Try search by name
            results = await kino_db.search_movies(query, limit=5)
            if results:
                text = f"🔍 <b>Natijalar:</b> \"{query}\"\n\n"
                for m in results:
                    text += f"🎬 <b>{m['name']}</b> — <code>#{m['code']}</code>\n"
                text += "\n✍🏻 Kodini yuboring."
                await message.answer(text, parse_mode="HTML")
            else:
                await message.answer(
                    "❌ <b>Kino topilmadi.</b>\n\n"
                    "✍🏻 To'g'ri kino kodini yuboring.",
                    parse_mode="HTML"
                )

    return router
