import asyncio
import re
import httpx
from datetime import datetime, timezone

LIST_URL = "https://api.lever.co/v0/postings/spotify"
API_BASE = "https://api.lever.co/v0/postings/spotify"
UUID_RE  = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
CONCURRENCY = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_ts(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch_one(client: httpx.AsyncClient, sem: asyncio.Semaphore, uid: str) -> dict | None:
    async with sem:
        try:
            r = await client.get(f"{API_BASE}/{uid}")
            r.raise_for_status()
            j = r.json()
        except Exception:
            return None
    cats = j.get("categories") or {}
    title = (j.get("text") or "").strip()
    if not title:
        return None
    return {
        "role_id":     f"spotify_{uid}",
        "title":       title,
        "team":        cats.get("department") or cats.get("team") or "",
        "location":    cats.get("location") or "",
        "posted_date": _fmt_ts(j.get("createdAt") or 0),
        "url":         j.get("hostedUrl") or f"https://jobs.lever.co/spotify/{uid}",
        "company":     "Spotify",
    }


async def scrape() -> list[dict]:
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = await client.get(LIST_URL)
        r.raise_for_status()
        uuids = list(dict.fromkeys(UUID_RE.findall(r.text)))
        print(f"[spotify] Found {len(uuids)} job IDs")

        sem = asyncio.Semaphore(CONCURRENCY)
        results = await asyncio.gather(*[_fetch_one(client, sem, uid) for uid in uuids])

    jobs = [j for j in results if j]
    print(f"[spotify] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)
