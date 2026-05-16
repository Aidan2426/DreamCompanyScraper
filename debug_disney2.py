"""Hunt Disney TalentBrew API - capture all non-tracker requests."""
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

        all_responses = []

        async def cap_response(response):
            try:
                url = response.url
                # Skip known trackers
                if any(x in url for x in ("google", "facebook", "doubleclick", "adobe", "adobedtm", "tbcdn", "segment")):
                    return
                ct = response.headers.get("content-type", "")
                if response.status == 200 and ("json" in ct or "text" in ct):
                    body = await response.body()
                    text = body.decode("utf-8", errors="ignore")
                    all_responses.append({"url": url, "preview": text[:600]})
            except Exception:
                pass

        page.on("response", lambda r: asyncio.ensure_future(cap_response(r)))

        print(f"Loading {URL}...")
        await page.goto(URL, wait_until="load", timeout=60_000)
        await page.wait_for_timeout(8000)

        print(f"\n=== NON-TRACKER RESPONSES ({len(all_responses)}) ===")
        for h in all_responses:
            print(f"URL: {h['url']}")
            print(f"Preview: {h['preview'][:400]}")
            print("-" * 60)

        # Look for job-related text in HTML
        content = await page.content()
        # Find first job listing
        for marker in ['"jobId"', '"requisitionId"', '"job_id"', 'data-job', 'job-listing', '"postingId"']:
            idx = content.find(marker)
            if idx >= 0:
                print(f"\n=== Found '{marker}' at {idx} ===")
                print(content[max(0, idx-100):idx+400])
                break

        # Also try clicking "View More Jobs" if present
        try:
            btn = page.locator("text=View More").first
            if await btn.count():
                print("\nClicking 'View More'...")
                await btn.click()
                await page.wait_for_timeout(3000)
                print("Clicked. Waiting for more responses...")
        except Exception as e:
            print(f"No view more button: {e}")

        await page.wait_for_timeout(3000)
        print(f"\n=== AFTER CLICK - NEW RESPONSES ===")
        for h in all_responses[-5:]:
            print(f"URL: {h['url']}")
            print(f"Preview: {h['preview'][:400]}")
            print("-" * 60)

        await browser.close()

asyncio.run(debug())
