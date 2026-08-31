import os

with open('master_bot/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'callback_data="template:kino", icon_custom_emoji_id=MOVIE_ID)',
    'callback_data="template:kino", icon_custom_emoji_id=MOVIE_ID, style="primary")'
)
content = content.replace(
    'callback_data="template:stars", icon_custom_emoji_id=STAR_ID)',
    'callback_data="template:stars", icon_custom_emoji_id=STAR_ID, style="primary")'
)
content = content.replace(
    'callback_data="template:money", icon_custom_emoji_id=CASH_ID)',
    'callback_data="template:money", icon_custom_emoji_id=CASH_ID, style="primary")'
)
content = content.replace(
    'callback_data="template:downloader", icon_custom_emoji_id=INBOX_ID)',
    'callback_data="template:downloader", icon_custom_emoji_id=INBOX_ID, style="primary")'
)
content = content.replace(
    'icon_custom_emoji_id=status_emoji_id\n            )',
    'icon_custom_emoji_id=status_emoji_id, style="primary"\n            )'
)
content = content.replace(
    'text=" Orqaga", callback_data="cancel", icon_custom_emoji_id=BACK_ID)',
    'text=" Orqaga", callback_data="cancel", icon_custom_emoji_id=BACK_ID, style="danger")'
)
content = content.replace(
    'text=" To\'xtatish", callback_data=f"bot_stop:{bot_id}", icon_custom_emoji_id=PAUSE_ID)',
    'text=" To\'xtatish", callback_data=f"bot_stop:{bot_id}", icon_custom_emoji_id=PAUSE_ID, style="primary")'
)
content = content.replace(
    'text=" Orqaga", callback_data="back_to_bots", icon_custom_emoji_id=BACK_ID)',
    'text=" Orqaga", callback_data="back_to_bots", icon_custom_emoji_id=BACK_ID, style="primary")'
)
content = content.replace(
    'text=" To\'lovlar tarixi", callback_data="payment_history:0", icon_custom_emoji_id=SCROLL_ID)',
    'text=" To\'lovlar tarixi", callback_data="payment_history:0", icon_custom_emoji_id=SCROLL_ID, style="primary")'
)
content = content.replace(
    'text="<", callback_data=f"payment_history:{page-1}")',
    'text="<", callback_data=f"payment_history:{page-1}", style="primary")'
)
content = content.replace(
    'text=f"{page+1}/{total_pages}", callback_data="noop")',
    'text=f"{page+1}/{total_pages}", callback_data="noop", style="primary")'
)
content = content.replace(
    'text=">", callback_data=f"payment_history:{page+1}")',
    'text=">", callback_data=f"payment_history:{page+1}", style="primary")'
)
content = content.replace(
    'text=" Balansga qaytish", callback_data="back_to_balance", icon_custom_emoji_id=BACK_ID)',
    'text=" Balansga qaytish", callback_data="back_to_balance", icon_custom_emoji_id=BACK_ID, style="primary")'
)
content = content.replace(
    'text=f" {name}", url=url)',
    'text=f" {name}", url=url, style="primary")'
)
content = content.replace(
    'icon_custom_emoji_id=TRASH_ID\n            )',
    'icon_custom_emoji_id=TRASH_ID, style="danger"\n            )'
)
content = content.replace(
    'text="Orqaga", icon_custom_emoji_id=BACK_ID)',
    'text="Orqaga", icon_custom_emoji_id=BACK_ID, style="danger")'
)

with open('master_bot/keyboards.py', 'w', encoding='utf-8') as f:
    f.write(content)
