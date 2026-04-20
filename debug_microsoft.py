"""Find real DOM selectors for Microsoft Careers."""
import asyncio
from playwright.async_api import async_playwright

URL = "https://apply.careers.microsoft.com/careers?start=0&pid=1970393556859892&sort_by=timestamp"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))

        # Intercept JSON API calls
        api_hits = []
        async def capture(response):
            ct = response.headers.get("content-type", "")
            if "json" in ct and response.status == 200:
                try:
                    data = await response.json()
                    if isinstance(data, dict) and any(k in data for k in ("jobs","positions","results","hits","docs")):
                        api_hits.append({"url": response.url, "keys": list(data.keys())})
                except Exception:
                    pass
        page.on("response", lambda r: asyncio.ensure_future(capture(r)))

        print(f"Loading {URL}...")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        if api_hits:
            print("\n=== JSON API HITS ===")
            for h in api_hits:
                print(h)

        # Find job links
        links = await page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="job"], a[href*="position"], a[href*="careers"]'))
                .filter(a => a.innerText.trim().length > 5);
            return links.slice(0, 3).map(a => ({
                href:            a.getAttribute('href'),
                text:            a.innerText.trim().substring(0, 80),
                parentTag:       a.parentElement?.tagName,
                parentClass:     a.parentElement?.className?.substring(0,80),
                grandparentTag:  a.parentElement?.parentElement?.tagName,
                grandparentClass:a.parentElement?.parentElement?.className?.substring(0,80),
            }));
        }""")
        print("\n=== JOB LINKS ===")
        for l in links:
            print(l)

        # Walk up from first job link to find card container
        card_html = await page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'))
                .filter(a => a.innerText.trim().length > 10 && a.href.includes('job'));
            if (!links.length) return 'NO JOB LINKS FOUND';
            const a = links[0];
            let el = a;
            let result = '';
            for (let i = 0; i < 10; i++) {
                el = el.parentElement;
                if (!el) break;
                const text = el.innerText?.substring(0, 80).replace(/\\n/g,' ') || '';
                result += `LEVEL ${i}: ${el.tagName}.${el.className?.split(' ')[0]} | "${text}"\\n`;
            }
            // dump level where date appears
            el = a;
            for (let i=0;i<10;i++) {
                el = el.parentElement;
                if (!el) break;
                if (el.innerText?.match(/\\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec/)) {
                    result += '\\n=== DATE LEVEL ' + i + ' HTML ===\\n' + el.outerHTML.substring(0,3000);
                    break;
                }
            }
            return result;
        }""")
        print("\n=== CARD STRUCTURE ===")
        print(card_html)

        await browser.close()

asyncio.run(main())
