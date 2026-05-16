import asyncio
import re
from datetime import datetime

from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

BASE_URL  = "https://uscareershub-fujifilm.icims.com/jobs/search"
TOTAL_PAGES = 13
CONCURRENCY = 5


def _fmt_date(raw: str) -> str:
    # raw looks like "4/28/2026 1:01 PM" (from title attr) or "(4/28/2026 1:01 PM)"
    m = re.search(r"(\d+/\d+/\d{4})", raw)
    if not m:
        return ""
    try:
        return datetime.strptime(m.group(1), "%m/%d/%Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _clean_url(href: str) -> str:
    return re.sub(r"[?&](?:hub=\d+|in_iframe=\d+)(&|$)", r"\1", href).rstrip("?&")


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("li.iCIMS_JobCardItem"):
        # Title + URL
        anchor = card.select_one("a.iCIMS_Anchor")
        if not anchor:
            continue
        title = anchor.select_one("h3")
        title = title.get_text(strip=True) if title else ""
        href  = anchor.get("href", "")
        if not title or not href:
            continue

        # Job ID from URL path
        id_match = re.search(r"/jobs/(\d+)/", href)
        job_id = id_match.group(1) if id_match else ""
        if not job_id:
            continue

        # Location
        loc_label = card.find("span", string=re.compile(r"Job Locations", re.I))
        location = ""
        if loc_label:
            loc_span = loc_label.find_next_sibling("span")
            if loc_span:
                location = loc_span.get_text(strip=True)

        # Date from title attr on the outer span in the date column
        date_outer = card.select_one("div.header.right span[title]")
        posted = _fmt_date(date_outer.get("title", "") if date_outer else "")

        jobs.append({
            "role_id":     f"fujifilm_{job_id}",
            "title":       title,
            "team":        "",
            "location":    location,
            "posted_date": posted,
            "url":         _clean_url(href),
            "company":     "Fujifilm",
        })
    return jobs


async def _fetch_page(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        r = await session.get(
            BASE_URL,
            params={"ss": "1", "pr": page, "in_iframe": "1"},
            timeout=30,
        )
        r.raise_for_status()
        return _parse_page(r.text)


async def scrape() -> list[dict]:
    sem = asyncio.Semaphore(CONCURRENCY)
    async with AsyncSession(impersonate="chrome124") as session:
        results = await asyncio.gather(*[_fetch_page(session, sem, p) for p in range(TOTAL_PAGES)])

    seen = set()
    jobs = []
    for batch in results:
        for j in batch:
            if j["role_id"] not in seen:
                seen.add(j["role_id"])
                jobs.append(j)

    print(f"[fujifilm] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
