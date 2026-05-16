import asyncio
import re
from curl_cffi.requests import AsyncSession

BASE_URL = "https://robopgh.org/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _parse_field(item_html: str, field: str) -> str:
    m = re.search(
        rf'fs-cmsfilter-field="{re.escape(field)}"[^>]*>(.*?)</\w+>',
        item_html,
        re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else ""


def _parse_items(html: str) -> list[dict]:
    chunks = html.split('<div role="listitem" class="w-dyn-item">')
    jobs = []
    for chunk in chunks[1:]:
        # URL
        m = re.search(r'href="(https?://[^"]+)"[^>]*class="job-board-list_item-link', chunk)
        if not m:
            m = re.search(r'class="job-board-list_item-link[^"]*"[^>]*href="(https?://[^"]+)"', chunk)
        url = m.group(1).strip() if m else ""

        title   = _parse_field(chunk, "JobTitle")
        company = _parse_field(chunk, "Employer")
        city    = _parse_field(chunk, "City")
        state   = _parse_field(chunk, "State")
        jtype   = _parse_field(chunk, "Type")

        if not title or not url:
            continue

        location = ", ".join(filter(None, [city, state])) or "Pittsburgh, PA"
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40]
        co_slug = re.sub(r"[^a-z0-9]+", "_", company.lower())[:20] if company else "robopgh"
        role_id = f"robopgh_{co_slug}_{slug}_{abs(hash(url)) % 100000}"

        jobs.append({
            "role_id":     role_id,
            "title":       title,
            "team":        jtype,
            "location":    location,
            "posted_date": "",
            "url":         url,
            "company":     company or "RoboPGH",
            "experience":  "",
        })
    return jobs


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        page = 1
        all_jobs: list[dict] = []
        seen_ids: set[str] = set()

        while True:
            params = {} if page == 1 else {"1db4616d_page": page}
            r = await session.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"[robopgh] page {page} -> {r.status_code}, stopping")
                break

            html = r.text
            items = _parse_items(html)
            if not items:
                break

            for j in items:
                if j["role_id"] not in seen_ids:
                    seen_ids.add(j["role_id"])
                    all_jobs.append(j)

            # Finsweet pagination: next page link exists only when there are more pages
            has_next = f'"1db4616d_page":{page + 1}' in html or f"1db4616d_page={page + 1}" in html
            # Fallback: if we got a full page of 20 items, try next
            if not has_next and len(items) < 20:
                break
            page += 1

    print(f"[robopgh] Done. {len(all_jobs)} jobs across {page} pages.")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["company"], "|", j["location"])
    print(f"Total: {len(jobs)}")
