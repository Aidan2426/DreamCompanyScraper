"""Find Meta Careers API endpoint and payload."""
import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.metacareers.com/jobsearch/"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))

        api_calls = []

        async def capture(response):
            try:
                ct = response.headers.get("content-type", "")
                if response.status == 200 and ("json" in ct or "graphql" in response.url):
                    body = await response.body()
                    text = body.decode("utf-8", errors="ignore")
                    if any(k in text for k in ('"jobs"', '"results"', '"edges"', '"nodes"', '"title"')):
                        api_calls.append({
                            "url":    response.url,
                            "method": response.request.method,
                            "status": response.status,
                            "preview": text[:500],
                        })
            except Exception:
                pass

        page.on("response", lambda r: asyncio.ensure_future(capture(r)))

        print(f"Loading {URL}...")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        print(f"\n=== API CALLS WITH JOB DATA ({len(api_calls)} found) ===")
        for c in api_calls[:5]:
            print(f"\nURL: {c['url']}")
            print(f"Method: {c['method']}")
            print(f"Preview: {c['preview'][:300]}")
            print("-" * 60)

        # Also capture request payloads (POST bodies)
        post_bodies = []
        async def capture_request(request):
            if request.method == "POST" and "meta" in request.url:
                try:
                    body = request.post_data
                    if body:
                        post_bodies.append({"url": request.url, "body": body[:500]})
                except Exception:
                    pass

        page.on("request", lambda r: asyncio.ensure_future(capture_request(r)))

        # Reload to capture requests too
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)

        print(f"\n=== POST REQUESTS TO META ({len(post_bodies)} found) ===")
        for p in post_bodies[:5]:
            print(f"\nURL: {p['url']}")
            print(f"Body: {p['body'][:400]}")
            print("-" * 60)

        await browser.close()

asyncio.run(main())
