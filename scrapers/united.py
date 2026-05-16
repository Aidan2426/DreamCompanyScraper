import asyncio
import re
import json
from curl_cffi.requests import AsyncSession

LIST_URL = "https://careers.united.com/us/en/search-results"
JOB_BASE = "https://careers.united.com/us/en/job"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}


def _extract_ddo(html: str) -> dict:
    m = re.search(r'phApp\.ddo\s*=\s*', html)
    if not m:
        return {}
    start = m.end()
    depth = end = 0
    for i, c in enumerate(html[start:], start):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    try:
        return json.loads(html[start:end])
    except Exception:
        return {}


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        from datetime import datetime
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return s[:10]


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            LIST_URL,
            params={"size": 1},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        ddo0  = _extract_ddo(r0.text)
        total = ddo0.get("eagerLoadRefineSearch", {}).get("totalHits", 0)
        print(f"[united] total={total}")

        r = await session.get(
            LIST_URL,
            params={"size": total or 200},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        ddo  = _extract_ddo(r.text)
        raw  = ddo.get("eagerLoadRefineSearch", {}).get("data", {}).get("jobs", [])

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("jobId") or j.get("reqId") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        location = (j.get("cityStateCountry") or j.get("location") or "").strip()
        posted   = _fmt_date(j.get("postedDate") or j.get("dateCreated") or "")
        apply_url = j.get("applyUrl") or ""
        jobs.append({
            "role_id":     f"united_{job_id}",
            "title":       title,
            "team":        (j.get("division") or "").strip(),
            "location":    location,
            "posted_date": posted,
            "url":         apply_url,
            "company":     "United Airlines",
            "experience":  "",
        })

    print(f"[united] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
