from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import user_kb, subscription_kb, movie_share_kb
from templates.kino_bot.handlers.subscription import check_subscription, send_subscription_message


def create_user_router(kino_db: KinoDB, admin_id: int) -> Router:
    router = Router()

    async def _send_movie(message: Message, movie: dict, bot_username: str):
        """Send movie to user with share button."""
        await kino_db.increment_views(movie["id"])
        caption = (
            f"🎬 <b>{movie['name']}</b>\n\n"
            f"📌 Kod: <code>#{movie['code']}</code>\n"
            f"👁 Ko'rishlar: {movie['views'] + 1}"
        )
        if movie.get("caption"):
            caption += f"\n\n{movie['caption']}"

        share_kb = movie_share_kb(bot_username, movie["code"], movie["name"])

        try:
            await message.answer_video(
                movie["file_id"], caption=caption,
                reply_markup=share_kb, parse_mode="HTML"
            )
        except Exception:
            try:
                await message.answer_document(
                    movie["file_id"], caption=caption,
                    reply_markup=share_kb, parse_mode="HTML"
                )
            except Exception:
                await message.answer("❌ Faylni yuborishda xatolik yuz berdi.")

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

        # Check deep link (movie code from share/channel)
        text = message.text or ""
        if " " in text:
            code = text.split(" ", 1)[1].strip()
            movie = await kino_db.get_movie_by_code(code)
            if movie:
                bot_me = await message.bot.get_me()
                await message.answer(
                    "✅ Kino topildi!",
                    reply_markup=user_kb(),
                    parse_mode="HTML"
                )
                await _send_movie(message, movie, bot_me.username)
                return

        # Admin gets admin panel
        if message.from_user.id == admin_id:
            from templates.kino_bot.keyboards import admin_main_kb
            await message.answer(
                "👑 <b>Admin Panel</b>\n\n"
                "Salom, Admin! Botni boshqarish uchun tugmalardan foydalaning.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
            return

        # Professional user greeting
        name = message.from_user.full_name or message.from_user.username or "Foydalanuvchi"
        user_id = message.from_user.id

        await message.answer(
            f"👋 Assalomu alaykum "
            f"<a href='tg://user?id={user_id}'>{name}</a>, "
            f"botimizga xush kelibsiz!\n\n"
            f"✍🏻 <b>Kino kodini yuboring...</b>",
            reply_markup=user_kb(),
            parse_mode="HTML"
        )

    @router.message(F.text == "👤 User rejimi")
    async def user_mode(message: Message):
        if message.from_user.id != admin_id:
            return

        name = message.from_user.full_name or "Admin"
        user_id = message.from_user.id

        await message.answer(
            f"👋 Assalomu alaykum "
            f"<a href='tg://user?id={user_id}'>{name}</a>, "
            f"botimizga xush kelibsiz!\n\n"
            f"✍🏻 <b>Kino kodini yuboring...</b>\n\n"
            f"Admin panelga qaytish uchun /start bosing.",
            reply_markup=user_kb(),
            parse_mode="HTML"
        )

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
                user_id = callback.from_user.id

                await callback.message.answer(
                    f"👋 Assalomu alaykum "
                    f"<a href='tg://user?id={user_id}'>{name}</a>, "
                    f"botimizga xush kelibsiz!\n\n"
                    f"✍🏻 <b>Kino kodini yuboring...</b>",
                    reply_markup=user_kb(),
                    parse_mode="HTML"
                )
        else:
            await callback.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

    # --- 🔍 Kino qidirish button ---
    @router.message(F.text == "🔍 Kino qidirish")
    async def search_prompt(message: Message):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return

        await message.answer(
            "🔍 <b>Kino qidirish</b>\n\n"
            "✍🏻 Kino kodini yoki nomini yuboring:",
            parse_mode="HTML"
        )


    # --- Handle ANY text as movie code ---
    @router.message(F.text)
    async def handle_text(message: Message):
        # Skip admin commands
        if message.from_user.id == admin_id:
            admin_commands = [
                "➕ Kino qo'shish", "📋 Kinolar ro'yxati",
                "✅ Majburiy obuna", "📢 Post kanali",
                "📢 Broadcast", "📊 Statistika",
                "🚫 Ban / Unban", "👤 User rejimi",
                "📝 Post yaratish", "⚙️ Sozlamalar"
            ]
            if message.text in admin_commands:
                return

        # Check ban
        if await kino_db.is_banned(message.from_user.id):
            await message.answer("🚫 Siz bloklangansiz.")
            return

        # Check subscription
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return

        query = message.text.strip()
        bot_me = await message.bot.get_me()

        # Try as movie code first
        movie = await kino_db.get_movie_by_code(query)

        if movie:
            await _send_movie(message, movie, bot_me.username)
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
