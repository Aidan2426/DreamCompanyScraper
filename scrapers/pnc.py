import asyncio
import re
from datetime import datetime, timedelta, timezone

from curl_cffi.requests import AsyncSession

API_URL  = "https://pnc.wd5.myworkdayjobs.com/wday/cxs/pnc/External/jobs"
JOB_BASE = "https://pnc.wd5.myworkdayjobs.com/External"
HEADERS  = {
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "Referer":      "https://pnc.wd5.myworkdayjobs.com/External",
}
LIMIT       = 20
CONCURRENCY = 10

_REL_RE = re.compile(r"(\d+)?\+?\s*(day|week|month)s?\s+ago", re.IGNORECASE)


def _posted_on_to_iso(text: str, now: datetime) -> str:
    """Workday's postedOn is relative text ("Posted Today", "Posted 30+ Days Ago")
    that would otherwise get re-interpreted against the viewer's clock on every
    page load. Resolve it to a fixed date at scrape time instead."""
    if not text:
        return ""
    t = text.strip().lower().removeprefix("posted").strip()
    if t == "today":
        return now.strftime("%Y-%m-%d")
    if t == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    m = _REL_RE.search(t)
    if not m:
        return ""
    n = int(m.group(1)) if m.group(1) else 1
    unit = m.group(2)
    delta = {"day": timedelta(days=n), "week": timedelta(weeks=n), "month": timedelta(days=n * 30)}[unit]
    return (now - delta).strftime("%Y-%m-%d")


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore,
                 offset: int, facet_id: str = None) -> list[dict]:
    async with sem:
        body = {"limit": LIMIT, "offset": offset, "searchText": "", "locations": []}
        if facet_id:
            body["appliedFacets"] = {"jobFamilyGroup": [facet_id]}
        r = await session.post(API_URL, json=body, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json().get("jobPostings", [])


async def _fetch_facet(session: AsyncSession, sem: asyncio.Semaphore,
                       facet_id: str, total: int) -> list[dict]:
    """Fetch all pages for one jobFamilyGroup facet."""
    first_page = await _fetch(session, sem, 0, facet_id)
    if total <= LIMIT:
        return first_page
    rest = await asyncio.gather(*[
        _fetch(session, sem, offset, facet_id)
        for offset in range(LIMIT, total, LIMIT)
    ])
    return first_page + [j for page in rest for j in page]


async def scrape() -> list[dict]:
    scrape_time = datetime.now(timezone.utc)
    async with AsyncSession(impersonate="chrome124") as session:
        # First request: get facet list
        r0 = await session.post(
            API_URL,
            json={"limit": 1, "offset": 0, "searchText": "", "locations": []},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        data0 = r0.json()

        facets = next(
            (f["values"] for f in data0.get("facets", [])
             if f.get("facetParameter") == "jobFamilyGroup"),
            []
        )
        print(f"[pnc] {len(facets)} jobFamilyGroup facets, total jobs ~{data0.get('total')}")

        sem = asyncio.Semaphore(CONCURRENCY)
        results = await asyncio.gather(*[
            _fetch_facet(session, sem, fv["id"], fv["count"])
            for fv in facets
        ])

    raw = [j for page in results for j in page]

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
            "role_id":     f"pnc_{req_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("locationsText") or "").strip(),
            "posted_date": _posted_on_to_iso(j.get("postedOn") or "", scrape_time),
            "url":         JOB_BASE + ext_path if ext_path else "",
            "company":     "PNC",
        })

    print(f"[pnc] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
