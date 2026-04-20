"""Find Anthropic careers API."""
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

        hits = []
        post_bodies = []

        async def cap_response(response):
            try:
                if response.status == 200:
                    body = await response.body()
                    text = body.decode("utf-8", errors="ignore")
                    if any(k in text for k in ('"title"', '"jobs"', '"postings"', '"positions"', '"department"', '"opening"')):
                        hits.append({"url": response.url, "preview": text[:1200]})
            except Exception:
                pass

        async def cap_request(request):
            if request.method == "POST":
                try:
                    body = request.post_data or ""
                    post_bodies.append({"url": request.url, "body": body[:800], "headers": dict(request.headers)})
                except Exception:
                    pass

        page.on("response", lambda r: asyncio.ensure_future(cap_response(r)))
        page.on("request",  lambda r: asyncio.ensure_future(cap_request(r)))

        print(f"Loading {URL}...")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        print(f"\n=== RESPONSES WITH JOB DATA ({len(hits)}) ===")
        for h in hits[:5]:
            print(f"URL: {h['url']}")
            print(f"Preview: {h['preview'][:800]}")
            print("-" * 60)

        print(f"\n=== POST BODIES ({len(post_bodies)}) ===")
        for p in post_bodies[:5]:
            print(f"URL: {p['url']}")
            print(f"Body: {p['body']}")
            print("-" * 60)

        # Also dump page HTML snippet to find selectors
        content = await page.content()
        # Find job-related sections
        idx = content.find("job")
        if idx > 0:
            print(f"\n=== HTML AROUND 'job' ===\n{content[max(0,idx-200):idx+500]}")

        await browser.close()

asyncio.run(debug())
