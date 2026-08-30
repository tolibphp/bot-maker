import os

with open('master_bot/emojis.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('5215239948420003628', '5933952676151695799')

with open('master_bot/emojis.py', 'w', encoding='utf-8') as f:
    f.write(content)
