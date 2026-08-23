from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def admin_main_kb():
    buttons = [
        [KeyboardButton(text="➕ Kino qo'shish"), KeyboardButton(text="📋 Kinolar ro'yxati")],
        [KeyboardButton(text="📁 Kategoriya boshqarish"), KeyboardButton(text="✅ Majburiy obuna")],
        [KeyboardButton(text="📢 Broadcast"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🚫 Ban / Unban"), KeyboardButton(text="👤 User rejimi")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def channel_link_kb(channels: list):
    """Single inline button with channel link for user welcome."""
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
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


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


def categories_kb(categories: list):
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {cat['name']}",
                callback_data=f"cat:{cat['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def categories_select_kb(categories: list):
    """For selecting category when adding movie."""
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=cat["name"],
                callback_data=f"selcat:{cat['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def movie_pagination_kb(page: int, total_pages: int):
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"mpage:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"mpage:{page+1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def movie_list_kb(movies: list, page: int, total_pages: int):
    """Movie list with inline delete buttons for admin."""
    buttons = []
    for m in movies:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎬 #{m['code']} - {m['name']}",
                callback_data=f"noop"
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"delmovie:{m['code']}"
            ),
        ])
    # Pagination
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


def categories_manage_kb(categories: list):
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 {cat['name']}",
                callback_data=f"delcat:{cat['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="add_category")])
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
