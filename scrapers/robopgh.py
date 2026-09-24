import asyncio
import json
import re
from datetime import date, datetime, timedelta
from curl_cffi.requests import AsyncSession

# Pittsburgh Robotics Network job board. robopgh.org/jobs (Webflow) now redirects
# here; this is a Next.js site that embeds each page's jobs as JSON in its
# React Server Components payload (self.__next_f.push chunks).
BASE_URL = "https://jobs.robopgh.org/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
MAX_PAGES = 100  # safety stop; the board has ~16 pages of 20
# Employers with their own scraper; RoboPGH's copies of their jobs would show up
# twice under a slightly different company name, with less data.
SKIP_EMPLOYERS = {"aurora", "aurora innovation", "gecko robotics", "meta"}

_JOB_START = re.compile(r'\{"id":"[a-z0-9]+","title":')


def _payload(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    return "".join(json.loads(f'"{c}"') for c in chunks)


def _extract_jobs(payload: str) -> list[dict]:
    decoder = json.JSONDecoder()
    out = []
    for m in _JOB_START.finditer(payload):
        try:
            obj, _ = decoder.raw_decode(payload, m.start())
        except ValueError:
            continue
        if obj.get("applyUrl") and obj.get("company"):
            out.append(obj)
    return out


def _posted(raw) -> str:
    if not raw:
        return ""
    s = str(raw).strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%m/%d/%Y").strftime("%b %d, %Y")
    except ValueError:
        pass
    low = s.lower().replace("a month", "1 month")
    m = re.search(r"(\d+)\+?\s*(day|month)", low)
    if m:
        days = int(m.group(1)) * (30 if m.group(2) == "month" else 1)
        return (date.today() - timedelta(days=days)).strftime("%b %d, %Y")
    if low in ("new", "today", "posted today", "just posted"):
        return date.today().strftime("%b %d, %Y")
    if "yesterday" in low:
        return (date.today() - timedelta(days=1)).strftime("%b %d, %Y")
    return ""


async def scrape() -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()
    async with AsyncSession(impersonate="chrome124") as session:
        for page in range(1, MAX_PAGES + 1):
            r = await session.get(BASE_URL, params={"page": page}, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"[robopgh] page {page} -> {r.status_code}, stopping")
                break
            raw = _extract_jobs(_payload(r.text))
            new = [j for j in raw if j["id"] not in seen]
            if not new:
                break
            for j in new:
                seen.add(j["id"])
                company = (j.get("company") or "").strip()
                if company.lower() in SKIP_EMPLOYERS:
                    continue
                jobs.append({
                    "role_id":     f"robopgh_{j['id']}",
                    "title":       (j.get("title") or "").strip(),
                    "team":        "",
                    "location":    (j.get("location") or "").strip(),
                    "posted_date": _posted(j.get("postedDate")),
                    "url":         j["applyUrl"],
                    "company":     company,
                    "experience":  (j.get("experience") or "").strip() if isinstance(j.get("experience"), str) else "",
                })

    print(f"[robopgh] Done. {len(jobs)} jobs across {page} pages "
          f"({len(seen) - len(jobs)} skipped as duplicates of direct scrapers).")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["company"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
