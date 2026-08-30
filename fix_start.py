import os

with open('master_bot/handlers/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make it dynamic
content = content.replace(
    'from config import ADMIN_ID, ADMIN_USERNAME',
    'from config import ADMIN_ID, ADMIN_USERNAME, TEMPLATES'
)

old_text = '''    await message.answer(
        f"{BOT} <b>Bot Maker</b> ga xush kelibsiz!\\n\\n"
        f"Bu bot orqali siz o'zingizning Telegram botingizni yaratishingiz mumkin.\\n\\n"
        f"<blockquote><b>Mavjud shablonlar:</b>\\n"
        f"{MOVIE} Kino Bot — 30,000 so'm\\n"
        f"{STAR} Stars Referral Bot — 15,000 so'm\\n"
        f"{CASH} Premium Pul Ishlash — 15,000 so'm\\n"
        f"{INBOX} Video Yuklovchi Bot — 15,000 so'm\\n\\n"
        f"{GIFT} Barchasi uchun birinchi 30 kun <b>BEPUL!</b>\\n"
        f"Keyin kunlik to'lov olinadi.</blockquote>",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )'''

new_text = '''    # Build dynamic template list
    template_list = ""
    for tmpl_id, tmpl in TEMPLATES.items():
        template_list += f"🔹 <b>{tmpl['name']}</b> — {tmpl['price']:,} so'm\\n"

    await message.answer(
        f"{BOT} <b>Bot Maker Xizmatiga Xush Kelibsiz!</b>\\n\\n"
        f"Bu yerda siz hech qanday dasturlash bilimisiz, bir necha soniya ichida o'z Telegram botingizni yarata olasiz.\\n\\n"
        f"<blockquote><b>Mavjud Shablonlar:</b>\\n"
        f"{template_list}\\n"
        f"{GIFT} <i>Siz yaratgan har qanday bot dastlabki 30 kun mutlaqo BEPUL ishlaydi!</i>\\n"
        f"Keyin oylik yoki kunlik tarif bo'yicha hisoblanadi.</blockquote>\\n\\n"
        f"👇 <b>Marhamat, quyidagi tugmalar orqali xizmatlardan foydalaning:</b>",
        reply_markup=main_menu_kb(message.from_user.id),
        parse_mode="HTML"
    )'''

content = content.replace(old_text, new_text)

with open('master_bot/handlers/start.py', 'w', encoding='utf-8') as f:
    f.write(content)
