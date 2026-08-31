import os

with open('master_bot/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'text="Mening botlarim", icon_custom_emoji_id=LIST_ID',
    'text="Mening botlarim", icon_custom_emoji_id=LIST_ID, style="success"'
)
content = content.replace(
    'text="Balansim", icon_custom_emoji_id=MONEY_ID',
    'text="Balansim", icon_custom_emoji_id=MONEY_ID, style="success"'
)
content = content.replace(
    'text="Referral", icon_custom_emoji_id=LINK_ID',
    'text="Referral", icon_custom_emoji_id=LINK_ID, style="primary"'
)
content = content.replace(
    'text="Aloqa", icon_custom_emoji_id=PHONE_ID',
    'text="Aloqa", icon_custom_emoji_id=PHONE_ID, style="success"'
)
content = content.replace(
    'text="Promo-kod", icon_custom_emoji_id=PROMO_GIFT_ID',
    'text="Promo-kod", icon_custom_emoji_id=PROMO_GIFT_ID, style="success"'
)
content = content.replace(
    'text="Admin Panel", icon_custom_emoji_id=CROWN_ID',
    'text="Admin Panel", icon_custom_emoji_id=CROWN_ID, style="success"'
)

with open('master_bot/keyboards.py', 'w', encoding='utf-8') as f:
    f.write(content)
