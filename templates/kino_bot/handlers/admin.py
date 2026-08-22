from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import (
    admin_main_kb, categories_select_kb, categories_manage_kb,
    channels_manage_kb, cancel_admin_kb, movie_pagination_kb
)
from templates.kino_bot.states import (
    AddMovieStates, AddCategoryStates, AddChannelStates,
    BroadcastStates, BanUserStates, DeleteMovieStates
)


def create_admin_router(kino_db: KinoDB, admin_id: int) -> Router:
    router = Router()

    def is_admin(message: Message) -> bool:
        return message.from_user.id == admin_id

    # --- Add Movie ---
    @router.message(F.text == "➕ Kino qo'shish")
    async def add_movie_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        await message.answer(
            "➕ <b>Kino qo'shish</b>\n\n"
            "Kino nomini kiriting:",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(AddMovieStates.waiting_name)

    @router.message(AddMovieStates.waiting_name)
    async def add_movie_name(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        await state.update_data(movie_name=message.text.strip())
        
        categories = await kino_db.get_categories()
        if not categories:
            await message.answer(
                "❌ Hali kategoriya qo'shilmagan!\n"
                "Avval 📂 Kategoriya boshqarish dan kategoriya qo'shing.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
            await state.clear()
            return
        
        await message.answer(
            "📂 Kategoriyani tanlang:",
            reply_markup=categories_select_kb(categories),
            parse_mode="HTML"
        )
        await state.set_state(AddMovieStates.waiting_category)

    @router.callback_query(F.data.startswith("selcat:"), AddMovieStates.waiting_category)
    async def add_movie_category(callback: CallbackQuery, state: FSMContext):
        cat_id = int(callback.data.split(":")[1])
        category = await kino_db.get_category(cat_id)
        await state.update_data(category_id=cat_id, category_name=category["name"] if category else "")
        
        await callback.message.edit_text(
            "📤 Endi kino faylini (video yoki dokument) yuboring:",
            parse_mode="HTML"
        )
        await state.set_state(AddMovieStates.waiting_file)

    @router.message(AddMovieStates.waiting_file, F.video | F.document)
    async def add_movie_file(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        
        if message.video:
            file_id = message.video.file_id
        elif message.document:
            file_id = message.document.file_id
        else:
            await message.answer("❌ Video yoki dokument yuboring.")
            return
        
        data = await state.get_data()
        caption = message.caption  # optional caption from the uploaded file
        
        code = await kino_db.add_movie(
            name=data["movie_name"],
            category_id=data["category_id"],
            file_id=file_id,
            caption=caption
        )
        
        await message.answer(
            f"✅ <b>Kino qo'shildi!</b>\n\n"
            f"🎬 Nomi: <b>{data['movie_name']}</b>\n"
            f"📂 Kategoriya: {data.get('category_name', '')}\n"
            f"📌 Kodi: <code>#{code}</code>",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.message(AddMovieStates.waiting_file)
    async def add_movie_file_invalid(message: Message):
        await message.answer("❌ Iltimos, video yoki dokument faylini yuboring.")

    # --- Movies List ---
    @router.message(F.text == "📋 Kinolar ro'yxati")
    async def movies_list(message: Message):
        if not is_admin(message):
            return
        
        total = await kino_db.get_movies_count()
        if total == 0:
            await message.answer("📋 Hali kino qo'shilmagan.")
            return
        
        per_page = 10
        total_pages = (total + per_page - 1) // per_page
        movies = await kino_db.get_all_movies(page=0, per_page=per_page)
        
        text = f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
        for m in movies:
            text += f"<code>#{m['code']}</code> — {m['name']} — 👁 {m['views']}\n"
        
        await message.answer(
            text,
            reply_markup=movie_pagination_kb(0, total_pages) if total_pages > 1 else None,
            parse_mode="HTML"
        )

    @router.callback_query(F.data.startswith("mpage:"))
    async def movies_page(callback: CallbackQuery):
        page = int(callback.data.split(":")[1])
        per_page = 10
        total = await kino_db.get_movies_count()
        total_pages = (total + per_page - 1) // per_page
        movies = await kino_db.get_all_movies(page=page, per_page=per_page)
        
        text = f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
        for m in movies:
            text += f"<code>#{m['code']}</code> — {m['name']} — 👁 {m['views']}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=movie_pagination_kb(page, total_pages),
            parse_mode="HTML"
        )

    # --- Delete Movie ---
    @router.message(F.text == "🗑 Kino o'chirish")
    async def delete_movie_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        await message.answer(
            "🗑 O'chiriladigan kino kodini kiriting (masalan: #0001):",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(DeleteMovieStates.waiting_code)

    @router.message(DeleteMovieStates.waiting_code)
    async def delete_movie_code(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        code = message.text.strip()
        movie = await kino_db.get_movie_by_code(code)
        if not movie:
            await message.answer("❌ Bu kodli kino topilmadi.")
            return
        
        await kino_db.delete_movie(code)
        await message.answer(
            f"✅ <b>{movie['name']}</b> (#{movie['code']}) o'chirildi.",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    # --- Category Management ---
    @router.message(F.text == "📂 Kategoriya boshqarish")
    async def manage_categories(message: Message):
        if not is_admin(message):
            return
        categories = await kino_db.get_categories()
        
        text = "📂 <b>Kategoriyalar</b>\n\n"
        if categories:
            for c in categories:
                text += f"• {c['name']}\n"
            text += "\nO'chirish uchun bosing. Yangi qo'shish uchun tugmani bosing."
        else:
            text += "Hali kategoriya yo'q."
        
        await message.answer(
            text,
            reply_markup=categories_manage_kb(categories),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_category")
    async def add_category_start(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📂 Yangi kategoriya nomini kiriting:",
            parse_mode="HTML"
        )
        await state.set_state(AddCategoryStates.waiting_name)

    @router.message(AddCategoryStates.waiting_name)
    async def add_category_name(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        name = message.text.strip()
        await kino_db.add_category(name)
        await message.answer(
            f"✅ Kategoriya <b>{name}</b> qo'shildi!",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.callback_query(F.data.startswith("delcat:"))
    async def delete_category(callback: CallbackQuery):
        cat_id = int(callback.data.split(":")[1])
        category = await kino_db.get_category(cat_id)
        await kino_db.delete_category(cat_id)
        await callback.message.edit_text(
            f"✅ Kategoriya <b>{category['name'] if category else ''}</b> o'chirildi.",
            parse_mode="HTML"
        )

    # --- Channel Management ---
    @router.message(F.text == "✅ Majburiy obuna")
    async def manage_channels(message: Message):
        if not is_admin(message):
            return
        channels = await kino_db.get_channels()
        
        text = "✅ <b>Majburiy obuna kanallari</b>\n\n"
        if channels:
            for ch in channels:
                text += f"📢 {ch['channel_name'] or ch['channel_id']}\n"
            text += "\nO'chirish uchun bosing."
        else:
            text += "Hali kanal qo'shilmagan."
        
        await message.answer(
            text,
            reply_markup=channels_manage_kb(channels),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_channel")
    async def add_channel_start(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📢 Kanal username ni kiriting\n"
            "Misol: <code>@mychannel</code>\n\n"
            "⚠️ Bot kanalda admin bo'lishi kerak!",
            parse_mode="HTML"
        )
        await state.set_state(AddChannelStates.waiting_channel)

    @router.message(AddChannelStates.waiting_channel)
    async def add_channel_name(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        channel_id = message.text.strip()
        
        # Try to get channel info
        try:
            chat = await message.bot.get_chat(channel_id)
            channel_name = chat.title
        except Exception:
            channel_name = channel_id
        
        await kino_db.add_channel(channel_id, channel_name)
        await message.answer(
            f"✅ Kanal <b>{channel_name}</b> qo'shildi!",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.callback_query(F.data.startswith("delch:"))
    async def delete_channel(callback: CallbackQuery):
        ch_id = int(callback.data.split(":")[1])
        await kino_db.delete_channel(ch_id)
        await callback.message.edit_text(
            "✅ Kanal o'chirildi.",
            parse_mode="HTML"
        )

    # --- Broadcast ---
    @router.message(F.text == "📢 Broadcast")
    async def broadcast_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        users_count = await kino_db.get_users_count()
        await message.answer(
            f"📢 <b>Broadcast</b>\n\n"
            f"Jami foydalanuvchilar: {users_count}\n"
            f"Xabarni yuboring (matn, rasm, video...):",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(BroadcastStates.waiting_message)

    @router.message(BroadcastStates.waiting_message)
    async def broadcast_send(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        
        users = await kino_db.get_all_users()
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
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    # --- Statistics ---
    @router.message(F.text == "📊 Statistika")
    async def show_stats(message: Message):
        if not is_admin(message):
            return
        
        users_count = await kino_db.get_users_count()
        today_users = await kino_db.get_today_users_count()
        movies_count = await kino_db.get_movies_count()
        categories = await kino_db.get_categories()
        channels = await kino_db.get_channels()
        
        await message.answer(
            f"📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{users_count}</b>\n"
            f"🆕 Bugungi yangi: <b>{today_users}</b>\n"
            f"🎬 Jami kinolar: <b>{movies_count}</b>\n"
            f"📂 Kategoriyalar: <b>{len(categories)}</b>\n"
            f"📢 Obuna kanallari: <b>{len(channels)}</b>",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )

    # --- Ban/Unban ---
    @router.message(F.text == "🚫 Ban / Unban")
    async def ban_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        await message.answer(
            "🚫 <b>Ban / Unban</b>\n\n"
            "Foydalanuvchi Telegram ID sini kiriting:\n"
            "(Ban qilish yoki bandan chiqarish)",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(BanUserStates.waiting_user_id)

    @router.message(BanUserStates.waiting_user_id)
    async def ban_user_id(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        
        try:
            user_id = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Noto'g'ri ID.")
            return
        
        user = await kino_db.get_user(user_id)
        if not user:
            await message.answer(
                "❌ Bu foydalanuvchi botdan foydalanmagan.",
                reply_markup=admin_main_kb()
            )
            await state.clear()
            return
        
        if user["is_banned"]:
            await kino_db.unban_user(user_id)
            await message.answer(
                f"✅ <b>{user['full_name']}</b> bandan chiqarildi.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
        else:
            await kino_db.ban_user(user_id)
            await message.answer(
                f"🚫 <b>{user['full_name']}</b> bloklandi.",
                reply_markup=admin_main_kb(),
                parse_mode="HTML"
            )
        await state.clear()

    # --- Cancel ---
    @router.callback_query(F.data == "cancel_admin")
    async def cancel_admin(callback: CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi.")
        await callback.message.answer(
            "👑 Admin Panel",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )

    return router
