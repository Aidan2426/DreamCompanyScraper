# Session Context — Pick Up Here Next Time

Last updated: 2026-05-22

---

## What This Project Is

`DreamCompanyScraper` — async Python job scraper. Scrapes ~140 companies, stores in SQLite (`jobs.db`), outputs `jobs.json`, builds `index.html` via `build.py`. Deployed to GitHub Pages via GitHub Actions daily cron at 3am EST (8am UTC).

Live site: https://aidan2426.github.io/DreamCompanyScraper/

---

## Git State Right Now

Branch: `main`. Everything committed. **Not pushed this session** — run `git push` before deploying.

Recent commits:
- `1c705f1` — feat(scrapers): add Dolby; rewrite Spotify to use bulk Lever API
- `29152fd` — crowdstrike/mondaydotcom/mongodb/zetaglobal
- `983f893` — palo alto
- `0d1e29d` — fix(stats): light background, fix sort descending by default
- `6fe4945` — feat(ui): add Stats panel — per-company total, new today, posted 24h

**Uncommitted this session:** Zscaler, UiPath scrapers + main.py wiring. Run `git push` after committing.

---

## What Was Built This Session

### Apple Scraper Rewrite (`scrapers/apple.py`)

**Problem:** Old Playwright scraper intercepted first XHR (15 jobs) and returned immediately — no pagination.

**Fix:** Direct `POST https://jobs.apple.com/api/v1/search` with session cookies + pagination.

Key discovery path:
- `/api/role/search` → 404; `/api/v1/role/search` → 401
- Found real endpoint by grepping JS bundle (`jobsite.main.*.js`) for `"/search"` → `l="/api/v1"`, `search.search.url = l+"/search"`
- Correct payload: `{query, filters:{}, locale:"en-us", sort:"newest", page:N, format:{...}}`
- Must GET main page first to seed session cookies; empty CSRF token works
- Location filter (`locationIds`, `locations`, etc.) does NOT work via API — filter US client-side by `countryName == "United States of America"`
- **Location bug:** API returns bare city names ("Sunnyvale"), `normalizeLocation` marks `isUS:false`, `_usOnly=true` default hides all Apple jobs → fix: append `", United States"` to location string so `normalizeLocation` returns `isUS:true`
- Also ran SQL UPDATE on existing DB rows to fix old location strings

**Result:** ~3,737 US jobs per run (was 15).

```python
# Apple API pattern
POST https://jobs.apple.com/api/v1/search
# Seed cookies first: GET https://jobs.apple.com/en-us/search?location=united-states-USA&sort=newest
# Headers: Content-Type: application/json, X-Apple-CSRF-Token: "", locale: en-us
# Payload: {query:"", filters:{}, locale:"en-us", sort:"newest", page:N, format:{longDate:"MMMM D, YYYY", mediumDate:"MMM D, YYYY"}}
# Response: {res: {searchResults:[...], totalRecords:N}}
# Fields: positionId, postingTitle, team.teamName/teamCode, locations[0].name, postingDate
# Job URL: https://jobs.apple.com/en-us/details/{positionId}
# Page size: 20, paginate page=1..N
# Location format: append ", United States" to city name for _usOnly filter to pass
```

### UI: Stats Panel (`build.py`)

Added **📊 Stats** button in filter strip. Opens a light-themed modal showing per-company:
- **Total Jobs** — all jobs in DB (sorted descending by default)
- **New Today** — `is_new=True` count (green)
- **Posted 24h** — `posted_date` within 48h (blue)

Features: sortable columns (click header), searchable by company name, click row → filters main view to that company. Primary use: diagnose broken scrapers (Apple had 15 → now shows 9907).

---

## main.py Current Import Line

```python
from scrapers import apple, google, microsoft, netflix, meta, amazon, openai, anthropic, disney, nvidia, hershey, ibm, cisco, oracle, universal, duolingo, hp, intel, qualcomm, micron, paramount, adobe, motorola, samsung, analogdevices, ebay, gecko, westerndigital, nps, xai, palantir, sony, nintendo, ea, epicgames, roblox, ubisoft, pinterest, linkedin, supercell, pwc, spotify, verizon, amd, salesforce, uber, airbnb, dropbox, twitch, yahoo, riotgames, fujifilm, pnc, upmc, natgeo, panasonic, snap, logitech, cloudflare, peloton, zillow, garmin, autodesk, deloitte, wesco, viatris, dsg, alcoa, arconic, westinghouse, eqt, howmet, americaneagle, coherent, nike, adidas, razer, stripe, notion, workatastartup, visa, bny, mastercard, generaldynamics, ford, sandisk, figma, capitalone, crowdstrike, boeing, wabtec, lenovo, tesla, spacex, lockheed, paypal, dell, broadcom, robopgh, aqua, cmu, covestro, fnb, bechtel, highmark, kennametal, leidos, servicenow, united, armada, bytedance, wbd, seatgeek, ticketmaster, stubhub, cgi, indeed, affirm, formenergy, gevernova, bdo, emerson, questdiagnostics, ey, fedex, gianteagle, atimaterials, ppg, gm, rivian, hubspot, github, discord, aurora, datadog, twok, moderna, boozallen, jnj, pfizer, merck, cdpr, bloomberg, l3harris, paloalto, zetaglobal, mondaydotcom, mongodb, dolby, zscaler, uipath
```

