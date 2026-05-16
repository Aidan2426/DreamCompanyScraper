import asyncio
import base64
import gzip
import json
import re
from curl_cffi.requests import AsyncSession

BASE      = "https://www.gd.com"
API_URL   = BASE + "/API/Careers/CareerSearch"
PAGE_URL  = BASE + "/careers/job-search"
PAGE_SIZE = 10


def _encode(obj: dict) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(raw)).decode("utf-8")


async def _fetch_page(session: AsyncSession, page: int, auth: dict) -> list[dict]:
    req = _encode({"address": [], "facets": [], "page": page, "what": ""})
    r = await session.get(
        API_URL,
        params={"request": req},
        headers={
            "Accept":              "application/json",
            "Referer":             PAGE_URL,
            "api-auth-nonce":      auth["nonce"],
            "api-auth-signature":  auth["sig"],
            "api-auth-timestamp":  auth["ts"],
        },
        timeout=30,
    )
    if r.status_code != 200 or not r.text:
        return []
    return r.json().get("Results", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        # Fetch page to get fresh auth tokens
        r0 = await session.get(PAGE_URL, timeout=30)
        html = r0.text
        auth = {
            "nonce": re.search(r'data-nonce="([^"]+)"',     html).group(1),
            "sig":   re.search(r'data-signature="([^"]+)"', html).group(1),
            "ts":    re.search(r'data-timestamp="([^"]+)"', html).group(1),
        }

        # Page 0 for total
        data0 = await _fetch_page(session, 0, auth)
        r_meta = await session.get(
            API_URL,
            params={"request": _encode({"address": [], "facets": [], "page": 0, "what": ""})},
            headers={"Accept": "application/json", "Referer": PAGE_URL,
                     "api-auth-nonce": auth["nonce"], "api-auth-signature": auth["sig"],
                     "api-auth-timestamp": auth["ts"]},
            timeout=30,
        )
        meta       = r_meta.json()
        page_count = meta.get("PageCount", 1)
        total      = meta.get("ResultTotal", 0)
        print(f"[generaldynamics] total={total} pages={page_count}")

        # Fetch remaining pages with semaphore
        sem = asyncio.Semaphore(15)

        async def _guarded(page):
            async with sem:
                return await _fetch_page(session, page, auth)

        rest = await asyncio.gather(*[_guarded(p) for p in range(1, page_count)])

    raw = meta.get("Results", [])
    for page_jobs in rest:
        raw.extend(page_jobs)

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("Id") or j.get("ReferenceCode") or "").strip()
        title  = (j.get("Title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        locs    = j.get("LocationNames") or []
        url_path = (j.get("Link") or {}).get("Url", "")
        jobs.append({
            "role_id":     f"gd_{job_id}",
            "title":       title,
            "team":        (j.get("Category") or "").strip(),
            "location":    locs[0].strip() if locs else "",
            "posted_date": (j.get("FormattedDate") or "").strip(),
            "url":         BASE + url_path if url_path else "",
            "company":     "General Dynamics",
            "experience":  "",
        })

    print(f"[generaldynamics] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
