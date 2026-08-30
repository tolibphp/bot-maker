from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import ADMIN_ID
from master_bot.emojis import (
    BOT_ID, LIST_ID, MONEY_ID, LINK_ID, CARD_ID, PHONE_ID, CROWN_ID,
    CHART_ID, PEOPLE_ID, HORN_ID, WRENCH_ID, BACK_ID, MOVIE_ID, STAR_ID, CASH_ID,
    CHECK_ID, CROSS_ID, PAUSE_ID, PLAY_ID, TRASH_ID, UPRIGHT_ID, SCROLL_ID, INBOX_ID, PROMO_GIFT_ID, PROMO_CASH_ID
)

def main_menu_kb(user_id: int = None):
    buttons = [
        [KeyboardButton(text="Bot yaratish", icon_custom_emoji_id=BOT_ID)],
        [KeyboardButton(text="Mening botlarim", icon_custom_emoji_id=LIST_ID), 
         KeyboardButton(text="Balansim", icon_custom_emoji_id=MONEY_ID)],
        [KeyboardButton(text="Referral", icon_custom_emoji_id=LINK_ID), 
         KeyboardButton(text="Balans to'ldirish", icon_custom_emoji_id=CARD_ID)],
        [KeyboardButton(text="Aloqa", icon_custom_emoji_id=PHONE_ID),
         KeyboardButton(text="Promo-kod", icon_custom_emoji_id=PROMO_GIFT_ID)],
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="Admin Panel", icon_custom_emoji_id=CROWN_ID)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def admin_panel_kb():
    buttons = [
        [KeyboardButton(text="Statistika", icon_custom_emoji_id=CHART_ID),
         KeyboardButton(text="Majburiy obuna", icon_custom_emoji_id=CHECK_ID)],
        [KeyboardButton(text="Foydalanuvchilar", icon_custom_emoji_id=PEOPLE_ID), 
         KeyboardButton(text="Balans qo'shish", icon_custom_emoji_id=MONEY_ID)],
        [KeyboardButton(text="Broadcast", icon_custom_emoji_id=HORN_ID), 
         KeyboardButton(text="Barcha botlar", icon_custom_emoji_id=WRENCH_ID)],
        [KeyboardButton(text="Promo-kodlar", icon_custom_emoji_id=PROMO_GIFT_ID)],
        [KeyboardButton(text="Orqaga", icon_custom_emoji_id=BACK_ID)],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def templates_kb():
    buttons = [
        [InlineKeyboardButton(text=" Kino Bot - 25,000 so'm", callback_data="template:kino", icon_custom_emoji_id=MOVIE_ID)],
        [InlineKeyboardButton(text=" Stars Referral Bot - 10,000 so'm", callback_data="template:stars", icon_custom_emoji_id=STAR_ID)],
        [InlineKeyboardButton(text=" Premium Pul Ishlash - 10,000 so'm", callback_data="template:money", icon_custom_emoji_id=CASH_ID)],
        [InlineKeyboardButton(text=" Video Yuklovchi - 10,000 so'm", callback_data="template:downloader", icon_custom_emoji_id=INBOX_ID)],
        [InlineKeyboardButton(text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_create_kb():
    buttons = [
        [InlineKeyboardButton(text=" Ha, yaratish", callback_data="confirm_create", icon_custom_emoji_id=CHECK_ID)],
        [InlineKeyboardButton(text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def my_bots_kb(bots: list):
    buttons = []
    for bot in bots:
        status_emoji_id = CHECK_ID if bot["status"] == "active" else STOP_ID
        buttons.append([
            InlineKeyboardButton(
                text=f" @{bot['bot_username']} ({bot['template_type']})",
                callback_data=f"mybot:{bot['id']}",
                icon_custom_emoji_id=status_emoji_id
            )
        ])
    buttons.append([InlineKeyboardButton(text=" Orqaga", callback_data="cancel", icon_custom_emoji_id=BACK_ID)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_manage_kb(bot_id: int, status: str):
    buttons = []
    if status == "active":
        buttons.append([InlineKeyboardButton(text=" To'xtatish", callback_data=f"bot_stop:{bot_id}", icon_custom_emoji_id=PAUSE_ID)])
    else:
        buttons.append([InlineKeyboardButton(text=" Ishga tushirish", callback_data=f"bot_start:{bot_id}", icon_custom_emoji_id=PLAY_ID)])
    buttons.append([InlineKeyboardButton(text=" O'chirish", callback_data=f"bot_delete:{bot_id}", icon_custom_emoji_id=TRASH_ID)])
    buttons.append([InlineKeyboardButton(text=" Orqaga", callback_data="back_to_bots", icon_custom_emoji_id=BACK_ID)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_kb():
    buttons = [
        [KeyboardButton(text="To'lov qildim", icon_custom_emoji_id=CARD_ID)],
        [KeyboardButton(text="Orqaga", icon_custom_emoji_id=BACK_ID)],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def payment_approve_kb(user_id: int, amount: int):
    buttons = [
        [InlineKeyboardButton(text="Tasdiqlash", callback_data=f"pay_approve:{user_id}:{amount}", icon_custom_emoji_id=CHECK_ID)],
        [InlineKeyboardButton(text="Rad etish", callback_data=f"pay_reject:{user_id}", icon_custom_emoji_id=CROSS_ID)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID)]
    ])


def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Orqaga", icon_custom_emoji_id=BACK_ID)]],
        resize_keyboard=True
    )


def balance_kb():
    buttons = [
        [InlineKeyboardButton(text=" To'lovlar tarixi", callback_data="payment_history:0", icon_custom_emoji_id=SCROLL_ID)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_history_kb(page: int, total_pages: int):
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="<", callback_data=f"payment_history:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=">", callback_data=f"payment_history:{page+1}"))
    if nav:
        buttons.append(nav)
    
    buttons.append([InlineKeyboardButton(text=" Balansga qaytish", callback_data="back_to_balance", icon_custom_emoji_id=BACK_ID)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def share_ref_link_kb(ref_link: str):
    share_url = f"https://t.me/share/url?url={ref_link}&text=Bot yaratish uchun eng zo'r platforma!"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Do'stlarga yuborish", url=share_url, icon_custom_emoji_id=UPRIGHT_ID)]
    ])

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
            InlineKeyboardButton(text=f" {name}", url=url)
        ])
    buttons.append([
        InlineKeyboardButton(text=" Tekshirish", callback_data="check_sub", icon_custom_emoji_id=CHECK_ID)
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def channels_manage_kb(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f" {ch['channel_name'] or ch['channel_id']}",
                callback_data=f"delch:{ch['id']}", icon_custom_emoji_id=TRASH_ID
            )
        ])
    buttons.append([InlineKeyboardButton(text=" Kanal qo'shish", callback_data="add_channel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def promocodes_manage_kb(promos: list):
    buttons = []
    for p in promos:
        buttons.append([
            InlineKeyboardButton(
                text=f" {p['code']} ({p['reward_amount']}) - {p['used_count']}/{p['usage_limit']}",
                callback_data=f"delpromo:{p['id']}", icon_custom_emoji_id=TRASH_ID
            )
        ])
    buttons.append([InlineKeyboardButton(text=" Yangi yaratish", callback_data="add_promocode")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