---

## Investigated But Blocked

| Company | Platform | Reason |
|---|---|---|
| **Northrop Grumman** | Eightfold AI | 403 on API — same as Accenture. Skip. |
| **McKinsey** | Unknown | Page times out. Workday tenant not found. |
| **American Express** | Oracle HCM | 403 Forbidden |
| **layoffs.fyi** | Airtable embed | iframe with Airtable data, server-side auth. Abandoned. |
| **Atlassian** | Custom (imkt-jsx) | AWS WAF blocks curl_cffi; urllib gets real HTML but jobs load client-side from lazy JS chunk. GraphQL gateway at `/gateway/api/graphql` exists but `careers` field not exposed. Abandoned. |
| **Dolby (jobs.dolby.com)** | Eightfold AI | 403 on `/api/apply/v2/jobs` even with CSRF token. Used `careers.dolby.com` (SuccessFactors) instead. |

---

## Companies Still Remaining (To Do List)

- **Square Enix** — Not investigated yet
- **BCG** — Not investigated yet (might be SmartRecruiters)
- **McKinsey** — Blocked (timeout, unknown ATS)
- **MSA Safety** — Not investigated yet (Pittsburgh)
- **ExlService** — Not investigated yet
- **Koppers** — Not investigated yet (Pittsburgh)

From "Broke" list worth fixing:
- Databricks, Snowflake, Zoom — probably Greenhouse/Lever
- JP Morgan Chase — likely Workday
- Raytheon — defense portal
- Goldman Sachs — own portal
- Blizzard — under Microsoft/Activision now

**Tip:** Use the new 📊 Stats panel to spot broken scrapers — companies with far fewer jobs than expected.

---

## Key Technical Facts

### GitHub Actions
- File: `.github/workflows/scrape.yml`
- Cron: `0 8 * * *` UTC = 3am EST
- Caches `jobs.db` between runs (key: `jobs-db-{run_id}`, restore-keys: `jobs-db-`)
- Deploys to `dist/` folder (NOT root — peaceiris respects .gitignore)
- Manual trigger: Actions tab → "Daily Job Scrape" → Run workflow

### _usOnly Filter (CRITICAL)
The UI defaults `_usOnly = true`. Jobs pass only if `normalizeLocation(location)` returns `isUS: true`.

`normalizeLocation` returns `isUS: true` when:
- Location has `, StateAbbrev` (e.g., "Pittsburgh, PA")
- Location has `, United States` / `, USA` / `, US` (e.g., "Sunnyvale, United States")
- Location matches `"City ST"` pattern (e.g., "Pittsburgh PA")

**If scraper returns bare city names → all jobs hidden.** Fix: append `", United States"` to location.

When fixing an existing scraper with bad locations, also UPDATE the DB:
```python
import sqlite3
conn = sqlite3.connect('jobs.db')
conn.execute("""
    UPDATE jobs SET location = location || ', United States'
    WHERE company = 'CompanyName'
      AND location != ''
      AND location NOT LIKE '%, United%'
      AND location NOT LIKE '%, US%'
""")
conn.commit()
```

### Platform Patterns Learned

**Greenhouse (simplest):**
```python
GET https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true
# Returns {"jobs": [...]}  — all jobs in one shot
# Fields: id, title, location.name, departments[0].name, first_published, absolute_url
```
Board names: `discord`, `hubspot`, `2k`, `datadog`, `bungie`

**Workday POST API:**
```python
POST https://{tenant}.wd*.myworkdayjobs.com/wday/cxs/{tenant}/{SITE}/jobs
body: {"limit": 20, "offset": offset, "searchText": "", "locations": []}
# Returns {"total": N, "jobPostings": [...]}
# Fields: title, externalPath (→job_id), locationsText, postedOn
# JOB_BASE = https://{tenant}.wd*.myworkdayjobs.com/en-US/{SITE}
# Max limit = 20, paginate with offset
```
Tenants: `ppg/PPG_CAREERS`, `gianteagle/GEExternalcareers`, `modernatx/M_tx`, `bah/BAH_Jobs`, `jj/JJ` (wd5), `pfizer/PfizerCareers`

