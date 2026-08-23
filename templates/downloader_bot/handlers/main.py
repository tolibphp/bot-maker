import asyncio
from aiogram import Router, F
from aiogram.types import Message
import yt_dlp

# We can import premium emojis from the master bot!
from master_bot.emojis import HELLO, CHART, PEOPLE, INBOX, HOURGLASS, CROSS, MOVIE
from aiogram.filters import CommandStart

def create_router() -> Router:
    router = Router()

    def extract_video_info(url: str):
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    @router.message(CommandStart())
    async def cmd_start(message: Message, db):
        await db.add_user(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username
        )
        await message.answer(
            f"{HELLO} <b>Xush kelibsiz!</b>\n\n"
            f"Menga TikTok, Instagram, YouTube yoki boshqa saytdan video ssilkasini yuboring va men uni sizga yuklab beraman!",
            parse_mode="HTML"
        )

    @router.message(F.text == '/stat')
    async def cmd_stat(message: Message, db):
        users, downloads = await db.get_stats()
        await message.answer(
            f"{CHART} <b>Statistika:</b>\n\n"
            f"<blockquote>{PEOPLE} Foydalanuvchilar: <b>{users}</b>\n"
            f"{INBOX} Yuklab olingan videolar: <b>{downloads}</b></blockquote>",
            parse_mode="HTML"
        )

    @router.message(F.text.regexp(r'(https?://[^\s]+)'))
    async def handle_url(message: Message, db):
        url = message.text.strip()
        wait_msg = await message.answer(f"{HOURGLASS} <i>Video yuklanmoqda, kuting...</i>", parse_mode="HTML")
        
        try:
            info = await asyncio.to_thread(extract_video_info, url)
            
            video_url = info.get('url')
            if not video_url:
                await wait_msg.edit_text(f"{CROSS} Videoni yuklab bo'lmadi. Yopiq profil yoki noto'g'ri havola bo'lishi mumkin.", parse_mode="HTML")
                return
                
            title = info.get('title', 'Video')
            bot_info = await message.bot.get_me()
            caption = f"{MOVIE} <b>{title}</b>\n\n{INBOX} @{bot_info.username} orqali yuklandi!"
            
            try:
                await message.answer_video(video=video_url, caption=caption, parse_mode="HTML")
                await db.add_download(message.from_user.id, url)
                await wait_msg.delete()
            except Exception as send_err:
                await wait_msg.edit_text(f"{INBOX} <b>Video topildi:</b>\n\n<a href='{video_url}'>Videoni yuklash (Direct Link)</a>", parse_mode="HTML")
                
        except Exception as e:
            await wait_msg.edit_text(f"{CROSS} Xatolik yuz berdi. Bu havola qo'llab-quvvatlanmasligi mumkin yoki yopiq sahifa.", parse_mode="HTML")

    return router
