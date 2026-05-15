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
    "UPMC":           "https://upload.wikimedia.org/wikipedia/commons/a/a0/UPMC_logo.svg",
    "National Geographic Society": "https://upload.wikimedia.org/wikipedia/commons/0/0e/National_Geographic_Society.svg",
    "Panasonic":      "https://upload.wikimedia.org/wikipedia/commons/3/31/Panasonic_logo_%28Blue%29.svg",
    "Snap":           "https://upload.wikimedia.org/wikipedia/commons/a/a7/Snapchat_logo.svg",
    "Logitech":       "https://upload.wikimedia.org/wikipedia/commons/0/05/Logitech_logo.svg",
    "Cloudflare":     "https://upload.wikimedia.org/wikipedia/commons/4/4b/Cloudflare_Logo.svg",
    "Peloton":        "https://upload.wikimedia.org/wikipedia/commons/1/16/Peloton_logo.svg",
    "Zillow":         "https://upload.wikimedia.org/wikipedia/commons/9/96/Zillow_logo.svg",
    "Garmin":         "https://upload.wikimedia.org/wikipedia/commons/5/5c/Garmin_logo.svg",
    "Autodesk":       "https://upload.wikimedia.org/wikipedia/commons/b/b9/Autodesk_Logo.svg",
    "Deloitte":       "https://upload.wikimedia.org/wikipedia/commons/5/56/Deloitte.svg",
    "Wesco":          "https://upload.wikimedia.org/wikipedia/commons/6/69/Wesco_International_logo.svg",
    "Viatris":        "https://upload.wikimedia.org/wikipedia/commons/6/6a/Viatris_logo.svg",
    "Dick's Sporting Goods": "https://upload.wikimedia.org/wikipedia/commons/5/56/DICK%27S_Sporting_Goods_logo.svg",
    "Alcoa":          "https://upload.wikimedia.org/wikipedia/commons/6/69/Alcoa_Logo.svg",
    "Arconic":        "https://upload.wikimedia.org/wikipedia/commons/8/8d/Arconic_logo.svg",
    "Westinghouse":   "https://upload.wikimedia.org/wikipedia/commons/4/49/Westinghouse_Electric_Corporation_Logo.svg",
    "EQT":            "https://upload.wikimedia.org/wikipedia/commons/0/05/EQT_Corporation_logo.svg",
    "Howmet Aerospace": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Howmet_Aerospace_logo.svg",
    "American Eagle":   "https://upload.wikimedia.org/wikipedia/commons/8/8b/American_Eagle_Outfitters_Logo.svg",
    "Coherent":         "https://upload.wikimedia.org/wikipedia/commons/8/8e/Coherent_Corp_logo.svg",
    "Nike":             "https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg",
    "Adidas":           "https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg",
    "Razer":            "https://upload.wikimedia.org/wikipedia/commons/a/a4/Razer_snake_logo.svg",
    "Stripe":           "https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg",
    "Notion":           "https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png",
    "Disney":           "https://upload.wikimedia.org/wikipedia/commons/a/a4/Disney_wordmark.svg",
    "Nvidia":           "https://upload.wikimedia.org/wikipedia/commons/a/a4/NVIDIA_logo.svg",
    "Hershey":          "https://upload.wikimedia.org/wikipedia/commons/e/e2/Hershey_Company_logo.svg",
    "IBM":              "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
    "Cisco":            "https://upload.wikimedia.org/wikipedia/commons/0/08/Cisco_logo_blue_2016.svg",
    "Oracle":           "https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg",
    "Universal Parks & Resorts": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Universal_Pictures_logo.svg",
    "Duolingo":         "https://upload.wikimedia.org/wikipedia/commons/d/de/Duolingo_logo.svg",
    "HP":               "https://upload.wikimedia.org/wikipedia/commons/a/ad/HP_logo_2012.svg",
    "Intel":            "https://upload.wikimedia.org/wikipedia/commons/7/7d/Intel_logo_%282006-2020%29.svg",
    "Qualcomm":         "https://upload.wikimedia.org/wikipedia/commons/f/fc/Qualcomm-Logo.svg",
    "Micron":           "https://upload.wikimedia.org/wikipedia/commons/c/c0/Micron_Technology_Inc._logo.svg",
    "Paramount":        "https://upload.wikimedia.org/wikipedia/commons/2/20/Paramount_Pictures_logo.svg",
    "Adobe":            "https://upload.wikimedia.org/wikipedia/commons/8/8d/Adobe_Corporate_logo.svg",
    "Motorola Solutions": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Motorola_Solutions_logo.svg",
    "Samsung":          "https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg",
    "eBay":             "https://upload.wikimedia.org/wikipedia/commons/1/1b/EBay_logo.svg",
    "Gecko Robotics":   "https://upload.wikimedia.org/wikipedia/commons/5/5e/Gecko_Robotics_logo.svg",
    "Western Digital":  "https://upload.wikimedia.org/wikipedia/commons/7/7e/Western_Digital_logo_%282020%29.svg",
    "National Park Service": "https://upload.wikimedia.org/wikipedia/commons/1/1f/US-NationalParkService-Logo.svg",
    "xAI":              "https://upload.wikimedia.org/wikipedia/commons/b/b2/XAI_Logo.svg",
    "Palantir":         "https://upload.wikimedia.org/wikipedia/commons/1/13/Palantir_Technologies_logo.svg",
    "Sony":             "https://upload.wikimedia.org/wikipedia/commons/c/ca/Sony_logo.svg",
    "Nintendo":         "https://upload.wikimedia.org/wikipedia/commons/0/0d/Nintendo.svg",
    "EA":               "https://upload.wikimedia.org/wikipedia/commons/a/ae/Electronic-arts-ea-logo.svg",
    "Epic Games":       "https://upload.wikimedia.org/wikipedia/commons/3/31/Epic_Games_logo_and_wordmark.svg",
    "Roblox":           "https://upload.wikimedia.org/wikipedia/commons/8/85/Roblox_logo.svg",
    "Ubisoft":          "https://upload.wikimedia.org/wikipedia/commons/7/78/Ubisoft_logo.svg",
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
      background: #0e0e10;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      padding: 14px 24px 12px;
      display: flex; flex-direction: column;
      align-items: center; gap: 11px;
    }}
    .search-wrap {{
      position: relative; width: 100%; max-width: 580px;
    }}
    .search-wrap .s-icon {{
      position: absolute; left: 13px; top: 50%; transform: translateY(-50%);
      width: 15px; height: 15px; pointer-events: none;
      stroke: rgba(255,255,255,0.3); fill: none;
      stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
    }}
    .search-input {{
      width: 100%; height: 38px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 10px;
      padding: 0 14px 0 38px;
      font-size: 14px; color: #fff; outline: none;
      transition: border-color 0.15s, background 0.15s;
    }}
    .search-input::placeholder {{ color: rgba(255,255,255,0.3); }}
    .search-input:focus {{ background: rgba(255,255,255,0.09); border-color: rgba(0,113,227,0.65); }}
    .filter-strip {{
      display: flex; align-items: center; gap: 7px;
      flex-wrap: wrap; justify-content: center;
    }}
    .fsep {{
      width: 1px; height: 18px;
      background: rgba(255,255,255,0.12);
      flex-shrink: 0; margin: 0 3px;
    }}
    .pill {{
      font-size: 12.5px; padding: 5px 13px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; white-space: nowrap; font-weight: 500;
      transition: all 0.15s;
    }}
    .pill:hover {{ background: rgba(255,255,255,0.11); color: #fff; border-color: rgba(255,255,255,0.2); }}
    .pill.active {{ background: var(--blue); border-color: var(--blue); color: #fff; }}
    .filter-select {{
      font-size: 12.5px; padding: 5px 26px 5px 12px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; outline: none; appearance: none; font-weight: 500;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='rgba(255,255,255,0.4)' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat; background-position: right 9px center;
      transition: all 0.15s;
    }}
    .filter-select option {{ background: #111113; }}
    .filter-select:hover {{ color: #fff; border-color: rgba(255,255,255,0.2); background-color: rgba(255,255,255,0.10); }}
    .filter-select.active {{ border-color: var(--blue); color: #fff; background-color: rgba(0,113,227,0.18); }}

    /* ── Custom multi-select dropdowns ── */
    .custom-select {{ position: relative; }}
    .cs-btn {{
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 12.5px; padding: 5px 12px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; white-space: nowrap; font-weight: 500;
      transition: all 0.15s; user-select: none;
    }}
    .cs-btn:hover {{ background: rgba(255,255,255,0.11); color: #fff; border-color: rgba(255,255,255,0.2); }}
    .cs-btn.active {{ border-color: var(--blue); color: #fff; background: rgba(0,113,227,0.18); }}
    .cs-badge {{
      display: none; background: var(--blue); color: #fff;
      border-radius: 980px; font-size: 10px; font-weight: 700;
      padding: 1px 6px; line-height: 1.5;
    }}
    .cs-chevron {{ flex-shrink: 0; transition: transform 0.15s; }}
    .custom-select.open .cs-chevron {{ transform: rotate(180deg); }}
    .cs-panel {{
      position: absolute; top: calc(100% + 6px); left: 50%;
      transform: translateX(-50%);
      background: #1c1c1e; border: 1px solid rgba(255,255,255,0.12);
      border-radius: 14px; padding: 8px;
      min-width: 230px; max-width: 300px; max-height: 340px;
      overflow: hidden; flex-direction: column; gap: 4px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
      z-index: 200; display: none;
    }}
    .custom-select.open .cs-panel {{ display: flex; }}
    .cs-search {{
      width: 100%; flex-shrink: 0;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 8px; padding: 6px 10px;
      font-size: 13px; color: #fff; outline: none;
    }}
    .cs-search::placeholder {{ color: rgba(255,255,255,0.3); }}
    .cs-list {{ overflow-y: auto; flex: 1; }}
    .cs-item {{
      display: flex; align-items: center; gap: 8px;
      padding: 7px 8px; border-radius: 8px;
      cursor: pointer; transition: background 0.1s;
    }}
    .cs-item:hover {{ background: rgba(255,255,255,0.07); }}
    .cs-item.selected {{ background: rgba(0,113,227,0.12); }}
    .cs-logo {{ width: 18px; height: 18px; object-fit: contain; flex-shrink: 0; background: #fff; border-radius: 3px; padding: 2px; box-sizing: border-box; }}
    .cs-lbl {{ font-size: 13px; color: rgba(255,255,255,0.82); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .cs-check {{
      width: 16px; height: 16px; border-radius: 4px;
      border: 1.5px solid rgba(255,255,255,0.2);
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: all 0.1s;
    }}
    .cs-item.selected .cs-check {{ background: var(--blue); border-color: var(--blue); }}
    .cs-tick {{ display: none; width: 9px; height: 8px; }}
    .cs-item.selected .cs-tick {{ display: block; }}
    .cs-empty {{ font-size: 13px; color: rgba(255,255,255,0.3); padding: 12px 8px; text-align: center; }}

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
    .card-top-right {{ margin-left: auto; display: flex; gap: 4px; align-items: center; }}
    .new-badge {{
      font-size: 10px; font-weight: 700;
      background: #34c759; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.4px;
    }}
    .match-badge {{
      font-size: 10px; font-weight: 700; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.3px;
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
  <div class="search-wrap">
    <svg class="s-icon" viewBox="0 0 20 20"><circle cx="8.5" cy="8.5" r="5.5"/><line x1="13" y1="13" x2="18" y2="18"/></svg>
    <input class="search-input" id="q" type="search" placeholder="Search jobs…" autocomplete="off"/>
  </div>
  <div class="filter-strip">
    <button class="pill active" data-new="all">All</button>
    <button class="pill" data-new="new">✦ New</button>
    <div class="fsep"></div>
    <button class="pill active" data-region="us">🇺🇸 US</button>
    <button class="pill" data-region="all">🌐 All</button>
    <div class="fsep"></div>
    <div class="custom-select" id="cs-company">
      <button class="cs-btn"><span class="cs-btn-label">Company</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <div class="custom-select" id="cs-team">
      <button class="cs-btn"><span class="cs-btn-label">Team</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <div class="custom-select" id="cs-city">
      <button class="cs-btn"><span class="cs-btn-label">City</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <div class="custom-select" id="cs-exp">
      <button class="cs-btn"><span class="cs-btn-label">Level</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><div class="cs-list"></div></div>
    </div>
    <div class="fsep"></div>
    <button class="pill active" data-sort="newest">Newest</button>
    <button class="pill" data-sort="title">A–Z</button>
    <button class="pill" data-sort="foryou">✦ For You</button>
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

// Cities that share a 2-letter code with a US state but are NOT in the US
const INTL_CITY_HINT = new Set([
  'bangalore','bengaluru','hyderabad','mumbai','delhi','new delhi','pune','chennai',
  'kolkata','noida','gurgaon','gurugram','ahmedabad','kochi','jaipur','indore','nagpur',
  'toronto','vancouver','montreal','ottawa','calgary','edmonton','winnipeg','halifax',
  'london','manchester','edinburgh','bristol','leeds','birmingham','glasgow','dublin',
  'amsterdam','berlin','munich','frankfurt','hamburg','cologne','stuttgart','paris',
  'lyon','marseille','madrid','barcelona','seville','milan','rome','turin','naples',
  'sydney','melbourne','brisbane','perth','adelaide','auckland','wellington','christchurch',
  'singapore','tokyo','osaka','kyoto','sapporo','beijing','shanghai','shenzhen',
  'guangzhou','hong kong','seoul','busan','taipei','kaohsiung','bangkok','jakarta',
  'kuala lumpur','manila','ho chi minh','hanoi','tel aviv','jerusalem','dubai',
  'abu dhabi','riyadh','doha','cairo','nairobi','lagos','johannesburg','cape town',
  'mexico city','guadalajara','monterrey','bogota','lima','santiago','sao paulo',
  'rio de janeiro','buenos aires','stockholm','oslo','copenhagen','helsinki',
  'zurich','geneva','bern','brussels','antwerp','vienna','warsaw','prague',
  'budapest','bucharest','athens','lisbon','porto'
]);

function normalizeLocation(loc) {{
  if (!loc) return null;
  // Strip zip codes
  let s = loc.replace(/\b\d{{5}}(-\d{{4}})?\b/g, '').replace(/\s+/g, ' ').trim();
  const parts = s.split(/\s*,\s*/).map(p => p.trim()).filter(Boolean);
  if (!parts.length) return null;
  const city = parts[0];
  const cityLc = city.toLowerCase();

  for (let i = 1; i < parts.length; i++) {{
    const p = parts[i];
    if (US_ST.has(p) && !INTL_CITY_HINT.has(cityLc))  return {{ display: `${{city}}, ${{p}}`,    isUS: true }};
    if (SA[p]        && !INTL_CITY_HINT.has(cityLc))   return {{ display: `${{city}}, ${{SA[p]}}`, isUS: true }};
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
  if (m && US_ST.has(m[2]) && !INTL_CITY_HINT.has(m[1].toLowerCase())) return {{ display: `${{m[1]}}, ${{m[2]}}`, isUS: true }};

  // International: "City, Country"
  if (parts.length >= 2) return {{ display: `${{city}}, ${{parts[parts.length - 1]}}`, isUS: false }};
  return {{ display: city, isUS: false }};
}}

// Parse all locations from a job (handles newline-delimited multi-location strings)
function getLocations(j) {{
  const raw = (j.location || '').trim();
  if (!raw) return [];
  const parts = raw.split(/\\r?\\n/).map(s => s.trim()).filter(Boolean);
  const results = [];
  parts.forEach(p => {{
    // "PA - Pittsburgh (15222)" or "PA - Pittsburgh" format
    const m = p.match(/^([A-Z]{{2}})\s*[-–]\s*(.+?)(?:\s*\(\d+\))?$/);
    if (m && US_ST.has(m[1]) && !INTL_CITY_HINT.has(m[2].trim().toLowerCase())) {{
      results.push({{ display: `${{m[2].trim()}}, ${{m[1]}}`, isUS: true }});
      return;
    }}
    const n = normalizeLocation(p);
    if (n) results.push(n);
  }});
  return results;
}}

// Build city lists — only include cities with ≥2 jobs to keep dropdowns manageable
const _cityCount = {{}};
JOBS.forEach(j => getLocations(j).forEach(n => {{ _cityCount[n.display] = (_cityCount[n.display] || 0) + 1; }}));
const US_CITIES   = [...new Set(JOBS.flatMap(j => getLocations(j).filter(n => n.isUS  && _cityCount[n.display] >= 2).map(n => n.display)))].sort();
const INTL_CITIES = [...new Set(JOBS.flatMap(j => getLocations(j).filter(n => !n.isUS && _cityCount[n.display] >= 2).map(n => n.display)))].sort();

// ── For You scoring ──
function scoreJob(j) {{
  let s = 10;
  const title = (j.title || '').toLowerCase();
  const team  = (j.team  || '').toLowerCase();
  const exp   = (j.experience || '').toLowerCase();

  // Role match — title
  if (/data[\\s-]?(engineer|analyst|scientist|science|pipelin)/.test(title)) s += 40;
  else if (/\\b(data|analytics|sql|\\bbi\\b|warehouse)/.test(title))          s += 22;
  if (/\\b(software[\\s-]*(engineer|developer)|swe|sde|developer|programmer)/.test(title)) s += 40;
  if (/\\b(machine[\\s-]*learning|\\bml\\b|\\bai\\b|artificial intel)/.test(title))        s += 35;
  if (/\\b(backend|frontend|full[\\s-]?stack)/.test(title))                               s += 22;
  if (/\\b(information tech|systems|infrastructure|devops|cloud|platform|\\bsre\\b)/.test(title)) s += 28;

  // Entry-level signals
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|early[\\s-]*career|level\\s*i\\b|associate\\b)/.test(title)) s += 28;
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|associate)/.test(exp)) s += 35;

  // Seniority penalties
  if (/\\b(senior|sr\\.?\\s|staff\\s|principal)/.test(title)) s -= 35;
  if (/\\b(director|vp\\b|vice\\s*president|head\\s+of|chief|\\bpresident\\b)/.test(title)) s -= 50;
  if (/\\bmanager\\b/.test(title)) s -= 20;
  if (/\\b(senior|staff|principal)/.test(exp)) s -= 30;

  // Team boost
  if (/\\b(engineering|software|data|analytics|\\bml\\b|\\bai\\b|\\bit\\b|technology|infrastructure|platform|cloud|security)/.test(team)) s += 15;

  return Math.max(0, Math.min(100, s));
}}

// ── Custom multi-select dropdown factory ──
function makeDropdown(containerId, getItems, iconFn) {{
  const wrap     = document.getElementById(containerId);
  const btn      = wrap.querySelector('.cs-btn');
  const badge    = wrap.querySelector('.cs-badge');
  const panel    = wrap.querySelector('.cs-panel');
  const searchEl = wrap.querySelector('.cs-search');
  const list     = wrap.querySelector('.cs-list');
  const sel      = new Set();
  let q = '';

  function renderItems() {{
    list.innerHTML = '';
    const items = getItems().filter(v => !q || v.toLowerCase().includes(q.toLowerCase()));
    if (!items.length) {{ list.innerHTML = '<div class="cs-empty">No results</div>'; return; }}
    const frag = document.createDocumentFragment();
    items.forEach(v => {{
      const icon = iconFn ? iconFn(v) : null;
      const d = document.createElement('div');
      d.className = 'cs-item' + (sel.has(v) ? ' selected' : '');
      if (icon) {{ const img=document.createElement('img'); img.className='cs-logo'; img.src=icon; img.alt=''; d.appendChild(img); }}
      const lbl=document.createElement('span'); lbl.className='cs-lbl'; lbl.textContent=v; d.appendChild(lbl);
      const chk=document.createElement('div'); chk.className='cs-check';
      chk.innerHTML='<svg class="cs-tick" viewBox="0 0 10 8" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4l3 3 5-6"/></svg>';
      d.appendChild(chk);
      d.addEventListener('mousedown', e => {{
        e.preventDefault();
        sel.has(v) ? sel.delete(v) : sel.add(v);
        d.classList.toggle('selected', sel.has(v));
        badge.textContent = sel.size || '';
        badge.style.display = sel.size ? '' : 'none';
        btn.classList.toggle('active', sel.size > 0);
        render();
      }});
      frag.appendChild(d);
    }});
    list.appendChild(frag);
  }}

  btn.addEventListener('click', e => {{
    e.stopPropagation();
    const wasOpen = wrap.classList.contains('open');
    document.querySelectorAll('.custom-select.open').forEach(el => el.classList.remove('open'));
    if (!wasOpen) {{ wrap.classList.add('open'); renderItems(); if (searchEl) {{ searchEl.value=''; q=''; searchEl.focus(); }} }}
  }});
  if (searchEl) {{
    searchEl.addEventListener('keydown', e => e.stopPropagation());
    searchEl.addEventListener('input',   () => {{ q=searchEl.value; renderItems(); }});
  }}
  panel.addEventListener('click', e => e.stopPropagation());
  return {{ sel, refresh: renderItems }};
}}
document.addEventListener('click', () => document.querySelectorAll('.custom-select.open').forEach(el=>el.classList.remove('open')));

const PAGE_SIZE = 100;
let currentPage = 1;
let _usOnly = true;

const companyDrop = makeDropdown('cs-company', ()=>COMPANIES, v=>LOGOS[v]);
const teamDrop    = makeDropdown('cs-team',    ()=>TEAMS,     null);
const cityDrop    = makeDropdown('cs-city',    ()=>_usOnly ? US_CITIES : [...new Set([...US_CITIES,...INTL_CITIES])].sort((a,b)=>a.localeCompare(b)), null);
const expDrop     = makeDropdown('cs-exp',     ()=>EXPERIENCES, null);

const state = {{ q:'', newOnly:false, sort:'newest' }};

function filtered() {{
  return JOBS.filter(j => {{
    if (state.q              && !j.title.toLowerCase().includes(state.q)) return false;
    if (state.newOnly        && !j.is_new)                                 return false;
    if (companyDrop.sel.size && !companyDrop.sel.has(j.company))          return false;
    if (teamDrop.sel.size    && !teamDrop.sel.has(j.team))                return false;
    if (expDrop.sel.size     && !expDrop.sel.has(j.experience))           return false;
    if (state.sort === 'foryou' && scoreJob(j) < 20)                      return false;
    if (_usOnly) {{
      const locs = getLocations(j);
      if (locs.length > 0 && !locs.some(n => n.isUS)) return false;
    }}
    if (cityDrop.sel.size) {{
      const locs = getLocations(j);
      if (!locs.some(n => cityDrop.sel.has(n.display))) return false;
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
  if (state.sort === 'title')  return [...arr].sort((a,b)=>a.title.localeCompare(b.title));
  if (state.sort === 'foryou') return [...arr].sort((a,b) => {{
    const da = Math.floor((parseDate(a.posted_date) || parseDate(a.first_seen)) / 86400000);
    const db = Math.floor((parseDate(b.posted_date) || parseDate(b.first_seen)) / 86400000);
    if (db !== da) return db - da;
    return scoreJob(b) - scoreJob(a) || a.title.localeCompare(b.title);
  }});
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
    const sc = state.sort === 'foryou' ? scoreJob(j) : -1;
    const matchColor = sc >= 70 ? '#34c759' : sc >= 40 ? '#ff9500' : '#8e8e93';
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-top">
        ${{logoSrc ? `<img class="logo" src="${{logoSrc}}" alt="${{j.company}}"/>` : ''}}
        <span class="company-label">${{j.company}}</span>
        <div class="card-top-right">
          ${{j.is_new ? '<span class="new-badge">NEW</span>' : ''}}
          ${{sc >= 0 ? `<span class="match-badge" style="background:${{matchColor}}">${{sc}}%</span>` : ''}}
        </div>
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
document.querySelectorAll('[data-region]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-region]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  _usOnly = b.dataset.region === 'us';
  cityDrop.sel.clear();
  cityDrop.refresh();
  render();
}}));
document.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-sort]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.sort = b.dataset.sort; render();
}}));

render();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built index.html — {len(jobs)} jobs, {new_count} new")
webbrowser.open("index.html")
