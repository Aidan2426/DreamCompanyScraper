"""Explore Disney TalentBrew search API and HTML job selectors."""
import asyncio, json
from playwright.async_api import async_playwright

URL = "https://www.disneycareers.com/en/search-jobs"


async def debug():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))

        disney_hits = []

        async def cap_response(response):
            try:
                url = response.url
                if "disneycareers.com" in url and response.status == 200:
                    body = await response.body()
                    text = body.decode("utf-8", errors="ignore")
                    disney_hits.append({"url": url, "preview": text[:2000]})
            except Exception:
                pass

        page.on("response", lambda r: asyncio.ensure_future(cap_response(r)))

        await page.goto(URL, wait_until="load", timeout=60_000)
        await page.wait_for_timeout(8000)

        print(f"=== DISNEY RESPONSES ({len(disney_hits)}) ===")
        for h in disney_hits:
            print(f"\nURL: {h['url']}")
            print(f"Preview: {h['preview'][:600]}")
            print("-" * 60)

        # Extract job items from DOM
        print("\n=== JOB ITEMS IN DOM ===")
        for sel in [
            "[class*='job-result']",
            "[class*='job-listing']",
            ".job-result",
            "li[data-job-id]",
            "[data-jobid]",
            "article.job",
            ".search-result-item",
            ".job-card",
        ]:
            count = await page.locator(sel).count()
            if count:
                print(f"'{sel}': {count} items")
                html = await page.locator(sel).first.inner_html()
                print(f"HTML: {html[:400]}")

        # Dump section of page HTML around job results
        content = await page.content()
        for marker in ["job-result", "search-result", "requisition", "jobId", "data-job-id"]:
            idx = content.find(marker)
            if idx >= 0:
                print(f"\n=== '{marker}' at HTML[{idx}] ===")
                print(content[max(0,idx-50):idx+600])
                break

        await browser.close()

asyncio.run(debug())
