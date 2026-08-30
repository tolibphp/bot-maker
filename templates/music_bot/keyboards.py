from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

MUSIC_EMOJI = '<tg-emoji emoji-id="5933952676151695799">🎧</tg-emoji>'
DOWN_EMOJI = '<tg-emoji emoji-id="5463107823946717464">⬇️</tg-emoji>'

def admin_main_kb():
    buttons = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✅ Majburiy obuna")],
        [KeyboardButton(text="📢 Broadcast")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def cancel_admin_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

def channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"🗑 {ch['channel_name'] or ch['channel_id']}", callback_data=f"delch:{ch['id']}")])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_main_kb():
    buttons = [
        [InlineKeyboardButton(text="🔍 Qidirish", switch_inline_query_current_chat="")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subscription_kb(channels: list):
    buttons = []
    for ch in channels:
        channel_id = ch["channel_id"]
        name = ch["channel_name"] or channel_id
        url = f"https://t.me/{channel_id[1:]}" if channel_id.startswith("@") else f"https://t.me/{channel_id}"
        buttons.append([InlineKeyboardButton(text=f"📢 {name}", url=url)])
    buttons.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
