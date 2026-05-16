import asyncio
import re
import json
from datetime import datetime
from curl_cffi.requests import AsyncSession

SEARCH_URL = "https://www.indeed.com/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

KEYWORDS = [
    "software engineer",
    "software developer",
    "data engineer",
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "devops engineer",
    "cloud engineer",
    "cybersecurity analyst",
    "network engineer",
    "systems engineer",
    "database administrator",
    "QA engineer",
    "full stack developer",
    "IT analyst",
]

LOCATION = "Pittsburgh, PA"
FROM_AGE = "1"  # past 24 hours


def _fmt_date(ms: int) -> str:
    if not ms:
        return ""
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%b %d, %Y")
    except Exception:
        return ""


def _extract(html: str) -> list[dict]:
    m = re.search(
        r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*(\{.*?\});\s*window\.mosaic',
        html,
        re.S,
    )
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []
    return data.get("metaData", {}).get("mosaicProviderJobCardsModel", {}).get("results", [])


async def _fetch(session: AsyncSession, keyword: str, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        params = {"q": keyword, "l": LOCATION, "fromage": FROM_AGE, "start": 0}
        r = await session.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return _extract(r.text)


async def scrape() -> list[dict]:
    seen: set[str] = set()
    jobs: list[dict] = []

    sem = asyncio.Semaphore(2)
    async with AsyncSession(impersonate="chrome124") as session:
        tasks = [_fetch(session, kw, sem) for kw in KEYWORDS]
        results = await asyncio.gather(*tasks)

    for batch in results:
        for j in batch:
            jobkey = (j.get("jobkey") or "").strip()
            title = (j.get("displayTitle") or j.get("title") or "").strip()
            if not jobkey or not title or jobkey in seen:
                continue
            seen.add(jobkey)
            jobs.append({
                "role_id":     f"indeed_{jobkey}",
                "title":       title,
                "team":        "",
                "location":    (j.get("formattedLocation") or "").strip(),
                "posted_date": _fmt_date(j.get("pubDate") or 0),
                "url":         f"https://www.indeed.com/viewjob?jk={jobkey}",
                "company":     (j.get("company") or "").strip(),
                "experience":  "",
            })

    print(f"[indeed] Done. {len(jobs)} unique jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:10]:
        print(j["title"], "|", j["company"], "|", j["location"])
    print(f"Total: {len(jobs)}")
