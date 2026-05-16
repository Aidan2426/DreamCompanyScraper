import asyncio
import re
from datetime import date, timedelta
from curl_cffi.requests import AsyncSession

API_URL  = "https://leidos.wd5.myworkdayjobs.com/wday/cxs/leidos/External/jobs"
JOB_BASE = "https://leidos.wd5.myworkdayjobs.com/External"
HEADERS  = {
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "Referer":      JOB_BASE,
}
LIMIT = 20
MAX_OFFSET = 2000  # API wraps after this


def _parse_posted_on(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    today = date.today()
    if "today" in s:
        return today.strftime("%b %d, %Y")
    m = re.search(r"(\d+)\+?\s*day", s)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%b %d, %Y")
    return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.post(
            API_URL,
            json={"limit": LIMIT, "offset": 0, "searchText": "", "locations": []},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        data0 = r0.json()
        raw   = data0.get("jobPostings", [])
        print(f"[leidos] fetching up to {MAX_OFFSET} jobs (API cap)")

        sem = asyncio.Semaphore(8)

        async def _fetch(offset):
            async with sem:
                r = await session.post(
                    API_URL,
                    json={"limit": LIMIT, "offset": offset, "searchText": "", "locations": []},
                    headers=HEADERS,
                    timeout=30,
                )
                if r.status_code == 200 and r.text:
                    return r.json().get("jobPostings", [])
                return []

        pages = await asyncio.gather(*[_fetch(off) for off in range(LIMIT, MAX_OFFSET, LIMIT)])
        for page in pages:
            raw.extend(page)

    seen = set()
    jobs = []
    for j in raw:
        bullets  = j.get("bulletFields") or []
        req_id   = bullets[0].strip() if bullets else ""
        title    = (j.get("title") or "").strip()
        ext_path = (j.get("externalPath") or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)
        jobs.append({
            "role_id":     f"leidos_{req_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("locationsText") or "").strip(),
            "posted_date": _parse_posted_on(j.get("postedOn") or ""),
            "url":         JOB_BASE + ext_path if ext_path else "",
            "company":     "Leidos",
            "experience":  "",
        })

    print(f"[leidos] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
