import asyncio
import re
from html import unescape
from curl_cffi.requests import AsyncSession

BASE     = "https://cgi.njoyn.com/corp"
LIST_URL = BASE + "/xweb/xweb.asp"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}
PARAMS   = {"NTKN": "c", "clid": "21001", "Page": "joblisting"}
ROW_RE   = re.compile(
    r"<tr\s+HasMultipleLocations='[01]'\s+RemoteWork='(?:True|False)'[^>]*>"
    r"<td><a\s+href='([^']+)'>(J[^<]+)</a></td>"
    r"<td>([^<]+)</td>"   # title
    r"<td>([^<]*)</td>"   # team
    r"<td>([^<]*)</td>"   # city
    r"<td[^>]*>([^<]*)</td>"  # country
)


def _parse_rows(html: str) -> list[tuple]:
    return ROW_RE.findall(html)


async def _fetch(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list[tuple]:
    async with sem:
        r = await session.get(LIST_URL, params={**PARAMS, "pn": page}, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return _parse_rows(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(LIST_URL, params={**PARAMS, "pn": 1}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        html0 = r0.text
        m = re.search(r'[Pp]age\s+\d+\s+of\s+(\d+)', html0)
        total_pages = int(m.group(1)) if m else 1
        raw = _parse_rows(html0)
        print(f"[cgi] total_pages={total_pages}")

        sem  = asyncio.Semaphore(8)
        rest = await asyncio.gather(*[_fetch(session, p, sem) for p in range(2, total_pages + 1)])
        for batch in rest:
            raw.extend(batch)

    seen = set()
    jobs = []
    for (href, job_id, title, team, city, country) in raw:
        job_id = job_id.strip()
        title  = title.strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        href = unescape(href)
        loc_parts = [p for p in [city.strip(), country.strip()] if p]
        jobs.append({
            "role_id":     f"cgi_{job_id}",
            "title":       title,
            "team":        team.strip(),
            "location":    ", ".join(loc_parts),
            "posted_date": "",
            "url":         BASE + "/" + href,
            "company":     "CGI",
            "experience":  "",
        })

    print(f"[cgi] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")
