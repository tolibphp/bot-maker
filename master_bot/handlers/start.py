from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.users import add_user
from master_bot.keyboards import main_menu_kb
from config import ADMIN_USERNAME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    await message.answer(
        "🤖 <b>Bot Maker</b> ga xush kelibsiz!\n\n"
        "Bu bot orqali siz o'zingizning Telegram botingizni yaratishingiz mumkin.\n\n"
        "🎬 <b>Mavjud shablonlar:</b>\n"
        "• Kino Bot — 35,000 so'm\n\n"
        "🎁 Birinchi 30 kun <b>BEPUL!</b>\n"
        "Keyin kuniga 5,000 so'm.",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )


@router.message(F.text == "🔙 Orqaga")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )


@router.message(F.text == "📞 Aloqa")
async def contact(message: Message):
    await message.answer(
        f"📞 <b>Aloqa</b>\n\n"
        f"Savollar va takliflar uchun admin ga yozing:\n"
        f"👤 {ADMIN_USERNAME}",
        parse_mode="HTML"
    )
