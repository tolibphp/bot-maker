import yt_dlp

def extract_info(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'quiet': True,
        'no_warnings': True,
        'simulate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Title:", info.get('title'))
        print("URL:", info.get('url'))

extract_info('https://www.instagram.com/reel/C3F7-ZqNWwO/')
