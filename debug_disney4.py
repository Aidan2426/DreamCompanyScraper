"""Parse Disney careers HTML for job items."""
import asyncio, re
from playwright.async_api import async_playwright

URL = "https://www.disneycareers.com/en/search-jobs"


async def debug():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))
        await page.goto(URL, wait_until="load", timeout=60_000)
        await page.wait_for_timeout(8000)

        content = await page.content()

        # Dump a large section of HTML around job listings
        # Try to find "job-result" or "requisition"
        patterns = ["job-result", "requisitionId", "job_id", "postingId", "job-listing", "search-result", "job-card", "job__title", "job-title", "careers__list"]
        for pat in patterns:
            idx = content.find(pat)
            if idx >= 0:
                print(f"=== Found '{pat}' at index {idx} ===")
                print(content[max(0, idx-200):idx+1000])
                print("\n")
                break

        # Dump all unique CSS class names from job-related elements
        # Try to count occurrences of common patterns
        for pat in patterns:
            count = content.count(pat)
            if count:
                print(f"'{pat}' appears {count} times")

        # Also look for <li> with data attributes
        li_with_data = re.findall(r'<li[^>]+data-[^>]+>', content)
        print(f"\n<li> with data- attributes: {len(li_with_data)}")
        for item in li_with_data[:3]:
            print(item[:200])

        # Find all anchor tags that contain "search-jobs" in href
        job_links = re.findall(r'<a[^>]+href="[^"]*search-jobs[^"]*"[^>]*>', content)
        print(f"\nJob links: {len(job_links)}")
        for lnk in job_links[:5]:
            print(lnk[:200])

        # Save full HTML to file for inspection
        with open("disney_page.html", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nFull HTML saved to disney_page.html ({len(content)} chars)")

        await browser.close()

asyncio.run(debug())
