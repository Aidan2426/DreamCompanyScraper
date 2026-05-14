"""
Reads jobs.json and generates index.html.
Run: python build.py
"""
import json
import os
import webbrowser

COMPANY_LOGOS = {
    "Apple":  "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
    "Google":    "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
    "Microsoft": "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg",
    "Netflix":   "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Meta":      "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg",
    "Amazon":    "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "OpenAI":    "https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg",
    "Anthropic":     "https://upload.wikimedia.org/wikipedia/commons/7/78/Anthropic_logo.svg",
    "Analog Devices": "https://upload.wikimedia.org/wikipedia/commons/8/86/Analog_Devices_Logo.svg",
    "Pinterest":      "https://upload.wikimedia.org/wikipedia/commons/3/35/Pinterest_Logo.svg",
    "LinkedIn":       "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
    "Supercell":      "https://upload.wikimedia.org/wikipedia/commons/9/97/Supercell-Logo.svg",
    "PwC":            "https://upload.wikimedia.org/wikipedia/commons/0/05/PricewaterhouseCoopers_Logo.svg",
    "Spotify":        "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
    "Verizon":        "https://upload.wikimedia.org/wikipedia/commons/8/81/Verizon_2015_logo_-vector.svg",
    "AMD":            "https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg",
    "Salesforce":     "https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg",
    "Uber":           "https://upload.wikimedia.org/wikipedia/commons/c/cc/Uber_logo_2018.png",
    "Airbnb":         "https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg",
    "Dropbox":        "https://upload.wikimedia.org/wikipedia/commons/7/74/Dropbox_logo_%282013%29.svg",
    "Twitch":         "https://upload.wikimedia.org/wikipedia/commons/2/26/Twitch_logo.svg",
    "Yahoo":          "https://upload.wikimedia.org/wikipedia/commons/2/2e/Yahoo%21_logo.svg",
    "Riot Games":     "https://upload.wikimedia.org/wikipedia/commons/9/9e/Riot_Games_2019.svg",
    "Fujifilm":       "https://upload.wikimedia.org/wikipedia/commons/5/58/Fujifilm_logo.svg",
    "PNC":            "https://upload.wikimedia.org/wikipedia/commons/6/6f/PNC_Financial_Services_logo.svg",
}

TEAM_COLORS = {
    "Machine Learning and AI":    ("#1a3a8f", "#e8f0fe"),
    "Software and Services":      ("#0a5c2e", "#e6f9ee"),
    "Hardware":                   ("#7a2d00", "#fff0e6"),
    "Apple Retail":               ("#5c0a5c", "#f9e6f9"),
    "Operations and Supply Chain":("#4a4a00", "#f9f9e6"),
}

STATE_ABBREV = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
    "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
    "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT",
    "Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM",
    "New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
    "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
    "District of Columbia":"DC","Puerto Rico":"PR","Guam":"GU","Virgin Islands":"VI",
}

jobs_data = {"scraped_at": "", "jobs": []}
if os.path.exists("jobs.json"):
    with open("jobs.json", encoding="utf-8") as f:
        jobs_data = json.load(f)

jobs       = jobs_data.get("jobs", [])
scraped_at = jobs_data.get("scraped_at", "")
new_count  = sum(1 for j in jobs if j.get("is_new"))
teams      = sorted({j["team"] for j in jobs if j.get("team")})
companies  = sorted({j["company"] for j in jobs if j.get("company")})
experiences = sorted({j["experience"] for j in jobs if j.get("experience")})

