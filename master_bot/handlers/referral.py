from aiogram import Router, F
from aiogram.types import Message

from database.users import get_referral_count, get_balance
from master_bot.keyboards import main_menu_kb, share_ref_link_kb
from master_bot.emojis import LINK, MONEY, BOT, PEOPLE, DOWN

REFERRAL_JOIN_BONUS = 1_000
REFERRAL_BOT_CREATE_BONUS = 5_000

router = Router()

@router.message(F.text.in_({"🔗 Referral", "Referral"}))
async def show_referral(message: Message):
    user_id = message.from_user.id
    bot = await message.bot.get_me()
    
    ref_link = f"https://t.me/{bot.username}?start=ref_{user_id}"
    ref_count = await get_referral_count(user_id)
    balance = await get_balance(user_id)

    text = (
        f"{LINK} <b>Referral dasturi</b>\n\n"
        f"Do'stlaringizni taklif qiling va pul ishlang!\n\n"
        f"<blockquote>{MONEY} Har bir do'st uchun: <b>+{REFERRAL_JOIN_BONUS:,} so'm</b>\n"
        f"{BOT} Do'st bot yaratsa: <b>+{REFERRAL_BOT_CREATE_BONUS:,} so'm</b></blockquote>\n\n"
        f"<b>Sizning statistika:</b>\n"
        f"<blockquote>{PEOPLE} Takliflar: <b>{ref_count}</b> ta\n"
        f"{MONEY} Balans: <b>{balance:,} so'm</b></blockquote>\n\n"
        f"{DOWN} <b>Sizning havola:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"Havolani nusxalab do'stlaringizga yuboring!"
    )

    await message.answer(text, reply_markup=share_ref_link_kb(ref_link), parse_mode="HTML")
