"""Find OpenAI careers API - check both openai.com and ashby."""
import asyncio
from playwright.async_api import async_playwright

URLS = [
    "https://openai.com/careers/search/",
    "https://jobs.ashbyhq.com/openai",
]


async def debug_url(url: str):
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
                    if any(k in text for k in ('"title"', '"jobPostings"', '"jobs"', '"postings"')):
                        hits.append({"url": response.url, "preview": text[:800]})
            except Exception:
                pass

        async def cap_request(request):
            if request.method == "POST":
                try:
                    body = request.post_data or ""
                    post_bodies.append({"url": request.url, "body": body[:800]})
                except Exception:
                    pass

        page.on("response", lambda r: asyncio.ensure_future(cap_response(r)))
        page.on("request",  lambda r: asyncio.ensure_future(cap_request(r)))

        print(f"\n{'='*60}\nLoading {url}...")
        await page.goto(url, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        print(f"=== RESPONSES WITH JOB DATA ({len(hits)}) ===")
        for h in hits[:3]:
            print(f"URL: {h['url']}")
            print(f"Preview: {h['preview'][:500]}\n{'-'*40}")

        print(f"\n=== POST BODIES ({len(post_bodies)}) ===")
        for p in post_bodies[:3]:
            print(f"URL: {p['url']}")
            print(f"Body: {p['body']}\n{'-'*40}")

        await browser.close()


async def main():
    for url in URLS:
        await debug_url(url)

asyncio.run(main())
