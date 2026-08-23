from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⭐️ Stars ishlash")],
            [KeyboardButton(text="💸 Stars yechish"), KeyboardButton(text="📊 To'lovlar")],
            [KeyboardButton(text="ℹ️ FAQ")]
        ],
        resize_keyboard=True
    )

def admin_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="✅ Majburiy obuna")],
            [KeyboardButton(text="📢 To'lovlar kanali"), KeyboardButton(text="📈 Statistika")],
            [KeyboardButton(text="👤 User rejimi")]
        ],
        resize_keyboard=True
    )

def settings_kb(ref_bonus: int, min_withdraw: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Referal bonus: {ref_bonus} ⭐️", callback_data="set_ref_bonus")],
        [InlineKeyboardButton(text=f"Minimal yechish: {min_withdraw} ⭐️", callback_data="set_min_withdraw")],
        [InlineKeyboardButton(text="🔙 Yopish", callback_data="close_admin")]
    ])

def subscription_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=ch['name'], url=f"https://t.me/{ch['name'].replace('@', '')}")])
    buttons.append([InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([
            InlineKeyboardButton(text=f"❌ {ch['name']}", callback_data=f"delch:{ch['channel_id']}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    buttons.append([InlineKeyboardButton(text="🔙 Yopish", callback_data="close_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")]
    ])

def payout_approve_kb(user_id: int, amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'landi", callback_data=f"payout_approve:{user_id}:{amount}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"payout_reject:{user_id}:{amount}")]
    ])

def post_bot_link_kb(bot_username: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Botga o'tish", url=f"https://t.me/{bot_username}")]
    ])
