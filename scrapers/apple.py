import asyncio
import re

from playwright.async_api import async_playwright, Page, Response

BASE_URL = "https://jobs.apple.com/en-us/search?location=united-states-USA&sort=newest"
JOB_CARD_SELECTOR = "div.job-title-link"
NEXT_BUTTON_SELECTOR = "a[aria-label='Next page'], button[aria-label='Next page'], a[aria-label='Next Page'], button[aria-label='Next Page']"

# Captured API responses (if Apple loads jobs via XHR we intercept them here)
_intercepted: list[dict] = []


async def _maybe_capture_response(response: Response):
    if "jobs.apple.com" in response.url and response.status == 200:
        ct = response.headers.get("content-type", "")
        if "json" in ct:
            try:
                data = await response.json()
                _intercepted.append({"url": response.url, "data": data})
            except Exception:
                pass


async def _extract_jobs_from_dom(page: Page) -> list[dict]:
    return await page.evaluate("""
        () => {
            const cards = document.querySelectorAll('div.job-title-link');
            return Array.from(cards).map(card => {
                const a = card.querySelector('h3 a');
                if (!a) return null;

                const title = a.innerText.trim();
                const href  = a.getAttribute('href') || '';

                const roleMatch = href.match(/\\/details\\/([^/?]+)/);
                const role_id   = roleMatch ? 'apple_' + roleMatch[1] : '';

                const teamCodeMatch = href.match(/[?&]team=([^&]+)/);
                const team_code = teamCodeMatch ? teamCodeMatch[1] : '';

                const team_name = (card.querySelector('span.team-name') || {}).innerText || '';
                const posted_date = (card.querySelector('span.job-posted-date') || {}).innerText || '';

                // Location lives in a sibling div of the card's parent row
                const row = card.parentElement;
                let location = '';
                if (row) {
                    const locEl = row.querySelector('[class*="location"], [id*="location"], span[id*="Location"]');
                    if (locEl) {
                        location = locEl.innerText.replace(/^Location\\s*/i, '').trim();
                    } else {
                        // fallback: grab all text from row, extract after "Location"
                        const rowText = row.innerText;
                        const locMatch = rowText.match(/Location([^\\n]+)/);
                        if (locMatch) location = locMatch[1].trim();
                    }
                }

                return { role_id, title, team: team_name || team_code,
                         location, posted_date,
                         url: href ? 'https://jobs.apple.com' + href : '',
                         company: 'Apple' };
            }).filter(j => j && j.role_id && j.title);
        }
    """)


async def _get_total_pages(page: Page) -> int:
    try:
        text = await page.inner_text("span.pageNumber, [class*='pagination'] span, nav[aria-label*='pagination']")
        nums = re.findall(r"\d+", text)
        if nums:
            return int(nums[-1])
    except Exception:
        pass
    return 1


async def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    _intercepted.clear()

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
        page.on("response", lambda r: asyncio.ensure_future(_maybe_capture_response(r)))

        print(f"[apple] Loading {BASE_URL}")
        await page.goto(BASE_URL, wait_until="networkidle", timeout=60_000)

        # Give React time to hydrate
        await page.wait_for_timeout(2000)

        # Check if we intercepted a JSON API — if so, use that instead
        if _intercepted:
            print(f"[apple] Found {len(_intercepted)} JSON API response(s) — using API data")
            return _parse_from_api(_intercepted)

        # Fall back to DOM scraping
        page_num = 1
        while True:
            print(f"[apple] Scraping page {page_num}...")

            try:
                await page.wait_for_selector(JOB_CARD_SELECTOR, timeout=15_000)
            except Exception:
                print(f"[apple] No job rows found on page {page_num}, stopping.")
                break

            jobs = await _extract_jobs_from_dom(page)
            if not jobs:
                print(f"[apple] 0 jobs extracted on page {page_num}, stopping.")
                break

            all_jobs.extend(jobs)
            print(f"[apple] Page {page_num}: {len(jobs)} jobs (total {len(all_jobs)})")

            # Try to go to next page
            next_btn = page.locator(NEXT_BUTTON_SELECTOR)
            if await next_btn.count() == 0:
                break
            is_disabled = await next_btn.get_attribute("aria-disabled")
            if is_disabled == "true":
                break

            await next_btn.click()
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await page.wait_for_timeout(1000)
            page_num += 1

        await browser.close()

    print(f"[apple] Done. {len(all_jobs)} total jobs scraped.")
    return all_jobs


def _parse_from_api(intercepted: list[dict]) -> list[dict]:
    """Parse jobs from intercepted JSON API responses."""
    jobs = []
    for entry in intercepted:
        data = entry["data"]
        # Handle common API shapes
        raw_jobs = []
        if isinstance(data, list):
            raw_jobs = data
        elif isinstance(data, dict):
            for key in ("results", "roles", "jobs", "data", "items"):
                if key in data and isinstance(data[key], list):
                    raw_jobs = data[key]
                    break

        for j in raw_jobs:
            raw_id = str(j.get("positionId") or j.get("roleId") or j.get("id") or "")
            role_id = f"apple_{raw_id}" if raw_id else ""
            title = j.get("postingTitle") or j.get("title") or j.get("name") or ""
            team = j.get("team", {})
            if isinstance(team, dict):
                team = team.get("teamCode") or team.get("name") or ""
            location = j.get("location") or j.get("locationName") or ""
            if isinstance(location, dict):
                location = location.get("name") or ""
            posted_date = j.get("postingDate") or j.get("postedDate") or ""
            url = f"https://jobs.apple.com/en-us/details/{raw_id}" if raw_id else ""
            if role_id and title:
                jobs.append({
                    "role_id": role_id,
                    "title": title,
                    "team": team,
                    "location": location,
                    "posted_date": posted_date,
                    "url": url,
                    "company": "Apple",
                })
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)
