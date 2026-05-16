import asyncio
import re
from datetime import date, timedelta
from curl_cffi.requests import AsyncSession

API_URL  = "https://livenation.wd503.myworkdayjobs.com/wday/cxs/livenation/TMExternalSite/jobs"
JOB_BASE = "https://livenation.wd503.myworkdayjobs.com/en-US/TMExternalSite"
HEADERS  = {
    "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":       "application/json",
    "Content-Type": "application/json",
}


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
        r0 = await session.post(API_URL, json={"limit": 20, "offset": 0, "searchText": "", "locations": []}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        d0    = r0.json()
        total = d0.get("total", 0)
        raw   = list(d0.get("jobPostings", []))
        print(f"[ticketmaster] total={total}")

        if total > 20:
            pages = await asyncio.gather(*[
                session.post(API_URL, json={"limit": 20, "offset": off, "searchText": "", "locations": []}, headers=HEADERS, timeout=30)
                for off in range(20, total, 20)
            ])
            for r in pages:
                if r.status_code == 200:
                    raw.extend(r.json().get("jobPostings", []))

    seen = set()
    jobs = []
    for j in raw:
        ext   = j.get("externalPath") or ""
        title = (j.get("title") or "").strip()
        job_id = ext.strip("/").split("/")[-1] if ext else ""
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        locs = j.get("locationsText") or j.get("location") or ""
        bullets = j.get("bulletFields") or []
        req_id  = bullets[0] if bullets else ""
        jobs.append({
            "role_id":     f"ticketmaster_{job_id}",
            "title":       title,
            "team":        (j.get("jobFamilyGroup") or "").strip(),
            "location":    locs.strip() if isinstance(locs, str) else "",
            "posted_date": _parse_posted_on(j.get("postedOn") or ""),
            "url":         JOB_BASE + ext,
            "company":     "Ticketmaster",
            "experience":  "",
        })

    print(f"[ticketmaster] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
