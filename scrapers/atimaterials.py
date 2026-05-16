import asyncio
import json
from datetime import datetime
from curl_cffi.requests import AsyncSession

SEARCH  = "https://careers.atimaterials.com/us/en/search-results"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
}


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


def _extract_json(html: str, marker: str) -> dict | None:
    idx = html.find(marker)
    if idx < 0:
        return None
    start = html.find("{", idx)
    if start < 0:
        return None
    depth, i = 0, start
    while i < len(html):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[start:i + 1])
                except Exception:
                    return None
        i += 1
    return None


def _parse(html: str) -> tuple[int, list[dict]]:
    ddo = _extract_json(html, "phApp.ddo = {")
    if not ddo:
        return 0, []
    eager = ddo.get("eagerLoadRefineSearch", {})
    total = eager.get("totalHits", 0)
    jobs  = eager.get("data", {}).get("jobs", [])
    return total, jobs


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(SEARCH, params={"keywords": "", "from": 0, "size": 1},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        total, _ = _parse(r0.text)
        print(f"[atimaterials] total={total}")

        r1 = await session.get(SEARCH, params={"keywords": "", "from": 0, "size": total + 50},
                               headers=HEADERS, timeout=60)
        r1.raise_for_status()
        _, raw = _parse(r1.text)

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        req_id = (j.get("reqId") or "").strip()
        title  = (j.get("title") or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)
        apply_url = (j.get("applyUrl") or "").strip()
        jobs.append({
            "role_id":     f"atimaterials_{req_id}",
            "title":       title,
            "team":        (j.get("category") or "").strip(),
            "location":    (j.get("cityState") or "").strip(),
            "posted_date": _fmt_date(j.get("postedDate") or ""),
            "url":         apply_url,
            "company":     "ATI Materials",
            "experience":  "",
        })

    print(f"[atimaterials] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
