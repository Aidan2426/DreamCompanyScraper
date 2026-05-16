import asyncio
from curl_cffi.requests import AsyncSession

API_URL  = "https://fnbcorp.wd501.myworkdayjobs.com/wday/cxs/fnbcorp/FNBCORP/jobs"
JOB_BASE = "https://fnbcorp.wd501.myworkdayjobs.com/FNBCORP"
HEADERS  = {
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "Referer":      JOB_BASE,
}
LIMIT = 20


def _parse_posted_on(s: str) -> str:
    if not s:
        return ""
    from datetime import date, timedelta
    import re
    s = s.lower().strip()
    today = date.today()
    if "today" in s:
        return today.strftime("%b %d, %Y")
    m = re.search(r"(\d+)\+?\s*day", s)
    if m:
        days = int(m.group(1))
        return (today - timedelta(days=days)).strftime("%b %d, %Y")
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
        total = data0.get("total", 0)
        raw   = data0.get("jobPostings", [])
        print(f"[fnb] total={total}")

        if total > LIMIT:
            pages = await asyncio.gather(*[
                session.post(
                    API_URL,
                    json={"limit": LIMIT, "offset": offset, "searchText": "", "locations": []},
                    headers=HEADERS,
                    timeout=30,
                )
                for offset in range(LIMIT, total, LIMIT)
            ])
            for r in pages:
                if r.status_code == 200 and r.text:
                    raw.extend(r.json().get("jobPostings", []))

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
        posted = _parse_posted_on(j.get("postedOn") or "")
        jobs.append({
            "role_id":     f"fnb_{req_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("locationsText") or "").strip(),
            "posted_date": posted,
            "url":         JOB_BASE + ext_path if ext_path else "",
            "company":     "First National Bank",
            "experience":  "",
        })

    print(f"[fnb] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
