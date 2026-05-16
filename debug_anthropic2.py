"""Inspect Anthropic careers DOM for job selectors."""
import asyncio
from playwright.async_api import async_playwright

URL = "https://www.anthropic.com/careers/jobs"


async def debug():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)

        # Find all anchor tags that look like job links
        links = await page.eval_on_selector_all("a[href*='/careers/']", """
            els => els.map(e => ({
                href: e.href,
                text: e.textContent.trim().slice(0, 100)
            }))
        """)
        print(f"Career links found: {len(links)}")
        for l in links[:10]:
            print(l)

        # Check for job rows/items
        # Try common patterns
        for sel in [
            "a[href*='/careers/jobs/']",
            "[class*='jobRow']",
            "[class*='job-row']",
            "[class*='opening']",
            "[class*='role']",
            "li a[href*='careers']",
        ]:
            count = await page.locator(sel).count()
            if count:
                print(f"\nSelector '{sel}': {count} matches")
                # Get first element HTML
                html = await page.locator(sel).first.inner_html()
                print(f"First element HTML: {html[:300]}")

        # Dump a section of the full HTML around job listings
        content = await page.content()
        # Find team group
        idx = content.find("teamGroup")
        if idx > 0:
            print(f"\n=== teamGroup HTML ===\n{content[idx:idx+2000]}")

        await browser.close()

asyncio.run(debug())
