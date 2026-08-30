import os

with open('master_bot/handlers/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('@router.message(F.text.in_({"?"T Orqaga", "Orqaga"}))', '@router.message(F.text.in_({"🔙 Orqaga", "Orqaga"}))')
content = content.replace('@router.message(F.text.in_({"?"? Aloqa", "Aloqa"}))', '@router.message(F.text.in_({"📞 Aloqa", "Aloqa"}))')

with open('master_bot/handlers/start.py', 'w', encoding='utf-8') as f:
    f.write(content)
