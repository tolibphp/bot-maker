from aiogram import Router, F
from aiogram.types import Message

from database.users import get_referral_count, get_balance
from master_bot.keyboards import main_menu_kb

REFERRAL_JOIN_BONUS = 1_000
REFERRAL_BOT_CREATE_BONUS = 5_000

router = Router()


@router.message(F.text == "🔗 Referral")
async def referral_menu(message: Message):
    user_id = message.from_user.id
    bot_me = await message.bot.get_me()

    ref_link = f"https://t.me/{bot_me.username}?start=ref_{user_id}"
    ref_count = await get_referral_count(user_id)
    balance = await get_balance(user_id)

    total_earned = ref_count * REFERRAL_JOIN_BONUS  # Approximate

    await message.answer(
        f"🔗 <b>Referral dasturi</b>\n\n"
        f"Do'stlaringizni taklif qiling va pul ishlang!\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━┓\n"
        f"  💰 Har bir do'st uchun: <b>+{REFERRAL_JOIN_BONUS:,} so'm</b>\n"
        f"  🤖 Do'st bot yaratsa: <b>+{REFERRAL_BOT_CREATE_BONUS:,} so'm</b>\n"
        f"┗━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"📊 <b>Sizning statistika:</b>\n"
        f"👥 Taklif qilganlar: <b>{ref_count}</b> ta\n"
        f"💰 Balans: <b>{balance:,} so'm</b>\n\n"
        f"🔗 <b>Sizning havola:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"👆 Havolani nusxalab do'stlaringizga yuboring!",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )
