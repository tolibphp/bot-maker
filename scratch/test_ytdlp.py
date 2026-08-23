import yt_dlp

def extract_info(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'forceurl': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Title:", info.get('title'))
        print("URL:", info.get('url'))

extract_info('https://www.tiktok.com/@mrbeast/video/7279172449755106593')
