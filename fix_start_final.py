import os

with open('master_bot/handlers/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First, fix the imports
content = content.replace(
    'from config import ADMIN_ID, ADMIN_USERNAME, TEMPLATES',
    'from config import ADMIN_ID, ADMIN_USERNAME, TEMPLATES\nfrom master_bot.emojis import BOT, MOVIE, STAR, CASH, GIFT, BACK, PHONE, CHECK, PERSON, MONEY, INBOX, DOWN'
)

# Second, find the start function's lower part and replace it
# We know it starts at     # Build dynamic template list and ends before @router.message(F.text.in_

start_idx = content.find('    # Build dynamic template list')
end_idx = content.find('@router.message(F.text.in_({"')

new_logic = '''    template_list = ""
    emoji_map = {
        "kino": MOVIE,
        "stars": STAR,
        "money": CASH,
        "downloader": INBOX
    }
    
    for tmpl_id, tmpl in TEMPLATES.items():
        emoji = emoji_map.get(tmpl_id, CHECK)
        # tmpl['name'] includes a standard emoji like "🎬 Kino Bot". 
        # We can strip the first two characters (the emoji and space) to keep it clean.
        clean_name = tmpl['name'].split(" ", 1)[1] if " " in tmpl['name'] else tmpl['name']
        template_list += f"{emoji} <b>{clean_name}</b> — {tmpl['price']:,} so'm\\n"

    await message.answer(
        f"{BOT} <b>Bot Maker Xizmatiga Xush Kelibsiz!</b>\\n\\n"
        f"Bu yerda siz hech qanday dasturlash bilimisiz, bir necha soniya ichida o'z Telegram botingizni yarata olasiz.\\n\\n"
        f"<blockquote><b>Mavjud Shablonlar:</b>\\n"
        f"{template_list}\\n"
        f"{GIFT} <i>Siz yaratgan har qanday bot dastlabki 30 kun mutlaqo BEPUL ishlaydi!</i>\\n"
        f"Keyin oylik yoki kunlik tarif bo'yicha hisoblanadi.</blockquote>\\n\\n"
        f"{DOWN} <b>Marhamat, quyidagi tugmalar orqali xizmatlardan foydalaning:</b>",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )

'''

content = content[:start_idx] + new_logic + content[end_idx:]

with open('master_bot/handlers/start.py', 'w', encoding='utf-8') as f:
    f.write(content)