jobs_json     = json.dumps(jobs,      ensure_ascii=False)
teams_json    = json.dumps(teams,     ensure_ascii=False)
companies_json= json.dumps(companies, ensure_ascii=False)
experiences_json  = json.dumps(experiences,  ensure_ascii=False)
state_abbrev_json = json.dumps(STATE_ABBREV, ensure_ascii=False)
logos_json        = json.dumps(COMPANY_LOGOS, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dream Jobs</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --blue:   #0071e3;
      --bg:     #f5f5f7;
      --white:  #ffffff;
      --near-black: #1d1d1f;
      --muted:  #6e6e73;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg); color: var(--near-black); min-height: 100vh;
    }}

    /* ── Nav ── */
    nav {{
      position: sticky; top: 0; z-index: 100;
      height: 52px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 28px;
      background: rgba(255,255,255,0.85);
      backdrop-filter: saturate(180%) blur(20px);
      border-bottom: 1px solid #d2d2d7;
    }}
    .nav-brand {{ font-size: 17px; font-weight: 700; letter-spacing: -0.3px; }}
    .nav-meta  {{ font-size: 13px; color: var(--muted); }}

    /* ── Hero ── */
    .hero {{
      background: #000; color: #fff;
      padding: 64px 28px 48px; text-align: center;
      display: flex; flex-direction: column; align-items: center; gap: 12px;
    }}
    .hero h1 {{
      font-size: clamp(40px, 6vw, 64px); font-weight: 700;
      letter-spacing: -1px; line-height: 1.05;
    }}
    .hero p {{ font-size: 17px; color: rgba(255,255,255,0.55); }}

    /* ── Controls ── */
    .controls-bar {{
      position: sticky; top: 52px; z-index: 90;
      background: rgba(0,0,0,0.9);
      backdrop-filter: saturate(180%) blur(20px);
      padding: 14px 28px; display: flex; flex-direction: column;
      align-items: center; gap: 10px;
    }}
    .search-row {{
      display: flex; gap: 10px; width: 100%; max-width: 680px;
    }}
    .search-input {{
      flex: 1; height: 36px; background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.15); border-radius: 10px;
      padding: 0 14px; font-size: 14px; color: #fff; outline: none;
    }}
    .search-input::placeholder {{ color: rgba(255,255,255,0.4); }}
    .search-input:focus {{ border-color: var(--blue); }}
    .filter-row {{
      display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;
    }}
    .pill {{
      font-size: 13px; padding: 5px 14px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 980px; color: rgba(255,255,255,0.7);
      cursor: pointer; white-space: nowrap;
      transition: background 0.15s, color 0.15s;
    }}
    .pill:hover {{ background: rgba(255,255,255,0.15); color: #fff; }}
    .pill.active {{ background: var(--blue); border-color: var(--blue); color: #fff; font-weight: 600; }}
    .filter-select {{
      font-size: 13px; padding: 5px 28px 5px 14px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 980px; color: rgba(255,255,255,0.7);
      cursor: pointer; outline: none; appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='rgba(255,255,255,0.5)' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat; background-position: right 10px center;
    }}
    .filter-select option {{ background: #1d1d1f; }}
    .filter-select.active {{ border-color: var(--blue); color: #fff; }}

    /* ── Count bar ── */
    .count-bar {{
      max-width: 1100px; margin: 28px auto 0; padding: 0 28px;
      font-size: 13px; color: var(--muted);
    }}

    /* ── Grid ── */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px; max-width: 1100px;
      margin: 16px auto 80px; padding: 0 28px;
    }}

    /* ── Card ── */
    .card {{
      background: var(--white); border-radius: 16px; padding: 22px;
      display: flex; flex-direction: column; gap: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      transition: box-shadow 0.2s, transform 0.2s;
    }}
    .card:hover {{ box-shadow: 0 6px 24px rgba(0,0,0,0.12); transform: translateY(-2px); }}

    .card-top {{
      display: flex; align-items: center; gap: 10px;
    }}
    .logo {{
      width: 22px; height: 22px; object-fit: contain; flex-shrink: 0;
    }}
    .company-label {{ font-size: 12px; color: var(--muted); font-weight: 500; }}
    .new-badge {{
      margin-left: auto; font-size: 10px; font-weight: 700;
      background: #34c759; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.4px;
    }}

    .card-title {{
      font-size: 15px; font-weight: 600; line-height: 1.35;
    }}
    .card-title a {{
      color: inherit; text-decoration: none;
    }}
    .card-title a:hover {{ color: var(--blue); }}

    .tags {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .tag {{
      font-size: 11px; font-weight: 500; border-radius: 6px; padding: 2px 8px;
      background: #f5f5f7; border: 1px solid #e5e5ea; color: #3a3a3c;
    }}
    .tag-team  {{ background: #e8f0fe; border-color: #c5d4f8; color: #1a3a8f; }}
    .tag-exp   {{ background: #fef3e2; border-color: #fcd58a; color: #7a4800; }}
    .tag-loc   {{ background: #f5f5f7; }}

    .card-date {{ font-size: 12px; color: #8e8e93; margin-top: auto; }}

    .no-results {{
      grid-column: 1/-1; text-align: center;
      padding: 80px 0; font-size: 19px; color: var(--muted);
    }}

    /* ── Pagination ── */
    .pagination {{
      display: flex; align-items: center; justify-content: center;
      gap: 8px; padding: 24px 28px 64px;
    }}
    .page-btn {{
      height: 36px; min-width: 36px; padding: 0 14px;
      background: var(--white); border: 1px solid #d2d2d7;
      border-radius: 10px; font-size: 14px; font-weight: 500;
      color: var(--near-black); cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
    }}
    .page-btn:hover:not(:disabled) {{ background: #f5f5f7; border-color: #b0b0b5; }}
    .page-btn:disabled {{ opacity: 0.35; cursor: default; }}
    .page-btn.active {{ background: var(--blue); border-color: var(--blue); color: #fff; }}
    .page-label {{ font-size: 13px; color: var(--muted); padding: 0 6px; }}
  </style>
</head>
<body>

<nav>
  <span class="nav-brand">Dream Jobs</span>
  <span class="nav-meta" id="nav-meta">{len(jobs)} jobs · {new_count} new today</span>
</nav>

<div class="hero">
  <h1>Dream Jobs</h1>
  <p>{len(jobs):,} jobs tracked{' · ' + str(new_count) + ' new today' if new_count else ''}{' · Updated ' + scraped_at if scraped_at else ''}</p>
</div>

<div class="controls-bar">
  <div class="search-row">
    <input class="search-input" id="q" type="search" placeholder="Search title…" autocomplete="off"/>
  </div>
  <div class="filter-row">
    <button class="pill active" data-new="all">All</button>
    <button class="pill" data-new="new">New Only</button>
    <select class="filter-select" id="team-select">
      <option value="">All Teams</option>
    </select>
    <select class="filter-select" id="company-select">
      <option value="">All Companies</option>
    </select>
    <select class="filter-select" id="us-city-select">
      <option value="">All US Cities</option>
    </select>
    <select class="filter-select" id="intl-city-select">
      <option value="">All Intl Cities</option>
    </select>
    <select class="filter-select" id="exp-select">
      <option value="">All Levels</option>
    </select>
    <button class="pill active" data-sort="newest">Newest</button>
    <button class="pill" data-sort="title">A–Z</button>
  </div>
</div>

<div class="count-bar"><span id="count-label"></span></div>
<div class="grid" id="grid"></div>
<div class="pagination" id="pagination"></div>

<script>
const JOBS        = {jobs_json};
const LOGOS       = {logos_json};
const TEAMS       = {teams_json};
const COMPANIES   = {companies_json};
const EXPERIENCES = {experiences_json};
const SA          = {state_abbrev_json};  // full state name → 2-letter abbrev
const US_ST       = new Set(Object.values(SA));  // set of valid 2-letter state codes

function normalizeLocation(loc) {{
  if (!loc) return null;
  // Strip zip codes
  let s = loc.replace(/\b\d{{5}}(-\d{{4}})?\b/g, '').replace(/\s+/g, ' ').trim();
  const parts = s.split(/\s*,\s*/).map(p => p.trim()).filter(Boolean);
  if (!parts.length) return null;
  const city = parts[0];

  for (let i = 1; i < parts.length; i++) {{
    const p = parts[i];
    if (US_ST.has(p))  return {{ display: `${{city}}, ${{p}}`,    isUS: true }};
    if (SA[p])         return {{ display: `${{city}}, ${{SA[p]}}`, isUS: true }};
    if (/^(USA|United States|US)$/i.test(p)) {{
      for (let k = i - 1; k >= 1; k--) {{
        if (US_ST.has(parts[k])) return {{ display: `${{city}}, ${{parts[k]}}`,    isUS: true }};
        if (SA[parts[k]])        return {{ display: `${{city}}, ${{SA[parts[k]]}}`, isUS: true }};
      }}
      return {{ display: city, isUS: true }};
    }}
  }}

  // "Pittsburgh PA" style — no comma, state abbrev at end
  const m = city.match(/^(.+?)\s+([A-Z]{{2}})$/);
  if (m && US_ST.has(m[2])) return {{ display: `${{m[1]}}, ${{m[2]}}`, isUS: true }};

  // International: "City, Country"
  if (parts.length >= 2) return {{ display: `${{city}}, ${{parts[parts.length - 1]}}`, isUS: false }};
  return {{ display: city, isUS: false }};
}}

// Build city lists — only include cities with ≥2 jobs to keep dropdowns manageable
const _cityCount = {{}};
JOBS.forEach(j => {{
  const n = normalizeLocation(j.location);
  if (n) _cityCount[n.display] = (_cityCount[n.display] || 0) + 1;
}});
const US_CITIES   = [...new Set(JOBS.map(j => normalizeLocation(j.location)).filter(n => n && n.isUS   && _cityCount[n.display] >= 2).map(n => n.display))].sort();
const INTL_CITIES = [...new Set(JOBS.map(j => normalizeLocation(j.location)).filter(n => n && !n.isUS  && _cityCount[n.display] >= 2).map(n => n.display))].sort();

const teamSel    = document.getElementById('team-select');
const companySel = document.getElementById('company-select');
const usCitySel  = document.getElementById('us-city-select');
const intlCitySel= document.getElementById('intl-city-select');
const expSel     = document.getElementById('exp-select');
TEAMS.forEach(t     => {{ const o=document.createElement('option'); o.value=o.textContent=t;   teamSel.appendChild(o); }});
COMPANIES.forEach(c => {{ const o=document.createElement('option'); o.value=o.textContent=c;   companySel.appendChild(o); }});
US_CITIES.forEach(c => {{ const o=document.createElement('option'); o.value=o.textContent=c;   usCitySel.appendChild(o); }});
INTL_CITIES.forEach(c=>{{ const o=document.createElement('option'); o.value=o.textContent=c;   intlCitySel.appendChild(o); }});
EXPERIENCES.forEach(e=>{{ const o=document.createElement('option'); o.value=o.textContent=e;   expSel.appendChild(o); }});

const PAGE_SIZE = 100;
let currentPage = 1;

const state = {{ q:'', newOnly:false, team:'', company:'', usCity:'', intlCity:'', experience:'', sort:'newest' }};

function filtered() {{
  return JOBS.filter(j => {{
    if (state.q          && !j.title.toLowerCase().includes(state.q)) return false;
    if (state.newOnly    && !j.is_new)                                 return false;
    if (state.team       && j.team    !== state.team)                  return false;
    if (state.company    && j.company !== state.company)               return false;
    if (state.experience && j.experience !== state.experience)         return false;
    if (state.usCity || state.intlCity) {{
      const n = normalizeLocation(j.location);
      if (state.usCity   && (!n || !n.isUS  || n.display !== state.usCity))   return false;
      if (state.intlCity && (!n ||  n.isUS  || n.display !== state.intlCity)) return false;
    }}
    return true;
  }});
}}

function parseDate(str) {{
  if (!str) return 0;
  // relative: "21 minutes ago", "an hour ago", "2 days ago", "a week ago"
  const rel = str.toLowerCase();
  const now = Date.now();
  const n = m => {{ const x = rel.match(m); return x ? (x[1]==='a'||x[1]==='an' ? 1 : parseInt(x[1])) : null; }};
  if (rel.includes('minute'))  {{ const v=n(/(\\d+|a|an)\\s+minute/); if(v) return now - v*60*1000; }}
  if (rel.includes('hour'))    {{ const v=n(/(\\d+|a|an)\\s+hour/);   if(v) return now - v*3600*1000; }}
  if (rel.includes('day'))     {{ const v=n(/(\\d+|a|an)\\s+day/);    if(v) return now - v*86400*1000; }}
  if (rel.includes('week'))    {{ const v=n(/(\\d+|a|an)\\s+week/);   if(v) return now - v*7*86400*1000; }}
  if (rel.includes('month'))   {{ const v=n(/(\\d+|a|an)\\s+month/);  if(v) return now - v*30*86400*1000; }}
  // absolute: "Apr 19, 2026"
  const d = new Date(str);
  return isNaN(d) ? 0 : d.getTime();
}}

function sorted(arr) {{
  if (state.sort === 'title') return [...arr].sort((a,b)=>a.title.localeCompare(b.title));
  return [...arr].sort((a,b) => {{
    const ta = parseDate(a.posted_date) || parseDate(a.first_seen);
    const tb = parseDate(b.posted_date) || parseDate(b.first_seen);
    return tb - ta || a.title.localeCompare(b.title);
  }});
}}

const grid       = document.getElementById('grid');
const label      = document.getElementById('count-label');
const pagination = document.getElementById('pagination');

function renderPagination(total, totalPages) {{
  pagination.innerHTML = '';
  if (totalPages <= 1) return;

  const start = (currentPage - 1) * PAGE_SIZE + 1;
  const end   = Math.min(currentPage * PAGE_SIZE, total);

  const prev = document.createElement('button');
  prev.className = 'page-btn'; prev.textContent = '‹ Prev';
  prev.disabled = currentPage === 1;
  prev.addEventListener('click', () => {{ currentPage--; renderPage(window._lastList); scrollToGrid(); }});
  pagination.appendChild(prev);

  // window around current page
  const delta = 2;
  const pages = new Set([1, totalPages]);
  for (let i = Math.max(2, currentPage-delta); i <= Math.min(totalPages-1, currentPage+delta); i++) pages.add(i);
  let last = 0;
  [...pages].sort((a,b)=>a-b).forEach(p => {{
    if (last && p - last > 1) {{
      const dots = document.createElement('span');
      dots.className = 'page-label'; dots.textContent = '…';
      pagination.appendChild(dots);
    }}
    const btn = document.createElement('button');
    btn.className = 'page-btn' + (p === currentPage ? ' active' : '');
    btn.textContent = p;
    btn.addEventListener('click', () => {{ currentPage = p; renderPage(window._lastList); scrollToGrid(); }});
    pagination.appendChild(btn);
    last = p;
  }});

  const next = document.createElement('button');
  next.className = 'page-btn'; next.textContent = 'Next ›';
  next.disabled = currentPage === totalPages;
  next.addEventListener('click', () => {{ currentPage++; renderPage(window._lastList); scrollToGrid(); }});
  pagination.appendChild(next);
}}

function scrollToGrid() {{
  grid.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

function renderPage(list) {{
  window._lastList = list;
  const totalPages = Math.ceil(list.length / PAGE_SIZE);
  currentPage = Math.max(1, Math.min(currentPage, totalPages || 1));

  const start = (currentPage - 1) * PAGE_SIZE;
  const page  = list.slice(start, start + PAGE_SIZE);
  const end   = start + page.length;

  if (list.length === 0) {{
    label.textContent = '0 jobs shown';
  }} else {{
    label.textContent = `Showing ${{(start+1).toLocaleString()}}–${{end.toLocaleString()}} of ${{list.length.toLocaleString()}} job${{list.length!==1?'s':''}}`;
  }}

  grid.innerHTML = '';
  if (!page.length) {{
    grid.innerHTML = '<div class="no-results">No jobs match your filters.</div>';
    renderPagination(0, 0);
    return;
  }}
  const frag = document.createDocumentFragment();
  page.forEach(j => {{
    const logoSrc = LOGOS[j.company];
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-top">
        ${{logoSrc ? `<img class="logo" src="${{logoSrc}}" alt="${{j.company}}"/>` : ''}}
        <span class="company-label">${{j.company}}</span>
        ${{j.is_new ? '<span class="new-badge">NEW</span>' : ''}}
      </div>
      <div class="card-title"><a href="${{j.url}}" target="_blank" rel="noopener">${{j.title}}</a></div>
      <div class="tags">
        ${{j.team       ? `<span class="tag tag-team">${{j.team}}</span>` : ''}}
        ${{j.experience ? `<span class="tag tag-exp">${{j.experience}}</span>` : ''}}
        ${{j.location   ? `<span class="tag tag-loc">📍 ${{j.location}}</span>` : ''}}
      </div>
      <div class="card-date">
        ${{j.posted_date ? `Posted ${{j.posted_date}}` : `First seen ${{j.first_seen}}`}}
      </div>
    `;
    frag.appendChild(card);
  }});
  grid.appendChild(frag);
  renderPagination(list.length, totalPages);
}}

function render() {{
  currentPage = 1;
  renderPage(sorted(filtered()));
}}

document.getElementById('q').addEventListener('input', e => {{ state.q = e.target.value.trim().toLowerCase(); render(); }});
document.querySelectorAll('[data-new]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-new]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.newOnly = b.dataset.new === 'new'; render();
}}));
document.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-sort]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.sort = b.dataset.sort; render();
}}));
teamSel.addEventListener('change',     () => {{ state.team     = teamSel.value;     teamSel.classList.toggle('active',!!teamSel.value);     render(); }});
companySel.addEventListener('change',  () => {{ state.company  = companySel.value;  companySel.classList.toggle('active',!!companySel.value);  render(); }});
usCitySel.addEventListener('change',   () => {{ state.usCity   = usCitySel.value;   usCitySel.classList.toggle('active',!!usCitySel.value);   if (usCitySel.value) {{ intlCitySel.value=''; state.intlCity=''; intlCitySel.classList.remove('active'); }} render(); }});
intlCitySel.addEventListener('change', () => {{ state.intlCity = intlCitySel.value; intlCitySel.classList.toggle('active',!!intlCitySel.value); if (intlCitySel.value) {{ usCitySel.value=''; state.usCity=''; usCitySel.classList.remove('active'); }} render(); }});
expSel.addEventListener('change',      () => {{ state.experience = expSel.value;    expSel.classList.toggle('active',!!expSel.value);           render(); }});

render();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built index.html — {len(jobs)} jobs, {new_count} new")
webbrowser.open("index.html")