**Apple Jobs API:**
```python
POST https://jobs.apple.com/api/v1/search
# Seed: GET https://jobs.apple.com/en-us/search?location=united-states-USA&sort=newest
# Headers: Content-Type:application/json, X-Apple-CSRF-Token:"", locale:en-us
# Payload: {query:"", filters:{}, locale:"en-us", sort:"newest", page:N, format:{longDate:"MMMM D, YYYY",mediumDate:"MMM D, YYYY"}}
# Response: {res:{searchResults:[...], totalRecords:N}} — page size 20
# Filter US: countryName=="United States of America"; location += ", United States"
# Job URL: https://jobs.apple.com/en-us/details/{positionId}
```

**Phenom People (eagerLoadRefineSearch):**
```python
GET https://{domain}/search-results?keywords=&from=0&size={total+50}
# Data in phApp.ddo JSON embedded in HTML
# Navigate: ddo["eagerLoadRefineSearch"]["data"]["jobs"]
# Must use brace-counting JSON extractor (regex breaks on nested arrays)
# Fields: reqId, title, category, cityState, postedDate, applyUrl
```
Used for: `atimaterials`, `merck`

**Jibe/iCIMS (GitHub, Rivian):**
```python
GET https://{domain}/api/jobs?limit=50&page=1
# NOTE: use page=N NOT offset=N
# Returns {"totalCount": N, "jobs": [...]}
# Job data in entry["data"]: req_id, title, department, location_name, posted_date, slug
```

**Algolia (Aurora):**
```python
GET https://UYBO3E5EHF-dsn.algolia.net/1/indexes/Greenhouse?query=&hitsPerPage=250
headers: X-Algolia-Application-Id: UYBO3E5EHF, X-Algolia-API-Key: 7a9b56bc6afb962030d482030f588e1e
# Same Greenhouse field format
# NOTE: POST doesn't work — must use GET with query params
```

**SmartRecruiters (CD Projekt Red):**
```python
GET https://api.smartrecruiters.com/v1/companies/{SLUG}/postings?limit=100&offset=0
# Returns {"totalFound": N, "content": [...]}
# Fields: id, name, releasedDate, location{city,region,country}, department{label}
# Job URL: https://jobs.smartrecruiters.com/{SLUG}/{id}
# Public API, no auth needed
```
Slug: `CDPROJEKTRED`

**Avature HTML (Bloomberg):**
```python
GET https://bloomberg.avature.net/careers/SearchJobs/?jobRecordsPerPage=12&jobOffset={offset}
# 12 per page, 501 total = 42 pages
# Parse: <a class="link" href="...JobDetail/.../{id}">Title</a>
#        <span class="list-item-location">City, Country</span>
# IMPORTANT: Use class="link" to avoid matching "Apply" buttons (same href pattern)
```

**TalentBrew HTML (L3Harris):**
```python
GET https://careers.l3harris.com/en/search-jobs?p={page}
# 111 pages of ~15 jobs = ~1,665 total
# Parse: <a href="/en/job/{city}/{slug}/4832/{job_id}" data-job-id="...">
#          <h2>Title</h2>
#          <span class="results-facet job-category">Category</span>
#          <span class="results-facet job-location test3">City, ST</span>
#        </a>
# Total pages from: "page 1 of 111"
```

**Umbraco/server-rendered HTML (GM):**
```python
GET https://search-careers.gm.com/en/jobs/?search=&location=&page=N
# Parse HTML with regex — splits on card divs, 42 pages
```

**Paradox.ai (FedEx):**
```python
GET https://careers.fedex.com/jobs?page_number=N&page_size=25
# NOTE: ?page=N doesn't work — must use page_number + page_size
```

### Broken/Blocked Companies
- **Accenture** — AEM/Adobe CSRF, requires JS execution. Skip.
- **LinkedIn** — In ALWAYS_SKIP set (requires auth)
- **Northrop Grumman** — Eightfold AI with CSRF/403
- **SAIC** — Cloudflare blocking
- **American Express** — Oracle HCM, 403
- **Unity** — No accessible ATS
- **Take-Two** — Client-side only
- **Bungie** — Greenhouse but 1 job only
- **McKinsey** — Page times out, ATS unknown

---

## How to Continue Next Time

1. `git status` — verify clean
2. `git push` — push this session's commits if not done
3. Use **📊 Stats** panel to identify other broken scrapers
4. Next companies to investigate:
   - **Square Enix** — find their ATS
   - **BCG** — find their ATS
   - **MSA Safety**, **Koppers** — Pittsburgh companies, likely small/easy
5. Fix broken scrapers (Databricks, Snowflake, Zoom, JP Morgan Chase)
6. After adding scrapers, always wire into main.py import + `all_scrapers` dict + test + commit
