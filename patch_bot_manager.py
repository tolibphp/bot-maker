import re

with open('bot_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from templates.downloader_bot import DownloaderBot', 'from templates.downloader_bot import DownloaderBot\nfrom templates.music_bot import MusicBot')

old_dict = '''        TEMPLATE_MAP = {
            "kino": KinoBot,
            "stars": StarsBot,
            "money": MoneyBot,
            "downloader": DownloaderBot
        }'''
        
new_dict = '''        TEMPLATE_MAP = {
            "kino": KinoBot,
            "stars": StarsBot,
            "money": MoneyBot,
            "downloader": DownloaderBot,
            "music": MusicBot
        }'''
        
content = content.replace(old_dict, new_dict)

with open('bot_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)
