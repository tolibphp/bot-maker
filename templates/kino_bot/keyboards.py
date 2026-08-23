import urllib.parse

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def user_kb():
    """User keyboard — qidiruv va kanal."""
    buttons = [
        [KeyboardButton(text="🔍 Kino qidirish"), KeyboardButton(text="📢 Kanalimiz")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_main_kb():
    buttons = [
        [KeyboardButton(text="➕ Kino qo'shish"), KeyboardButton(text="📋 Kinolar ro'yxati")],
        [KeyboardButton(text="✅ Majburiy obuna"), KeyboardButton(text="📢 Bot kanali")],
        [KeyboardButton(text="📢 Broadcast"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🚫 Ban / Unban"), KeyboardButton(text="👤 User rejimi")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def movie_share_kb(bot_username: str, code: str, movie_name: str):
    """Share button under movie for users."""
    bot_link = f"https://t.me/{bot_username}?start={code}"
    share_url = "https://t.me/share/url?" + urllib.parse.urlencode({
        "url": bot_link,
        "text": f"🎬 {movie_name}\n▶️ Botda ko'rish 👆"
    })
    buttons = [
        [InlineKeyboardButton(text="📤 Do'stlarga ulashish", url=share_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def channel_post_kb(bot_username: str):
    """Button under channel post — link to bot."""
    buttons = [
        [InlineKeyboardButton(text="🎬 Kinoni ko'rish", url=f"https://t.me/{bot_username}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscription_kb(channels: list):
    buttons = []
    for ch in channels:
        channel_id = ch["channel_id"]
        name = ch["channel_name"] or channel_id
        if channel_id.startswith("@"):
            url = f"https://t.me/{channel_id[1:]}"
        else:
            url = f"https://t.me/{channel_id}"
        buttons.append([
            InlineKeyboardButton(text=f"📢 {name}", url=url)
        ])
    buttons.append([
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def movie_list_kb(movies: list, page: int, total_pages: int):
    buttons = []
    for m in movies:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎬 #{m['code']} - {m['name']}",
                callback_data="noop"
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"delmovie:{m['code']}"
            ),
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"mpage:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"mpage:{page+1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 {ch['channel_name'] or ch['channel_id']}",
                callback_data=f"delch:{ch['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 {ch['channel_name'] or ch['channel_id']}",
                callback_data=f"delbotch:{ch['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_bot_channel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")]
    ])


def confirm_delete_kb(code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_del:{code}")],
        [InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_del")],
    ])
