import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.kino_bot.database import KinoDB
from templates.kino_bot.keyboards import (
    admin_main_kb, channels_manage_kb, bot_channels_manage_kb,
    cancel_admin_kb, movie_list_kb, confirm_delete_kb, channel_post_kb
)
from templates.kino_bot.states import (
    AddMovieStates, AddChannelStates, AddBotChannelStates,
    BroadcastStates, BanUserStates, CreatePostStates, SettingsStates
)

logger = logging.getLogger(__name__)


def create_admin_router(kino_db: KinoDB, admin_id: int) -> Router:
    router = Router()

    def is_admin(message: Message) -> bool:
        return message.from_user.id == admin_id

    # ==========================================
    #  ➕ KINO QO'SHISH (Nom → Video → Tayyor!)
    # ==========================================

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
        await message.answer(
            "📤 Kino faylini yuboring (video yoki dokument):",
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
        caption = message.caption

        code = await kino_db.add_movie(
            name=data["movie_name"],
            category_id=None,
            file_id=file_id,
            caption=caption
        )

        await message.answer(
            f"✅ <b>Kino qo'shildi!</b>\n\n"
            f"🎬 Nomi: <b>{data['movie_name']}</b>\n"
            f"📌 Kodi: <code>#{code}</code>",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )

        await state.clear()

    @router.message(AddMovieStates.waiting_file)
    async def add_movie_file_invalid(message: Message):
        await message.answer("❌ Iltimos, video yoki dokument faylini yuboring.")

    # ==========================================
    #  📋 KINOLAR RO'YXATI
    # ==========================================

    @router.message(F.text == "📋 Kinolar ro'yxati")
    async def movies_list(message: Message):
        if not is_admin(message):
            return

        total = await kino_db.get_movies_count()
        if total == 0:
            await message.answer("📋 Hali kino qo'shilmagan.")
            return

        per_page = 8
        total_pages = (total + per_page - 1) // per_page
        movies = await kino_db.get_all_movies(page=0, per_page=per_page)

        await message.answer(
            f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
            f"O'chirish uchun 🗑 bosing:",
            reply_markup=movie_list_kb(movies, 0, total_pages),
            parse_mode="HTML"
        )

    @router.callback_query(F.data.startswith("mpage:"))
    async def movies_page(callback: CallbackQuery):
        page = int(callback.data.split(":")[1])
        per_page = 8
        total = await kino_db.get_movies_count()
        total_pages = (total + per_page - 1) // per_page
        movies = await kino_db.get_all_movies(page=page, per_page=per_page)

        await callback.message.edit_text(
            f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
            f"O'chirish uchun 🗑 bosing:",
            reply_markup=movie_list_kb(movies, page, total_pages),
            parse_mode="HTML"
        )

    @router.callback_query(F.data.startswith("delmovie:"))
    async def delete_movie_inline(callback: CallbackQuery):
        code = callback.data.split(":")[1]
        movie = await kino_db.get_movie_by_code(code)
        if not movie:
            await callback.answer("Kino topilmadi!", show_alert=True)
            return
        await callback.message.edit_text(
            f"🗑 <b>{movie['name']}</b> (#{movie['code']}) ni o'chirmoqchimisiz?",
            reply_markup=confirm_delete_kb(code),
            parse_mode="HTML"
        )

    @router.callback_query(F.data.startswith("confirm_del:"))
    async def confirm_delete_movie(callback: CallbackQuery):
        code = callback.data.split(":")[1]
        movie = await kino_db.get_movie_by_code(code)
        if movie:
            await kino_db.delete_movie(code)
            await callback.message.edit_text(
                f"✅ <b>{movie['name']}</b> (#{code}) o'chirildi.",
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text("❌ Kino topilmadi.")

    @router.callback_query(F.data == "cancel_del")
    async def cancel_delete(callback: CallbackQuery):
        await callback.message.delete()

    # ==========================================
    #  ✅ MAJBURIY OBUNA (faqat tekshirish uchun)
    # ==========================================

    @router.message(F.text == "✅ Majburiy obuna")
    async def manage_sub_channels(message: Message):
        if not is_admin(message):
            return
        channels = await kino_db.get_channels()

        text = (
            "✅ <b>Majburiy obuna</b>\n\n"
            "Bu kanallar foydalanuvchi botdan foydalanish uchun\n"
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
        if not is_admin(message):
            return
        channel_id = message.text.strip()
        try:
            chat = await message.bot.get_chat(channel_id)
            channel_name = chat.title
        except Exception:
            channel_name = channel_id

        await kino_db.add_channel(channel_id, channel_name)
        await message.answer(
            f"✅ <b>{channel_name}</b> majburiy obuna ga qo'shildi!",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.callback_query(F.data.startswith("delch:"))
    async def delete_sub_channel(callback: CallbackQuery):
        ch_id = int(callback.data.split(":")[1])
        await kino_db.delete_channel(ch_id)
        channels = await kino_db.get_channels()
        text = "✅ Kanal o'chirildi.\n\n"
        if channels:
            for ch in channels:
                text += f"✅ {ch['channel_name'] or ch['channel_id']}\n"
        else:
            text += "⚠️ Majburiy obuna kanallar yo'q."
        await callback.message.edit_text(
            text, reply_markup=channels_manage_kb(channels), parse_mode="HTML"
        )

    # ==========================================
    #  📢 BOT KANALI (Kanalimiz tugmasi + avto-post)
    # ==========================================

    @router.message(F.text == "📢 Post kanali")
    async def manage_bot_channels(message: Message):
        if not is_admin(message):
            return
        channels = await kino_db.get_bot_channels()

        text = (
            "📢 <b>Bot kanali</b>\n\n"
            "Bu kanal:\n"
            "📢 «Kanalimiz» tugmasida ko'rsatiladi\n"
            "📤 Yangi kino avtomatik post qilinadi\n\n"
        )
        if channels:
            text += "<b>Qo'shilgan kanallar:</b>\n"
            for ch in channels:
                text += f"📢 {ch['channel_name'] or ch['channel_id']}\n"
            text += "\nO'chirish uchun bosing 👇"
        else:
            text += "⚠️ Hali kanal qo'shilmagan."

        await message.answer(
            text,
            reply_markup=bot_channels_manage_kb(channels),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_bot_channel")
    async def add_bot_channel_start(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📢 <b>Bot kanali qo'shish</b>\n\n"
            "Kanal username ni kiriting:\n"
            "Misol: <code>@mychannel</code>\n\n"
            "⚠️ Bot kanalda admin bo'lishi kerak!\n"
            "(Avto-post uchun zarur)",
            parse_mode="HTML"
        )
        await state.set_state(AddBotChannelStates.waiting_channel)

    @router.message(AddBotChannelStates.waiting_channel)
    async def add_bot_channel_save(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        channel_id = message.text.strip()
        try:
            chat = await message.bot.get_chat(channel_id)
            channel_name = chat.title
        except Exception:
            channel_name = channel_id

        await kino_db.add_bot_channel(channel_id, channel_name)
        await message.answer(
            f"📢 <b>{channel_name}</b> bot kanaliga qo'shildi!\n\n"
            f"📢 «Kanalimiz» tugmasida ko'rsatiladi\n"
            f"📤 Yangi kinolar avto-post qilinadi",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.callback_query(F.data.startswith("delbotch:"))
    async def delete_bot_channel(callback: CallbackQuery):
        ch_id = int(callback.data.split(":")[1])
        await kino_db.delete_bot_channel(ch_id)
        channels = await kino_db.get_bot_channels()
        text = "✅ Kanal o'chirildi.\n\n"
        if channels:
            for ch in channels:
                text += f"📢 {ch['channel_name'] or ch['channel_id']}\n"
        else:
            text += "⚠️ Bot kanallari yo'q."
        await callback.message.edit_text(
            text, reply_markup=bot_channels_manage_kb(channels), parse_mode="HTML"
        )

    # ==========================================
    #  📢 BROADCAST
    # ==========================================

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

    # ==========================================
    #  📊 STATISTIKA
    # ==========================================

    @router.message(F.text == "📊 Statistika")
    async def show_stats(message: Message):
        if not is_admin(message):
            return

        users_count = await kino_db.get_users_count()
        today_users = await kino_db.get_today_users_count()
        movies_count = await kino_db.get_movies_count()
        sub_channels = await kino_db.get_channels()
        bot_channels = await kino_db.get_bot_channels()

        await message.answer(
            f"📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{users_count}</b>\n"
            f"🆕 Bugungi yangi: <b>{today_users}</b>\n"
            f"🎬 Jami kinolar: <b>{movies_count}</b>\n"
            f"✅ Majburiy obuna: <b>{len(sub_channels)}</b> ta kanal\n"
            f"📢 Bot kanali: <b>{len(bot_channels)}</b> ta kanal",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )

    # ==========================================
    #  🚫 BAN / UNBAN
    # ==========================================

    @router.message(F.text == "🚫 Ban / Unban")
    async def ban_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        await message.answer(
            "🚫 <b>Ban / Unban</b>\n\n"
            "Foydalanuvchi Telegram ID sini kiriting:",
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

    # ==========================================
    #  ❌ BEKOR QILISH
    # ==========================================

    @router.callback_query(F.data == "cancel_admin")
    async def cancel_admin(callback: CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi.")
        await callback.message.answer(
            "👑 Admin Panel",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "noop")
    async def noop(callback: CallbackQuery):
        await callback.answer()

    # ==========================================
    #  ⚙️ SOZLAMALAR (Instagram havolasi)
    # ==========================================
    @router.message(F.text == "⚙️ Sozlamalar")
    async def settings_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        current_link = await kino_db.get_setting("instagram_link")
        link_text = current_link if current_link else "Kiritilmagan"
        
        await message.answer(
            f"⚙️ <b>Sozlamalar</b>\n\n"
            f"📸 <b>Joriy Instagram havola:</b>\n{link_text}\n\n"
            f"Yangi Instagram havolasini yuboring (yoki bekor qilish uchun ❌ bosing):",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(SettingsStates.waiting_instagram_link)

    @router.message(SettingsStates.waiting_instagram_link)
    async def settings_save_ig(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        new_link = message.text.strip()
        await kino_db.set_setting("instagram_link", new_link)
        await message.answer(
            f"✅ <b>Instagram havola saqlandi!</b>\n\n{new_link}",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    # ==========================================
    #  📝 POST YARATISH
    # ==========================================
    @router.message(F.text == "📝 Post yaratish")
    async def create_post_start(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        bot_channels = await kino_db.get_bot_channels()
        if not bot_channels:
            await message.answer(
                "⚠️ Post yaratish uchun avval <b>📢 Bot kanali</b> bo'limidan kanal qo'shing!",
                parse_mode="HTML"
            )
            return
            
        await message.answer(
            "📝 <b>Post yaratish</b>\n\n"
            "Qaysi kinoni kanalga post qilmoqchisiz?\n"
            "Kino kodini yuboring (Masalan: 001):",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CreatePostStates.waiting_code)

    @router.message(CreatePostStates.waiting_code)
    async def create_post_code(message: Message, state: FSMContext):
        if not is_admin(message):
            return
        
        code = message.text.strip()
        movie = await kino_db.get_movie_by_code(code)
        if not movie:
            await message.answer("❌ Bunday kodli kino topilmadi. Qaytadan urinib ko'ring:")
            return
            
        await state.update_data(movie_code=code)
        await message.answer(
            f"✅ Kodi <b>{code}</b> bo'lgan kino topildi: <b>{movie['name']}</b>\n\n"
            f"Kanalga chiqarish uchun Media (rasm yoki qisqa video) yuboring. \n"
            f"Media tagiga (caption) kino haqida ma'lumotlarni ham yozib yuboring (ixtiyoriy).",
            reply_markup=cancel_admin_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CreatePostStates.waiting_media)

    @router.message(CreatePostStates.waiting_media, F.photo | F.video | F.document)
    async def create_post_send(message: Message, state: FSMContext):
        if not is_admin(message):
            return
            
        data = await state.get_data()
        movie_code = data.get("movie_code")
        movie = await kino_db.get_movie_by_code(movie_code)
        
        bot_channels = await kino_db.get_bot_channels()
        ig_link = await kino_db.get_setting("instagram_link") or "Kiritilmagan"
        bot_me = await message.bot.get_me()
        bot_username = bot_me.username
        
        user_caption = message.caption or ""
        if user_caption:
            user_caption += "\n\n"
            
        post_caption = (
            f"{user_caption}"
            f"👆 Ushbu kinoni to'liq holatda kino botimizga joyladik\n\n"
            f"🔎 Kino kodi:  {movie['code']} \n\n"
            f"🤖 Botimiz: @{bot_username}  👈\n\n"
            f"📸 Bizning <a href='{ig_link}'>Instagram sahifamiz</a>\n\n"
            f"📥 To'liq filmni tomosha qilish uchun pastdagi \"📥 Kinoni ko'rish\" tugmasini bosing."
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        post_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Kinoni ko'rish", url=f"https://t.me/{bot_username}?start={movie['code']}")]
        ])
        
        # Get file ID
        file_id = None
        file_type = None
        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"
            
        sent = 0
        failed = 0
        
        for ch in bot_channels:
            try:
                if file_type == "photo":
                    await message.bot.send_photo(
                        chat_id=ch["channel_id"],
                        photo=file_id,
                        caption=post_caption,
                        reply_markup=post_kb,
                        parse_mode="HTML"
                    )
                elif file_type == "video":
                    await message.bot.send_video(
                        chat_id=ch["channel_id"],
                        video=file_id,
                        caption=post_caption,
                        reply_markup=post_kb,
                        parse_mode="HTML"
                    )
                else:
                    await message.bot.send_document(
                        chat_id=ch["channel_id"],
                        document=file_id,
                        caption=post_caption,
                        reply_markup=post_kb,
                        parse_mode="HTML"
                    )
                sent += 1
            except Exception as e:
                failed += 1
                logger.error(f"Post failed for {ch['channel_id']}: {e}")
                
        await message.answer(
            f"✅ <b>Post yaratildi va kanallarga yuborildi!</b>\n\n"
            f"📤 Yuborildi: {sent} ta kanal\n"
            f"❌ Xatolik: {failed} ta kanal",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    return router
