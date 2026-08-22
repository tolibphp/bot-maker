from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import ADMIN_ID


def main_menu_kb(user_id: int = None):
    buttons = [
        [KeyboardButton(text="🤖 Bot yaratish")],
        [KeyboardButton(text="📋 Mening botlarim"), KeyboardButton(text="💰 Balansim")],
        [KeyboardButton(text="💳 Balans to'ldirish"), KeyboardButton(text="📞 Aloqa")],
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="👑 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_panel_kb():
    buttons = [
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="💰 Balans qo'shish")],
        [KeyboardButton(text="📢 Broadcast"), KeyboardButton(text="🔧 Barcha botlar")],
        [KeyboardButton(text="🔙 Orqaga")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def templates_kb():
    buttons = [
        [InlineKeyboardButton(text="🎬 Kino Bot — 35,000 so'm", callback_data="template:kino")],
        [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_create_kb():
    buttons = [
        [InlineKeyboardButton(text="✅ Ha, yaratish", callback_data="confirm_create")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def my_bots_kb(bots: list):
    buttons = []
    for bot in bots:
        status_emoji = "✅" if bot["status"] == "active" else "⛔"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_emoji} @{bot['bot_username']} ({bot['template_type']})",
                callback_data=f"mybot:{bot['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_manage_kb(bot_id: int, status: str):
    buttons = []
    if status == "active":
        buttons.append([InlineKeyboardButton(text="⏹ To'xtatish", callback_data=f"bot_stop:{bot_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="▶️ Ishga tushirish", callback_data=f"bot_start:{bot_id}")])
    buttons.append([InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"bot_delete:{bot_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_bots")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])


def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
        resize_keyboard=True
    )
