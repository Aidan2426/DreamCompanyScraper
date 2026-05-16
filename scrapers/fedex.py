import asyncio
import json
import math
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE     = "https://careers.fedex.com"
LIST_URL = BASE + "/jobs"
PER_PAGE = 25
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}


def _extract(html: str) -> tuple[int, list]:
    idx = html.find("__PRELOAD_STATE__")
    if idx < 0:
        return 0, []
    chunk = html[idx + len("__PRELOAD_STATE__ = "):]
    brace = 0
    end = 0
    for i, c in enumerate(chunk):
        if c == "{":
            brace += 1
        elif c == "}":
            brace -= 1
        if brace == 0 and i > 0:
            end = i + 1
            break
    try:
        d = json.loads(chunk[:end])
    except Exception:
        return 0, []
    js = d.get("jobSearch", {})
    return js.get("totalJob", 0), js.get("jobs", [])


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch_page(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list:
    async with sem:
        r = await session.get(LIST_URL, params={"page_number": page, "page_size": PER_PAGE},
                              headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        _, jobs = _extract(r.text)
        return jobs


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(LIST_URL, params={"page_number": 1, "page_size": PER_PAGE},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        total, page1_raw = _extract(r0.text)
        total_pages = math.ceil(total / PER_PAGE)
        print(f"[fedex] total={total} pages={total_pages}")

        sem  = asyncio.Semaphore(5)
        rest = await asyncio.gather(*[_fetch_page(session, p, sem) for p in range(2, total_pages + 1)])

    all_raw = page1_raw + [j for page in rest for j in page]

    seen = set()
    jobs = []
    for j in all_raw:
        ref      = (j.get("reference") or "").strip()
        title    = (j.get("title") or "").strip()
        orig_url = (j.get("originalURL") or "").strip()
        if not ref or not title or ref in seen:
            continue
        seen.add(ref)
        locs = j.get("locations") or []
        if locs:
            loc = locs[0]
            location = f"{loc.get('city', '')}, {loc.get('stateAbbr', '')}".strip(", ")
        else:
            location = ""
        cf   = {c["cfKey"]: c.get("value", "") for c in (j.get("customFields") or [])}
        date = _fmt_date(cf.get("cf_effective_date", ""))
        jobs.append({
            "role_id":     f"fedex_{ref}",
            "title":       title,
            "team":        (j.get("brandName") or "").strip(),
            "location":    location,
            "posted_date": date,
            "url":         f"{BASE}/{orig_url}" if orig_url else "",
            "company":     "FedEx",
            "experience":  "",
        })

    print(f"[fedex] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")
