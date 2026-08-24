import asyncio
import uuid
import html
import yt_dlp
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart

from master_bot.emojis import HELLO, CHART, PEOPLE, INBOX, HOURGLASS, CROSS, MOVIE, CROWN, MONEY, HORN, CHECK, WRENCH, DOWN, TRASH, SCROLL

# Memory cache for URLs
URL_CACHE = {}

class DownloaderAdminStates(StatesGroup):
    waiting_channel_id = State()
    waiting_broadcast = State()
    waiting_ad_text = State()

def create_router(admin_id: int) -> Router:
    router = Router()

    # --- KEYBOARDS ---
    def admin_kb():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Xabar yuborish")],
            [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="🗑 Kanallarni o'chirish")],
            [KeyboardButton(text="📝 Reklama sozlash")]
        ], resize_keyboard=True)

    def cancel_kb():
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

    def subscription_kb(channels):
        buttons = []
        for ch in channels:
            name = ch.get("channel_name") or "Kanal"
            buttons.append([InlineKeyboardButton(text=name, url=f"https://t.me/{ch['channel_id'].replace('@', '')}")])
        buttons.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_sub")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def user_main_kb(db):
        from aiogram.types import ReplyKeyboardRemove
        ad_text = await db.get_setting("ad_text")
        if ad_text:
            return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📢 Reklama")]], resize_keyboard=True)
        return ReplyKeyboardRemove()

    def format_choice_kb(cache_id: str):
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎥 Video", callback_data=f"dl_vid_{cache_id}"),
                InlineKeyboardButton(text="🎵 Audio", callback_data=f"dl_aud_{cache_id}")
            ]
        ])

    # --- SUBSCRIPTION ---
    async def check_subscription(bot: Bot, user_id: int, db) -> bool:
        channels = await db.get_channels()
        if not channels:
            return True
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel["channel_id"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    return False
            except Exception:
                continue
        return True

    # --- HELPERS ---
    def extract_video_info(url: str, is_audio=False):
        ydl_opts = {
            'format': 'bestaudio/best' if is_audio else 'b',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    # --- ADMIN HANDLERS ---
    @router.message(F.text == '/admin')
    async def cmd_admin(message: Message):
        if message.from_user.id != admin_id:
            return
        await message.answer(f"{CROWN} <b>Admin Panel</b>\n\nXush kelibsiz!", reply_markup=admin_kb(), parse_mode="HTML")

    @router.message(F.text == "📊 Statistika")
    async def admin_stat(message: Message, db):
        if message.from_user.id != admin_id: return
        users, downloads = await db.get_stats()
        await message.answer(
            f"{CHART} <b>Statistika:</b>\n\n"
            f"<blockquote>{PEOPLE} Foydalanuvchilar: <b>{users}</b>\n"
            f"{INBOX} Yuklab olingan videolar: <b>{downloads}</b></blockquote>",
            parse_mode="HTML"
        )

    @router.message(F.text == "📢 Xabar yuborish")
    async def admin_broadcast_start(message: Message, state: FSMContext):
        if message.from_user.id != admin_id: return
        await message.answer(f"{HORN} Barchaga yuboriladigan xabarni kiriting:", reply_markup=cancel_kb())
        await state.set_state(DownloaderAdminStates.waiting_broadcast)

    @router.message(F.text == "❌ Bekor qilish")
    async def admin_cancel(message: Message, state: FSMContext):
        if message.from_user.id != admin_id: return
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_kb())

    @router.message(DownloaderAdminStates.waiting_broadcast)
    async def admin_broadcast_send(message: Message, state: FSMContext, db):
        if message.from_user.id != admin_id: return
        if message.text == "❌ Bekor qilish":
            return await admin_cancel(message, state)
            
        users = await db.get_all_users()
        sent = 0
        failed = 0
        await message.answer("Xabar yuborilmoqda, kuting...", reply_markup=admin_kb())
        for u in users:
            try:
                await message.copy_to(u["telegram_id"])
                sent += 1
            except Exception:
                failed += 1
        await message.answer(f"{CHECK} <b>Xabar yuborildi!</b>\n\nMuvaffaqiyatli: {sent}\nBloklaganlar: {failed}", parse_mode="HTML")
        await state.clear()

    @router.message(F.text == "➕ Kanal qo'shish")
    async def admin_add_channel(message: Message, state: FSMContext):
        if message.from_user.id != admin_id: return
        await message.answer(f"{DOWN} Kanal IDsini yoki @username kiriting\nMasalan: @mening_kanalim yoki -100123456789", reply_markup=cancel_kb())
        await state.set_state(DownloaderAdminStates.waiting_channel_id)

    @router.message(DownloaderAdminStates.waiting_channel_id)
    async def admin_save_channel(message: Message, state: FSMContext, db):
        if message.from_user.id != admin_id: return
        if message.text == "❌ Bekor qilish":
            return await admin_cancel(message, state)
            
        ch_id = message.text.strip()
        try:
            ch_info = await message.bot.get_chat(ch_id)
            await db.add_channel(str(ch_info.id), ch_info.title)
            await message.answer(f"{CHECK} Kanal qo'shildi: {ch_info.title}", reply_markup=admin_kb())
        except Exception as e:
            await message.answer(f"{CROSS} Kanal topilmadi yoki bot u yerda admin emas! Xato: {html.escape(str(e))}", reply_markup=admin_kb())
        await state.clear()

    @router.message(F.text == "🗑 Kanallarni o'chirish")
    async def admin_del_channel(message: Message, db):
        if message.from_user.id != admin_id: return
        channels = await db.get_channels()
        if not channels:
            await message.answer("Kanallar yo'q.")
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for c in channels:
            kb.inline_keyboard.append([InlineKeyboardButton(text=f"❌ {c['channel_name']}", callback_data=f"del_ch_{c['id']}")])
        await message.answer("O'chirish uchun kanalni tanlang:", reply_markup=kb)

    @router.callback_query(F.data.startswith("del_ch_"))
    async def admin_del_ch_callback(callback: CallbackQuery, db):
        if callback.from_user.id != admin_id: return
        ch_id = int(callback.data.split("_")[2])
        await db.delete_channel(ch_id)
        await callback.message.edit_text("Kanal o'chirildi.")

    @router.message(F.text == "📝 Reklama sozlash")
    async def admin_ad_start(message: Message, state: FSMContext, db):
        if message.from_user.id != admin_id: return
        current_ad = await db.get_setting("ad_text")
        text = f"{SCROLL} <b>Reklama tugmasi sozlamasi</b>\n\n"
        if current_ad:
            text += f"Joriy reklama matni:\n<blockquote>{current_ad}</blockquote>\n\n"
        text += "Foydalanuvchi '📢 Reklama' tugmasini bosganda qanday xabar chiqishini xohlaysiz?\nYangi matnni yuboring (yoki tugmani o'chirish uchun 'ochirish' deb yozing):"
        await message.answer(text, reply_markup=cancel_kb(), parse_mode="HTML")
        await state.set_state(DownloaderAdminStates.waiting_ad_text)

    @router.message(DownloaderAdminStates.waiting_ad_text)
    async def admin_save_ad(message: Message, state: FSMContext, db):
        if message.from_user.id != admin_id: return
        if message.text == "❌ Bekor qilish":
            return await admin_cancel(message, state)
            
        new_text = message.text
        if new_text.lower() == "ochirish":
            await db.set_setting("ad_text", "")
            await message.answer(f"{CHECK} Reklama tugmasi o'chirildi.", reply_markup=admin_kb())
        else:
            await db.set_setting("ad_text", new_text)
            await message.answer(f"{CHECK} Reklama matni saqlandi va foydalanuvchilarga ko'rinadi!", reply_markup=admin_kb())
        await state.clear()

    # --- USER HANDLERS ---
    @router.message(CommandStart())
    async def cmd_start(message: Message, db):
        await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        if not await check_subscription(message.bot, message.from_user.id, db):
            channels = await db.get_channels()
            await message.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=subscription_kb(channels))
            return
            
        kb = await user_main_kb(db)
        await message.answer(
            f"{HELLO} <b>Xush kelibsiz!</b>\n\n"
            f"Menga TikTok, Instagram, YouTube yoki boshqa saytdan video ssilkasini yuboring va men uni sizga yuklab beraman!",
            reply_markup=kb,
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "check_sub")
    async def check_sub_callback(callback: CallbackQuery, db):
        if not await check_subscription(callback.bot, callback.from_user.id, db):
            await callback.answer("Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
            return
        await callback.message.delete()
        kb = await user_main_kb(db)
        await callback.message.answer(f"{CHECK} <b>Obuna tasdiqlandi!</b>\n\nEndi videolarni yuborishingiz mumkin.", reply_markup=kb, parse_mode="HTML")

    @router.message(F.text == "📢 Reklama")
    async def cmd_show_ad(message: Message, db):
        ad_text = await db.get_setting("ad_text")
        if ad_text:
            await message.answer(ad_text)

    @router.message(F.text.regexp(r'(https?://[^\s]+)'))
    async def handle_url(message: Message, db):
        if not await check_subscription(message.bot, message.from_user.id, db):
            channels = await db.get_channels()
            await message.answer("Kechirasiz, kanallarga obuna bo'lmasangiz bot ishlamaydi:", reply_markup=subscription_kb(channels))
            return
            
        url = message.text.strip()
        wait_msg = await message.answer(f"{HOURGLASS} <i>Ma'lumot olinmoqda...</i>", parse_mode="HTML")
        
        try:
            info = await asyncio.to_thread(extract_video_info, url, False)
            title = info.get('title', 'Noma\'lum video')
            thumbnail = info.get('thumbnail')
            extractor = str(info.get('extractor_key', '')).lower()
            
            # If it's YouTube, ask for format choice
            if 'youtube' in extractor:
                cache_id = uuid.uuid4().hex[:10]
                URL_CACHE[cache_id] = url
                kb = format_choice_kb(cache_id)
                caption = f"{MOVIE} <b>{html.escape(title)}</b>\n\nQaysi formatda yuklab olmoqchisiz?"
                
                await wait_msg.delete()
                if thumbnail:
                    try:
                        await message.answer_photo(photo=thumbnail, caption=caption, reply_markup=kb, parse_mode="HTML")
                    except Exception:
                        await message.answer(caption, reply_markup=kb, parse_mode="HTML")
                else:
                    await message.answer(caption, reply_markup=kb, parse_mode="HTML")
            else:
                # For non-YouTube links (Instagram, TikTok, etc), download immediately
                file_url = info.get('url')
                if not file_url:
                    await wait_msg.edit_text(f"{CROSS} Faylni yuklab bo'lmadi.", parse_mode="HTML")
                    return
                
                bot_info = await message.bot.get_me()
                caption = f"{MOVIE} <b>{html.escape(title)}</b>\n\n{INBOX} @{bot_info.username} orqali yuklandi!"
                
                try:
                    await message.answer_video(video=file_url, caption=caption, parse_mode="HTML")
                    await db.add_download(message.from_user.id, url)
                    await wait_msg.delete()
                except Exception:
                    await wait_msg.edit_text(f"{INBOX} <b>Fayl topildi:</b>\n\n<a href='{file_url}'>Bu yerdan yuklab oling (Direct Link)</a>", parse_mode="HTML")
                  
        except Exception as e:
            err_msg = str(e)
            await wait_msg.edit_text(f"{CROSS} Xatolik yuz berdi.\n\nSabab: <code>{html.escape(err_msg)}</code>\n\nIzoh: <i>Telegram storylarni himoya sababli yuklab bo'lmaydi. Instagram post/reels yuklash uchun ochiq profil bo'lishi kerak.</i>", parse_mode="HTML")

    @router.callback_query(F.data.startswith("dl_vid_") | F.data.startswith("dl_aud_"))
    async def process_download(callback: CallbackQuery, db):
        action = callback.data[:6] # dl_vid or dl_aud
        cache_id = callback.data[7:]
        
        url = URL_CACHE.get(cache_id)
        if not url:
            await callback.answer("Havola muddati tugagan. Qaytadan yuboring.", show_alert=True)
            return
            
        await callback.message.edit_reply_markup(reply_markup=None)
        wait_msg = await callback.message.reply(f"{HOURGLASS} <i>Fayl yuklanmoqda, kuting...</i>", parse_mode="HTML")
        
        is_audio = (action == "dl_aud")
        
        try:
            info = await asyncio.to_thread(extract_video_info, url, is_audio)
            file_url = info.get('url')
            if not file_url:
                await wait_msg.edit_text(f"{CROSS} Faylni yuklab bo'lmadi.", parse_mode="HTML")
                return
                
            title = info.get('title', 'Audio' if is_audio else 'Video')
            bot_info = await callback.bot.get_me()
            caption = f"{MOVIE} <b>{html.escape(title)}</b>\n\n{INBOX} @{bot_info.username} orqali yuklandi!"
            
            try:
                if is_audio:
                    await callback.message.answer_audio(audio=file_url, caption=caption, parse_mode="HTML")
                else:
                    await callback.message.answer_video(video=file_url, caption=caption, parse_mode="HTML")
                
                await db.add_download(callback.from_user.id, url)
                await wait_msg.delete()
            except Exception as send_err:
                await wait_msg.edit_text(f"{INBOX} <b>Fayl topildi:</b>\n\n<a href='{file_url}'>Bu yerdan yuklab oling (Direct Link)</a>", parse_mode="HTML")
                
        except Exception as e:
            err_msg = str(e)
            await wait_msg.edit_text(f"{CROSS} Xatolik yuz berdi.\n\nSabab: <code>{html.escape(err_msg)}</code>", parse_mode="HTML")

    return router
