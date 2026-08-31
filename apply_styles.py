import os

with open('master_bot/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'text="Bot yaratish", icon_custom_emoji_id=BOT_ID',
    'text="Bot yaratish", icon_custom_emoji_id=BOT_ID, style="success"'
)
content = content.replace(
    'text="Balans to\'ldirish", icon_custom_emoji_id=CARD_ID',
    'text="Balans to\'ldirish", icon_custom_emoji_id=CARD_ID, style="primary"'
)
content = content.replace(
    'text="Balans qo\'shish", icon_custom_emoji_id=MONEY_ID',
    'text="Balans qo\'shish", icon_custom_emoji_id=MONEY_ID, style="primary"'
)
content = content.replace(
    'text=" Ha, yaratish", callback_data="confirm_create", icon_custom_emoji_id=CHECK_ID',
    'text=" Ha, yaratish", callback_data="confirm_create", icon_custom_emoji_id=CHECK_ID, style="success"'
)
content = content.replace(
    'text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID',
    'text=" Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID, style="danger"'
)
content = content.replace(
    'text="Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID',
    'text="Bekor qilish", callback_data="cancel", icon_custom_emoji_id=CROSS_ID, style="danger"'
)
content = content.replace(
    'text=" O\'chirish", callback_data=f"bot_delete:{bot_id}", icon_custom_emoji_id=TRASH_ID',
    'text=" O\'chirish", callback_data=f"bot_delete:{bot_id}", icon_custom_emoji_id=TRASH_ID, style="danger"'
)
content = content.replace(
    'text=" Rad etish", callback_data=f"pay_reject:{user_id}", icon_custom_emoji_id=CROSS_ID',
    'text=" Rad etish", callback_data=f"pay_reject:{user_id}", icon_custom_emoji_id=CROSS_ID, style="danger"'
)
content = content.replace(
    'text="Rad etish", callback_data=f"pay_reject:{user_id}", icon_custom_emoji_id=CROSS_ID',
    'text="Rad etish", callback_data=f"pay_reject:{user_id}", icon_custom_emoji_id=CROSS_ID, style="danger"'
)
content = content.replace(
    'text="Tasdiqlash", callback_data=f"pay_approve:{user_id}:{amount}", icon_custom_emoji_id=CHECK_ID',
    'text="Tasdiqlash", callback_data=f"pay_approve:{user_id}:{amount}", icon_custom_emoji_id=CHECK_ID, style="success"'
)
content = content.replace(
    'text=" Tekshirish", callback_data="check_sub", icon_custom_emoji_id=CHECK_ID',
    'text=" Tekshirish", callback_data="check_sub", icon_custom_emoji_id=CHECK_ID, style="primary"'
)
content = content.replace(
    'text=" Do\'stlarga yuborish", url=share_url, icon_custom_emoji_id=UPRIGHT_ID',
    'text=" Do\'stlarga yuborish", url=share_url, icon_custom_emoji_id=UPRIGHT_ID, style="primary"'
)
content = content.replace(
    'text=" Ishga tushirish", callback_data=f"bot_start:{bot_id}", icon_custom_emoji_id=PLAY_ID',
    'text=" Ishga tushirish", callback_data=f"bot_start:{bot_id}", icon_custom_emoji_id=PLAY_ID, style="success"'
)
content = content.replace(
    'text="To\'lov qildim", icon_custom_emoji_id=CARD_ID',
    'text="To\'lov qildim", icon_custom_emoji_id=CARD_ID, style="success"'
)
content = content.replace(
    'text=" Kanal qo\'shish", callback_data="add_channel"',
    'text=" Kanal qo\'shish", callback_data="add_channel", style="primary"'
)
content = content.replace(
    'text=" Yangi yaratish", callback_data="add_promocode"',
    'text=" Yangi yaratish", callback_data="add_promocode", style="primary"'
)

with open('master_bot/keyboards.py', 'w', encoding='utf-8') as f:
    f.write(content)
