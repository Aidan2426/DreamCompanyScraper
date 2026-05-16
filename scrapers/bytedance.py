import asyncio
from curl_cffi.requests import AsyncSession

BASE     = "https://jobs.bytedance.com/api/v1/public/supplier"
SITE     = "https://joinbytedance.com"
API_URL  = BASE + "/search/job/posts"
HEADERS  = {
    "Content-Type":   "application/json",
    "accept-language": "en-US",
    "website-path":   "en",
    "origin":         SITE,
    "User-Agent":     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
}
PER_PAGE = 500


def _payload(offset: int) -> dict:
    return {
        "keyword":              "",
        "limit":                PER_PAGE,
        "offset":               offset,
        "recruitment_id_list":  [],
        "job_category_id_list": [],
        "subject_id_list":      [],
        "location_code_list":   [],
    }


def _location(j: dict) -> str:
    city_info = j.get("city_info") or {}
    city   = city_info.get("en_name") or ""
    parent = (city_info.get("parent") or {}).get("en_name") or ""
    if city and parent:
        return f"{city}, {parent}"
    return city or parent


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.post(API_URL, json=_payload(0), headers=HEADERS, timeout=30)
        r0.raise_for_status()
        d0    = r0.json()
        data0 = d0.get("data", {})
        total = data0.get("count", 0)
        raw   = list(data0.get("job_post_list") or [])
        print(f"[bytedance] total={total}")

        if total > PER_PAGE:
            pages = await asyncio.gather(*[
                session.post(API_URL, json=_payload(off), headers=HEADERS, timeout=30)
                for off in range(PER_PAGE, total, PER_PAGE)
            ])
            for r in pages:
                if r.status_code == 200:
                    raw.extend(r.json().get("data", {}).get("job_post_list") or [])

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        cat = j.get("job_category") or {}
        exp = j.get("job_subject") or {}
        jobs.append({
            "role_id":     f"bytedance_{job_id}",
            "title":       title,
            "team":        (cat.get("en_name") or "").strip(),
            "location":    _location(j),
            "posted_date": "",
            "url":         f"{SITE}/search/{job_id}",
            "company":     "ByteDance",
            "experience":  (exp.get("en_name") or "").strip(),
        })

    print(f"[bytedance] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")
