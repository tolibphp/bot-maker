import os
import re

with open('master_bot/handlers/admin.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix imports
if 'PROMO_GIFT' not in content:
    content = content.replace(
        'from master_bot.emojis import CROWN, CHART, PEOPLE, HORN, WRENCH, MONEY, CROSS, CHECK, DOWN',
        'from master_bot.emojis import CROWN, CHART, PEOPLE, HORN, WRENCH, MONEY, CROSS, CHECK, DOWN, PROMO_GIFT'
    )

# Fix triggers
content = re.sub(r'F\.text\.in_\(\{"[^"]+ Admin Panel", "Admin Panel"\}\)', 'F.text == "Admin Panel"', content)
content = re.sub(r'F\.text == "[^"]+ Majburiy obuna"', 'F.text == "Majburiy obuna"', content)
content = re.sub(r'F\.text\.in_\(\{"[^"]+ Promo-kodlar", "Promo-kodlar"\}\)', 'F.text == "Promo-kodlar"', content)

# I will just replace the exact substrings seen in powershell output.
content = content.replace("?:", "{CHECK}")
content = content.replace("?'", "{MONEY}")
content = content.replace("?'?", "{PEOPLE}")
content = content.replace("???", "{PROMO_GIFT}")
content = content.replace("??", "{CROSS}")
content = content.replace("?-'", "{CROSS}")
content = content.replace("??", "{CROSS}")
content = content.replace("?  ", "{CHECK} ")

with open('master_bot/handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
