from aiogram import Router, F
from aiogram.types import Message, InlineQuery, InlineQueryResultAudio
import urllib.parse
import json

from templates.music_bot.keyboards import MUSIC_EMOJI, DOWN_EMOJI

def create_search_router(db, admin_id: int):
    router = Router()
    
    # We will use a mock or simple yt-dlp implementation later
    # For now, let's setup the structure.

    @router.message(F.text)
    async def search_text(message: Message):
        if message.text.startswith('/'): return
        
        # Check sub
        channels = await db.get_channels()
        if channels and message.from_user.id != admin_id:
            try:
                for ch in channels:
                    member = await message.bot.get_chat_member(ch["channel_id"], message.from_user.id)
                    if member.status in ['left', 'kicked', 'restricted']:
                        await message.answer("❌ Qidirish uchun oldin kanallarga obuna bo'ling! /start ni bosing.")
                        return
            except:
                pass
        
        await message.answer(
            f"🔍 <b>Qidirilmoqda:</b> {message.text}\n\n"
            f"⏳ Iltimos biroz kuting...",
            parse_mode="HTML"
        )
        
        # Here we will add yt-dlp code to download and send audio
        await message.answer("Yt-dlp integratsiyasi tez orada qo'shiladi...")

    return router
