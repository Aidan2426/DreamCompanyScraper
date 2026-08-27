import asyncio
import re

from datetime import datetime, timedelta, timezone

from playwright.async_api import async_playwright, Page

BASE_URL = "https://apply.careers.microsoft.com/careers"
SEARCH_PARAMS = "pid=1970393556859892&sort_by=timestamp"
PAGE_SIZE = 20

_REL_RE = re.compile(r"(\d+|an?)\s+(minute|hour|day|week|month)s?\s+ago", re.IGNORECASE)


def _relative_to_iso(text: str, now: datetime) -> str:
    """Microsoft's site renders posted_date as relative text ('2 hours ago') that
    the frontend would otherwise re-interpret against the viewer's clock every time
    the page loads, making jobs look freshly posted no matter how old they are.
    Resolve it to a fixed absolute timestamp at scrape time instead."""
    if not text:
        return ""
    t = text.strip().lower()
    if t in ("today", "just posted", "posted today"):
        return now.strftime("%Y-%m-%d")
    if t == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    m = _REL_RE.search(t)
    if not m:
        return text
    n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
    unit = m.group(2)
    delta = {
        "minute": timedelta(minutes=n),
        "hour": timedelta(hours=n),
        "day": timedelta(days=n),
        "week": timedelta(weeks=n),
        "month": timedelta(days=n * 30),
    }[unit]
    return (now - delta).strftime("%Y-%m-%d")


async def _get_total_jobs(page: Page) -> int:
    try:
        text = await page.inner_text('[data-testid="job-count"]')
        m = re.search(r"([\d,]+)", text)
        return int(m.group(1).replace(",", "")) if m else 0
    except Exception:
        return 0


async def _extract_jobs_from_dom(page: Page) -> list[dict]:
    return await page.evaluate("""
        () => {
            const cards = document.querySelectorAll('div[data-test-id="job-listing"]');
            return Array.from(cards).map(card => {
                const linkEl  = card.querySelector('a.card-F1ebU');
                const href    = linkEl ? linkEl.getAttribute('href') : '';
                const fullUrl = href
                    ? (href.startsWith('http') ? href : 'https://apply.careers.microsoft.com' + href)
                    : '';

                const roleMatch = href ? href.match(/\\/job\\/(\\d+)/) : null;
                const role_id   = roleMatch ? 'microsoft_' + roleMatch[1] : '';

                const titleEl = card.querySelector('div.title-1aNJK');
                const title   = titleEl ? titleEl.innerText.trim() : '';

                const locEl   = card.querySelector('div.fieldValue-3kEar');
                const location = locEl ? locEl.innerText.trim() : '';

                const dateEl  = card.querySelector('div.subData-13Lm1');
                const posted_date = dateEl ? dateEl.innerText.replace(/^Posted\\s*/i, '').trim() : '';

                return { role_id, title, team: '', location, posted_date,
                         url: fullUrl, company: 'Microsoft' };
            }).filter(j => j.role_id && j.title);
        }
    """)


async def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    scrape_time = datetime.now(timezone.utc)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        print("[microsoft] Loading page 1...")
        await page.goto(f"{BASE_URL}?start=0&{SEARCH_PARAMS}", wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)

        total = await _get_total_jobs(page)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        print(f"[microsoft] {total} jobs across {total_pages} pages")

        start = 0
        page_num = 1
        while start < total:
            if page_num > 1:
                url = f"{BASE_URL}?start={start}&{SEARCH_PARAMS}"
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(1000)

            try:
                await page.wait_for_selector('div[data-test-id="job-listing"]', timeout=15_000)
            except Exception:
                print(f"[microsoft] Page {page_num}: no cards found, stopping")
                break

            jobs = await _extract_jobs_from_dom(page)
            if not jobs:
                print(f"[microsoft] Page {page_num}: 0 jobs extracted, stopping")
                break

            for j in jobs:
                j["posted_date"] = _relative_to_iso(j["posted_date"], scrape_time)

            all_jobs.extend(jobs)
            print(f"[microsoft] Page {page_num}/{total_pages}: {len(jobs)} jobs (total {len(all_jobs)})")

            start += PAGE_SIZE
            page_num += 1

        await browser.close()

    print(f"[microsoft] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)
