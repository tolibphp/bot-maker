from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import (
    user_main_kb, admin_main_kb, categories_kb,
    movie_pagination_kb, subscription_kb
)
from templates.kino_bot.states import SearchStates
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
        
        if message.from_user.id == admin_id:
            await message.answer(
                "👑 <b>Admin Panel</b>\n\n"
                "Salom, Admin! Botni boshqarish uchun quyidagi tugmalardan foydalaning.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "🎬 <b>Kino Botga xush kelibsiz!</b>\n\n"
                "Kino kodini yuboring yoki quyidagi tugmalardan foydalaning.",
                reply_markup=user_main_kb(),
                parse_mode="HTML"
            )

    @router.message(F.text == "👤 User rejimi")
    async def user_mode(message: Message):
        if message.from_user.id != admin_id:
            return
        await message.answer(
            "👤 User rejimiga o'tdingiz.\n"
            "Admin panelga qaytish uchun /start bosing.",
            reply_markup=user_main_kb(),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "check_sub")
    async def check_sub_callback(callback: CallbackQuery):
        if await check_subscription(callback.bot, callback.from_user.id, kino_db):
            await callback.message.delete()
            if callback.from_user.id == admin_id:
                await callback.message.answer(
                    "👑 Admin Panel",
                    reply_markup=admin_main_kb(),
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer(
                    "✅ Obuna tasdiqlandi!\n🎬 Kino kodini yuboring yoki quyidagi tugmalardan foydalaning.",
                    reply_markup=user_main_kb(),
                    parse_mode="HTML"
                )
        else:
            await callback.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

    # --- Search ---
    @router.message(F.text == "🔍 Qidirish")
    async def search_start(message: Message, state: FSMContext):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return
        await message.answer(
            "🔍 Kino nomi yoki kodini kiriting:",
            parse_mode="HTML"
        )
        await state.set_state(SearchStates.waiting_query)

    @router.message(SearchStates.waiting_query)
    async def search_query(message: Message, state: FSMContext):
        await state.clear()
        query = message.text.strip()
        
        # Check if it's a code
        if query.startswith("#") or query.isdigit():
            movie = await kino_db.get_movie_by_code(query)
            if movie:
                await kino_db.increment_views(movie["id"])
                caption = f"🎬 <b>{movie['name']}</b>\n\n📌 Kod: #{movie['code']}\n👁 Ko'rishlar: {movie['views'] + 1}"
                if movie.get("caption"):
                    caption += f"\n\n{movie['caption']}"
                try:
                    await message.answer_video(movie["file_id"], caption=caption, parse_mode="HTML")
                except Exception:
                    await message.answer_document(movie["file_id"], caption=caption, parse_mode="HTML")
            else:
                await message.answer("❌ Kino topilmadi.")
            return
        
        # Search by name
        movies = await kino_db.search_movies(query)
        if not movies:
            await message.answer("❌ Hech narsa topilmadi.")
            return
        
        text = f"🔍 <b>Qidiruv natijalari:</b> \"{query}\"\n\n"
        for m in movies:
            text += f"🎬 <b>{m['name']}</b> — Kod: <code>#{m['code']}</code>\n"
        text += "\n📌 Kodni yuboring yoki bosing."
        
        await message.answer(text, parse_mode="HTML")

    # --- Handle direct code/number input (without search state) ---
    @router.message(F.text.regexp(r'^#?\d{1,}$'))
    async def direct_code(message: Message):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return
        
        code = message.text.strip()
        movie = await kino_db.get_movie_by_code(code)
        if movie:
            await kino_db.increment_views(movie["id"])
            caption = f"🎬 <b>{movie['name']}</b>\n\n📌 Kod: #{movie['code']}\n👁 Ko'rishlar: {movie['views'] + 1}"
            if movie.get("caption"):
                caption += f"\n\n{movie['caption']}"
            try:
                await message.answer_video(movie["file_id"], caption=caption, parse_mode="HTML")
            except Exception:
                await message.answer_document(movie["file_id"], caption=caption, parse_mode="HTML")
        else:
            await message.answer("❌ Bu kodli kino topilmadi.")

    # --- Categories ---
    @router.message(F.text == "📂 Kategoriyalar")
    async def show_categories(message: Message):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return
        
        categories = await kino_db.get_categories()
        if not categories:
            await message.answer("📂 Hali kategoriya qo'shilmagan.")
            return
        
        await message.answer(
            "📂 <b>Kategoriyalar</b>\n\nBirini tanlang:",
            reply_markup=categories_kb(categories),
            parse_mode="HTML"
        )

    @router.callback_query(F.data.startswith("cat:"))
    async def category_movies(callback: CallbackQuery):
        cat_id = int(callback.data.split(":")[1])
        category = await kino_db.get_category(cat_id)
        movies = await kino_db.get_movies_by_category(cat_id)
        
        if not movies:
            await callback.answer("Bu kategoriyada kino yo'q.", show_alert=True)
            return
        
        text = f"📂 <b>{category['name'] if category else 'Kategoriya'}</b>\n\n"
        for m in movies[:20]:
            text += f"🎬 <b>{m['name']}</b> — <code>#{m['code']}</code>\n"
        
        await callback.message.edit_text(text, parse_mode="HTML")

    # --- Recent & Top ---
    @router.message(F.text == "🔥 So'nggi kinolar")
    async def recent_movies(message: Message):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return
        
        movies = await kino_db.get_recent_movies(10)
        if not movies:
            await message.answer("🔥 Hali kino qo'shilmagan.")
            return
        
        text = "🔥 <b>So'nggi qo'shilgan kinolar:</b>\n\n"
        for m in movies:
            text += f"🎬 <b>{m['name']}</b> — <code>#{m['code']}</code>\n"
        text += "\n📌 Kodini yuboring."
        
        await message.answer(text, parse_mode="HTML")

    @router.message(F.text == "📊 Top kinolar")
    async def top_movies(message: Message):
        if await kino_db.is_banned(message.from_user.id):
            return
        if not await check_subscription(message.bot, message.from_user.id, kino_db):
            await send_subscription_message(message, kino_db)
            return
        
        movies = await kino_db.get_top_movies(10)
        if not movies:
            await message.answer("📊 Hali kino yo'q.")
            return
        
        text = "📊 <b>Eng ko'p ko'rilgan kinolar:</b>\n\n"
        for i, m in enumerate(movies, 1):
            text += f"{i}. 🎬 <b>{m['name']}</b> — 👁 {m['views']} — <code>#{m['code']}</code>\n"
        text += "\n📌 Kodini yuboring."
        
        await message.answer(text, parse_mode="HTML")

    return router
