import asyncio
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
            "posted_date": "",
            "url":         JOB_BASE + ext_path if ext_path else "",
            "company":     "PNC",
        })

    print(f"[pnc] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
