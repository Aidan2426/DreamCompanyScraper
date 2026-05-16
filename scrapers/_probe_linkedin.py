import asyncio
import re
import json
from curl_cffi.requests import AsyncSession

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

SEARCH_URL = "https://www.linkedin.com/jobs/search/"
PARAMS = {
    "keywords": "software engineer",
    "location": "Greater Pittsburgh Area",
    "f_TPR": "r86400",  # past 24 hours
    "start": 0,
}


async def probe():
    async with AsyncSession(impersonate="chrome124") as s:
        print("Hitting LinkedIn public job search...")
        r = await s.get(SEARCH_URL, params=PARAMS, headers=HEADERS, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('content-type', '')}")
        print(f"Response size: {len(r.text)}")

        # Check what we got
        html = r.text
        if "sign in" in html.lower() or "join now" in html.lower() or "authwall" in html.lower():
            print(">>> BLOCKED: Login wall detected")
        elif "captcha" in html.lower():
            print(">>> BLOCKED: CAPTCHA detected")
        elif r.status_code == 429:
            print(">>> RATE LIMITED")
        elif r.status_code == 999:
            print(">>> BLOCKED: LinkedIn 999 (bot detection)")
        else:
            print(">>> Possibly got real content!")

        # Try to find job data — LinkedIn embeds JSON in <code> tags
        code_blocks = re.findall(r'<code[^>]*>(.*?)</code>', html, re.S)
        print(f"\nCode blocks found: {len(code_blocks)}")

        # Look for job titles
        titles = re.findall(r'"title"\s*:\s*\{"text"\s*:\s*"([^"]+)"', html)
        print(f"Job titles found: {len(titles)}")
        for t in titles[:10]:
            print(f"  {t}")

        # Look for company names
        companies = re.findall(r'"companyName"\s*:\s*"([^"]+)"', html)
        print(f"\nCompanies found: {len(companies)}")
        for c in companies[:10]:
            print(f"  {c}")

        # Show a snippet to diagnose
        print("\n--- First 2000 chars ---")
        print(html[:2000])


asyncio.run(probe())
