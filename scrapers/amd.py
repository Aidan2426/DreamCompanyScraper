import asyncio
import math
import httpx
from datetime import datetime, timezone

BASE_URL = "https://careers.amd.com/api/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://careers.amd.com/careers-home/jobs",
}
PAGE_SIZE   = 100
CONCURRENCY = 10


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_job(raw: dict) -> dict | None:
    j = raw.get("data") or raw
    req_id = str(j.get("req_id") or "").strip()
    title  = (j.get("title") or "").strip()
    if not req_id or not title:
        return None

    cats = j.get("categories") or []
    team = (cats[0].get("name") or "").strip() if cats else ""

    url = ((j.get("meta_data") or {}).get("canonical_url") or
           f"https://careers.amd.com/jobs/{req_id}?lang=en-us")

    return {
        "role_id":     f"amd_{req_id}",
        "title":       title,
        "team":        team,
        "location":    j.get("full_location") or j.get("short_location") or "",
        "posted_date": _fmt_date(j.get("posted_date") or ""),
        "url":         url,
        "company":     "AMD",
    }


async def _fetch_page(client: httpx.AsyncClient, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        try:
            r = await client.get(BASE_URL, params={"page": page, "limit": PAGE_SIZE})
            r.raise_for_status()
            return r.json().get("jobs", [])
        except Exception:
            return []


async def scrape() -> list[dict]:
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = await client.get(BASE_URL, params={"page": 1, "limit": PAGE_SIZE})
        r.raise_for_status()
        data        = r.json()
        total       = data.get("totalCount", 0)
        total_pages = math.ceil(total / PAGE_SIZE)
        first_raw   = data.get("jobs", [])
        print(f"[amd] {total} jobs across {total_pages} pages")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[_fetch_page(client, sem, p) for p in range(2, total_pages + 1)])

    all_raw = first_raw + [j for page in rest for j in page]

    seen = set()
    jobs = []
    for raw in all_raw:
        j = _parse_job(raw)
        if not j or j["role_id"] in seen:
            continue
        seen.add(j["role_id"])
        jobs.append(j)

    print(f"[amd] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print({k: v.encode("ascii", "replace").decode() for k, v in j.items()})
