import re

with open('master_bot/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'CHECK_ID, CROSS_ID, PAUSE_ID, PLAY_ID, TRASH_ID, UPRIGHT_ID, SCROLL_ID',
    'CHECK_ID, CROSS_ID, PAUSE_ID, PLAY_ID, TRASH_ID, UPRIGHT_ID, SCROLL_ID, INBOX_ID, PROMO_GIFT_ID, PROMO_CASH_ID'
)

content = content.replace(
    '[KeyboardButton(text=""Aloqa"", icon_custom_emoji_id=PHONE_ID)],',
    '[KeyboardButton(text=""Aloqa"", icon_custom_emoji_id=PHONE_ID),\n         KeyboardButton(text=""Promo-kod"", icon_custom_emoji_id=PROMO_GIFT_ID)],'
)

content = content.replace(
    '[KeyboardButton(text=""Orqaga"", icon_custom_emoji_id=BACK_ID)],',
    '[KeyboardButton(text=""🎁 Promo-kodlar""), KeyboardButton(text=""Orqaga"", icon_custom_emoji_id=BACK_ID)],'
)

content = content.replace(
    'template:downloader"", icon_custom_emoji_id=SCROLL_ID)',
    'template:downloader"", icon_custom_emoji_id=INBOX_ID)'
)

# Add promocode manage keyboards at the end
content += '''

def promocodes_manage_kb(promos: list):
    buttons = []
    for p in promos:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 {p['code']} ({p['reward_amount']}) - {p['used_count']}/{p['usage_limit']}",
                callback_data=f"delpromo:{p['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Yangi yaratish", callback_data="add_promocode")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

with open('master_bot/keyboards.py', 'w', encoding='utf-8') as f:
    f.write(content)

