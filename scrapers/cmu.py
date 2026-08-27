import asyncio
import re
from datetime import datetime, timedelta, timezone

from curl_cffi.requests import AsyncSession

# CMU migrated Workday clusters (was wd5); check via the CMU careers page if this breaks again.
API_URL  = "https://cmu.wd115.myworkdayjobs.com/wday/cxs/cmu/CMU/jobs"
JOB_BASE = "https://cmu.wd115.myworkdayjobs.com/CMU"
HEADERS  = {
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "Referer":      JOB_BASE,
}
LIMIT = 20

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


async def scrape() -> list[dict]:
    scrape_time = datetime.now(timezone.utc)
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
        print(f"[cmu] total={total}")

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
        jobs.append({
            "role_id":     f"cmu_{req_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("locationsText") or "").strip(),
            "posted_date": _posted_on_to_iso(j.get("postedOn") or "", scrape_time),
            "url":         JOB_BASE + ext_path if ext_path else "",
            "company":     "CMU",
            "experience":  "",
        })

    print(f"[cmu] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
    print(f"Total: {len(jobs)}")
