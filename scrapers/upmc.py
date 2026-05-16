import asyncio
import json
import re
from datetime import datetime

from curl_cffi.requests import AsyncSession

API_URL     = "https://jobsapi-internal.m-cloud.io/api/job"
ORG         = "2450"
PAGE_SIZE   = 10
CONCURRENCY = 5
HEADERS     = {"Referer": "https://careers.upmc.com/"}


def _strip_jsonp(text: str) -> str:
    m = re.search(r"\((.+)\)$", text, re.S)
    return m.group(1) if m else text


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, offset: int) -> list[dict]:
    async with sem:
        r = await session.get(
            API_URL,
            params={"callback": "cb", "Organization": ORG,
                    "offset": offset, "num": PAGE_SIZE,
                    "sortField": "id", "sortOrder": "asc"},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        import json
        return json.loads(_strip_jsonp(r.text)).get("queryResult", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        # First page to get total
        r0 = await session.get(
            API_URL,
            params={"callback": "cb", "Organization": ORG, "offset": 0, "num": PAGE_SIZE,
                    "sortField": "id", "sortOrder": "asc"},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        data0  = json.loads(_strip_jsonp(r0.text))
        total  = data0.get("totalHits", 0)
        first  = data0.get("queryResult", [])
        print(f"[upmc] totalHits={total}, fetching {(total + PAGE_SIZE - 1) // PAGE_SIZE} pages")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch(session, sem, offset)
            for offset in range(PAGE_SIZE, total, PAGE_SIZE)
        ])

    raw = first + [j for page in rest for j in page]

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)

        city  = (j.get("primary_city")  or "").strip()
        state = (j.get("primary_state") or "").strip()
        loc   = f"{city}, {state}" if city and state else city or state

        jobs.append({
            "role_id":     f"upmc_{job_id}",
            "title":       title,
            "team":        (j.get("primary_category") or j.get("department") or "").strip(),
            "location":    loc,
            "posted_date": _fmt_date(j.get("open_date") or ""),
            "url":         (j.get("url") or "").strip(),
            "company":     "UPMC",
            "experience":  (j.get("level") or "").strip(),
        })

    print(f"[upmc] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
