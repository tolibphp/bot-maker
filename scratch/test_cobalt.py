import asyncio
import aiohttp

async def test_cobalt():
    url = 'https://www.tiktok.com/@zachking/video/6829303562506079493'
    # Cobalt API docs: POST /api/json
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        'url': url,
        'vCodec': 'h264'
    }
    # Let's use a known public instance
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.cobalt.tools/api/json', json=payload, headers=headers) as resp:
            print(resp.status)
            text = await resp.text()
            print(text)

asyncio.run(test_cobalt())
