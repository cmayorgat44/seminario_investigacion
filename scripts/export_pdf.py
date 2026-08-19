import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Absolute path to the presentation HTML
        file_path = f"file://{os.path.abspath('docs/presentacion_favar.html')}?print-pdf"
        
        print(f"Loading {file_path}...")
        await page.goto(file_path, wait_until='networkidle')
        
        # Give reveal.js a few seconds to render all slides in print mode
        await page.wait_for_timeout(3000)
        
        output_path = "docs/presentacion_favar.pdf"
        print(f"Exporting to {output_path}...")
        
        await page.pdf(
            path=output_path,
            width='1920px',
            height='1080px',
            print_background=True,
            landscape=True
        )
        print("Done!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
