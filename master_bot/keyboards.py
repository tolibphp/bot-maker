from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import ADMIN_ID


def main_menu_kb(user_id: int = None):
    buttons = [
        [KeyboardButton(text="🤖 Bot yaratish")],
        [KeyboardButton(text="📋 Mening botlarim"), KeyboardButton(text="💰 Balansim")],
        [KeyboardButton(text="🔗 Referral"), KeyboardButton(text="💳 Balans to'ldirish")],
        [KeyboardButton(text="📞 Aloqa")],
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
        [InlineKeyboardButton(text="⭐️ Stars Referral Bot — 35,000 so'm", callback_data="template:stars")],
        [InlineKeyboardButton(text="💸 Premium Pul Ishlash — 50,000 so'm", callback_data="template:money")],
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
        buttons.append([InlineKeyboardButton(text="⏸ To'xtatish", callback_data=f"bot_stop:{bot_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="▶️ Ishga tushirish", callback_data=f"bot_start:{bot_id}")])
    buttons.append([InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"bot_delete:{bot_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_bots")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_kb():
    buttons = [
        [KeyboardButton(text="💳 To'lov qildim")],
        [KeyboardButton(text="🔙 Orqaga")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def payment_approve_kb(user_id: int, amount: int):
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_approve:{user_id}:{amount}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_reject:{user_id}")],
    ]
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


def balance_kb():
    """Inline keyboard under the balance message."""
    buttons = [
        [InlineKeyboardButton(text="📜 To'lovlar tarixi", callback_data="payment_history:0")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_history_kb(page: int, total_pages: int):
    """Inline keyboard for navigating transaction history."""
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"payment_history:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"payment_history:{page+1}"))
    if nav:
        buttons.append(nav)
    
    buttons.append([InlineKeyboardButton(text="🔙 Balansga qaytish", callback_data="back_to_balance")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def share_ref_link_kb(ref_link: str):
    share_url = f"https://t.me/share/url?url={ref_link}&text=Bot yaratish uchun eng zo'r platforma!"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↗️ Do'stlarga yuborish", url=share_url)]
    ])
