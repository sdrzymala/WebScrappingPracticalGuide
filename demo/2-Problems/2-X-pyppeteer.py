import asyncio
from pyppeteer import launch

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.similarweb.com/top-websites/poland')
    await page.screenshot({'path': 'pyppeteer.png'})
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())