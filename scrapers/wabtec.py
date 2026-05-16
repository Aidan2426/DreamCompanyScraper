import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://api.smartrecruiters.com/v1/companies/Wabtec/postings"
JOB_BASE = "https://careers.smartrecruiters.com/Wabtec"
HEADERS  = {"User-Agent": "Mozilla/5.0 Chrome/124", "Accept": "application/json"}
LIMIT    = 100


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(API_URL, params={"limit": LIMIT, "offset": 0}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        data0 = r0.json()
        total = data0.get("totalFound", 0)
        raw   = data0.get("content", [])
        print(f"[wabtec] total={total}")

        if total > LIMIT:
            pages = await asyncio.gather(*[
                session.get(API_URL, params={"limit": LIMIT, "offset": offset}, headers=HEADERS, timeout=30)
                for offset in range(LIMIT, total, LIMIT)
            ])
            for r in pages:
                if r.status_code == 200 and r.text:
                    raw.extend(r.json().get("content", []))

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("name") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        loc  = j.get("location") or {}
        func = j.get("function") or {}
        exp  = j.get("experienceLevel") or {}
        jobs.append({
            "role_id":     f"wabtec_{job_id}",
            "title":       title,
            "team":        (func.get("label") or "").strip(),
            "location":    (loc.get("fullLocation") or "").strip(),
            "posted_date": _fmt_date(j.get("releasedDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "Wabtec",
            "experience":  (exp.get("label") or "").strip(),
        })

    print(f"[wabtec] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")
