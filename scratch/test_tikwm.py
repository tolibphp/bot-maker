import asyncio
import aiohttp

async def test_tikwm():
    url = 'https://www.tiktok.com/@zachking/video/6829303562506079493'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://www.tikwm.com/api/', data={'url': url}) as resp:
            text = await resp.json()
            print(text)

asyncio.run(test_tikwm())
