with open('bot_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from templates.downloader_bot import DownloaderBot\nfrom templates.music_bot import MusicBot', 'from templates.downloader_bot import DownloaderBot')

music_block = '''            elif bot_data["template_type"] == "music":
                from templates.music_bot import MusicBot
                bot_instance = MusicBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )'''
content = content.replace(music_block, '')

with open('bot_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)
