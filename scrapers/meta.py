import asyncio
from playwright.async_api import async_playwright, Response

URL = "https://www.metacareers.com/jobsearch/"

_job_data: list[dict] = []


async def _capture(response: Response):
    if "metacareers.com/graphql" not in response.url:
        return
    try:
        body = await response.body()
        text = body.decode("utf-8", errors="ignore")
        if "all_jobs" in text or "job_search" in text:
            import json as _json
            data = _json.loads(text)
            search = (data.get("data") or {}).get("job_search_with_featured_jobs") or {}
            jobs = search.get("all_jobs", [])
            if jobs:
                _job_data.extend(jobs)
    except Exception as e:
        pass


async def scrape() -> list[dict]:
    _job_data.clear()

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
        page.on("response", lambda r: asyncio.ensure_future(_capture(r)))

        print("[meta] Loading jobsearch page...")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        await browser.close()

    print(f"[meta] Intercepted {len(_job_data)} raw job records")

    all_jobs = []
    seen = set()
    for j in _job_data:
        raw_id = str(j.get("id", ""))
        role_id = f"meta_{raw_id}" if raw_id else ""
        if not role_id or role_id in seen:
            continue
        seen.add(role_id)

        title    = j.get("title", "").strip()
        teams    = j.get("teams", [])
        team     = ", ".join(teams) if teams else ""
        locs     = j.get("locations", [])
        location = " | ".join(locs) if locs else ""
        url      = f"https://www.metacareers.com/jobs/{raw_id}/"

        all_jobs.append({
            "role_id":    role_id,
            "title":      title,
            "team":       team,
            "location":   location,
            "posted_date": "",
            "url":        url,
            "company":    "Meta",
        })

    print(f"[meta] Done. {len(all_jobs)} unique jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)
