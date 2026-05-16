"""Find Disney careers API."""
import asyncio
from playwright.async_api import async_playwright

URL = "https://www.disneycareers.com/en/search-jobs"


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
                    ct = response.headers.get("content-type", "")
                    if "json" in ct or "javascript" in ct:
                        body = await response.body()
                        text = body.decode("utf-8", errors="ignore")
                        if any(k in text for k in ('"title"', '"jobs"', '"postings"', '"positions"', '"requisition"', '"jobId"')):
                            hits.append({"url": response.url, "preview": text[:1500]})
            except Exception:
                pass

        async def cap_request(request):
            try:
                post_bodies.append({
                    "url": request.url,
                    "method": request.method,
                    "body": (request.post_data or "")[:800],
                })
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
            print(f"Preview: {h['preview'][:1000]}")
            print("-" * 60)

        print(f"\n=== ALL REQUESTS (POST/XHR) ===")
        for p in post_bodies:
            if p["method"] in ("POST", "GET") and any(k in p["url"] for k in ("api", "search", "job", "career", "talent")):
                print(f"[{p['method']}] {p['url']}")
                if p["body"]:
                    print(f"  Body: {p['body'][:400]}")

        await browser.close()

asyncio.run(debug())
