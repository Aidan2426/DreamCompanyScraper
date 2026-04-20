import asyncio
import re

from playwright.async_api import async_playwright, Page, Response

BASE_URL = "https://www.google.com/about/careers/applications/jobs/results/"
JOB_CARD_SELECTOR = "li.lLd3Je"

_intercepted: list[dict] = []


async def _maybe_capture_response(response: Response):
    if "careers/applications" in response.url and response.status == 200:
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
            const cards = document.querySelectorAll('li.lLd3Je');
            return Array.from(cards).map(card => {
                const titleEl = card.querySelector('h3.QJPWVe');
                const title   = titleEl ? titleEl.innerText.trim() : '';

                const linkEl  = card.querySelector('a.WpHeLc');
                const href    = linkEl ? linkEl.getAttribute('href') : '';
                const fullUrl = href
                    ? (href.startsWith('http') ? href : 'https://www.google.com/about/careers/applications/' + href)
                    : '';

                const roleMatch = href ? href.match(/jobs\\/results\\/([^?/]+)/) : null;
                const role_id   = roleMatch ? roleMatch[1] : '';

                // Dedupe locations — Google renders same span twice
                const locEls  = card.querySelectorAll('span.r0wTof');
                const locSet  = [...new Set(Array.from(locEls).map(e => e.innerText.trim()).filter(Boolean))];
                const location = locSet.join(' | ');

                // Org — span.RP7SMd contains icon + span text
                const orgEl   = card.querySelector('span.RP7SMd > span:last-child');
                const team    = orgEl ? orgEl.innerText.trim() : '';

                // Experience level
                const expEl   = card.querySelector('span.wVSTAb');
                const experience = expEl ? expEl.innerText.trim() : '';

                return { role_id, title, team, location,
                         posted_date: '', experience,
                         url: fullUrl, company: 'Google' };
            }).filter(j => j.role_id && j.title);
        }
    """)


async def _get_total_pages(page: Page) -> int:
    try:
        text = await page.inner_text("body")
        m = re.search(r"of\s+([\d,]+)", text)
        if m:
            total = int(m.group(1).replace(",", ""))
            return (total + 19) // 20
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

        print(f"[google] Loading page 1...")
        await page.goto(BASE_URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)

        if _intercepted:
            print(f"[google] Found JSON API — using it")
            await browser.close()
            return _parse_from_api(_intercepted)

        total_pages = await _get_total_pages(page)
        print(f"[google] {total_pages} pages to scrape")

        for page_num in range(1, total_pages + 1):
            if page_num > 1:
                url = f"{BASE_URL}?page={page_num}"
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(1000)

            jobs = await _extract_jobs_from_dom(page)
            if not jobs:
                print(f"[google] Page {page_num}: 0 jobs — stopping")
                break

            all_jobs.extend(jobs)
            print(f"[google] Page {page_num}/{total_pages}: {len(jobs)} jobs (total {len(all_jobs)})")

        await browser.close()

    print(f"[google] Done. {len(all_jobs)} total jobs.")
    return all_jobs


def _parse_from_api(intercepted: list[dict]) -> list[dict]:
    jobs = []
    for entry in intercepted:
        data = entry["data"]
        raw = []
        if isinstance(data, list):
            raw = data
        elif isinstance(data, dict):
            for key in ("jobs", "results", "data", "items"):
                if key in data and isinstance(data[key], list):
                    raw = data[key]
                    break
        for j in raw:
            role_id = str(j.get("id") or j.get("jobId") or "")
            title   = j.get("title") or j.get("jobTitle") or ""
            team    = j.get("organization") or j.get("team") or j.get("department") or ""
            loc     = j.get("location") or j.get("locations") or ""
            if isinstance(loc, list):
                loc = " | ".join(loc)
            posted  = j.get("date") or j.get("postedDate") or ""
            url     = j.get("url") or (f"https://www.google.com/about/careers/applications/jobs/results/{role_id}" if role_id else "")
            if role_id and title:
                jobs.append({"role_id": role_id, "title": title, "team": team,
                             "location": loc, "posted_date": posted,
                             "url": url, "company": "Google"})
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)
