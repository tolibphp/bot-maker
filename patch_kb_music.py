import re

with open('master_bot/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('PROMO_CASH_ID', 'PROMO_CASH_ID, MUSIC_ID')

old_kb = '''def templates_kb():
    buttons = [
        [InlineKeyboardButton(text=" Kino Bot — 30,000 so'm", callback_data="template:kino", icon_custom_emoji_id=MOVIE_ID)],
        [InlineKeyboardButton(text=" Stars Referral Bot — 15,000 so'm", callback_data="template:stars", icon_custom_emoji_id=STAR_ID)],
        [InlineKeyboardButton(text=" Premium Pul Ishlash — 15,000 so'm", callback_data="template:money", icon_custom_emoji_id=CASH_ID)],
        [InlineKeyboardButton(text=" Video Yuklovchi — 15,000 so'm", callback_data="template:downloader", icon_custom_emoji_id=INBOX_ID)],
        [InlineKeyboardButton(text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)'''

new_kb = '''def templates_kb():
    buttons = [
        [InlineKeyboardButton(text=" Kino Bot — 25,000 so'm", callback_data="template:kino", icon_custom_emoji_id=MOVIE_ID)],
        [InlineKeyboardButton(text=" Stars Referral Bot — 10,000 so'm", callback_data="template:stars", icon_custom_emoji_id=STAR_ID)],
        [InlineKeyboardButton(text=" Premium Pul Ishlash — 10,000 so'm", callback_data="template:money", icon_custom_emoji_id=CASH_ID)],
        [InlineKeyboardButton(text=" Video Yuklovchi — 10,000 so'm", callback_data="template:downloader", icon_custom_emoji_id=INBOX_ID)],
        [InlineKeyboardButton(text=" VK Music Bot — 10,000 so'm", callback_data="template:music", icon_custom_emoji_id=MUSIC_ID)],
        [InlineKeyboardButton(text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)'''

content = content.replace(old_kb, new_kb)

with open('master_bot/keyboards.py', 'w', encoding='utf-8') as f:
    f.write(content)
