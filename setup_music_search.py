import os
import json
import asyncio
import hashlib
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InlineQuery, InlineQueryResultAudio
from aiogram.exceptions import TelegramAPIError

from templates.music_bot.keyboards import MUSIC_EMOJI, DOWN_EMOJI

def create_search_router(db, admin_id: int):
    router = Router()
    
    async def search_youtube(query: str, limit: int = 5):
        cmd = [
            'yt-dlp',
            f'ytsearch{limit}:{query}',
            '--dump-json',
            '--no-playlist',
            '--ignore-errors',
            '--extract-audio',
            '--audio-format', 'mp3'
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        results = []
        for line in stdout.decode().splitlines():
            if not line.strip(): continue
            try:
                data = json.loads(line)
                results.append({
                    'id': data.get('id'),
                    'title': data.get('title'),
                    'duration': data.get('duration_string', '0:00'),
                    'channel': data.get('uploader', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={data.get('id')}"
                })
            except:
                pass
        return results

    async def download_audio(youtube_id: str, output_path: str):
        url = f"https://www.youtube.com/watch?v={youtube_id}"
        cmd = [
            'yt-dlp',
            '-x', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', f'{output_path}/%(id)s.%(ext)s',
            url
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return f"{output_path}/{youtube_id}.mp3"

    @router.message(F.text)
    async def search_text(message: Message):
        if message.text.startswith('/'): return
        
        msg = await message.answer(f"{MUSIC_EMOJI} <b>Qidirilmoqda...</b>", parse_mode="HTML")
        
        results = await search_youtube(message.text)
        if not results:
            await msg.edit_text("❌ Hech narsa topilmadi.")
            return
            
        buttons = []
        text = f"🔍 <b>{message.text}</b> uchun natijalar:\n\n"
        for i, res in enumerate(results, 1):
            text += f"{i}. <b>{res['title']}</b> ({res['duration']})\n👤 {res['channel']}\n\n"
            buttons.append([InlineKeyboardButton(
                text=f"{DOWN_EMOJI} {i} - Musiqani yuklash",
                callback_data=f"dlaudio:{res['id']}"
            )])
            
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

    @router.callback_query(F.data.startswith("dlaudio:"))
    async def cb_dl_audio(callback: CallbackQuery):
        yt_id = callback.data.split(":")[1]
        
        cached = await db.get_cached_audio(yt_id)
        if cached:
            try:
                await callback.message.answer_audio(
                    audio=cached["telegram_file_id"],
                    caption=f"{MUSIC_EMOJI} @{callback.bot._me.username} orqali yuklandi"
                )
                await callback.answer()
                return
            except Exception:
                pass
                
        await callback.answer("⏳ Yuklanmoqda...", show_alert=False)
        msg = await callback.message.answer(f"{DOWN_EMOJI} <b>Musiqa yuklanmoqda... Iltimos kuting.</b>", parse_mode="HTML")
        
        os.makedirs("downloads", exist_ok=True)
        try:
            file_path = await download_audio(yt_id, "downloads")
            if os.path.exists(file_path):
                audio = FSInputFile(file_path)
                sent = await callback.message.answer_audio(
                    audio=audio,
                    caption=f"{MUSIC_EMOJI} @{callback.bot._me.username} orqali yuklandi"
                )
                await db.cache_audio(yt_id, sent.audio.file_id, sent.audio.title or yt_id)
                os.remove(file_path)
                await msg.delete()
            else:
                await msg.edit_text("❌ Yuklashda xatolik yuz berdi.")
        except Exception as e:
            await msg.edit_text("❌ Kutilmagan xatolik yuz berdi.")

    @router.inline_query()
    async def inline_search(query: InlineQuery):
        text = query.query.strip()
        if not text:
            return
            
        results = await search_youtube(text, limit=10)
        inline_results = []
        
        for res in results:
            cached = await db.get_cached_audio(res['id'])
            if cached:
                # If cached, we can serve it immediately!
                inline_results.append(
                    InlineQueryResultAudio(
                        id=res['id'],
                        audio_url="", # We don't have direct URL, aiogram inline audio requires http URL or file_id. Wait, we can't use cached file_id in audio_url. We have to use audio_file_id!
                        audio_file_id=cached['telegram_file_id'],
                        title=res['title'],
                        performer=res['channel']
                    )
                )
            else:
                # We can't provide InlineQueryResultAudio without a direct mp3 link or file_id.
                # So we can't fully do inline download for uncached music natively in Telegram.
                pass
                
        if inline_results:
            try:
                await query.answer(inline_results, cache_time=300, is_personal=False)
            except:
                pass

    return router
