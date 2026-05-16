import httpx
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html, */*",
    "Referer": "https://careers.paramount.com/search/",
    "X-Requested-With": "XMLHttpRequest",
}

BASE = "https://careers.paramount.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    client.get(f"{BASE}/search/", headers={**HEADERS, "Accept": "text/html"})
    r = client.get(f"{BASE}/search/tile-search-results/",
                   params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc", "startrow": 0})
    soup = BeautifulSoup(r.text, "html.parser")
    tiles = soup.find_all("li", class_=re.compile(r"job-tile"))

    # Extract all customfield values from desktop section of first 5 tiles
    for tile in tiles[:5]:
        job_id_match = re.search(r'job-id-(\d+)', " ".join(tile.get("class", [])))
        job_id = job_id_match.group(1) if job_id_match else "?"

        # Title
        title_el = tile.find("a", class_="jobTitle-link")
        title = title_el.get_text(strip=True) if title_el else ""

        # Get all section-field divs in desktop sub-section only
        desktop = tile.find("div", class_=re.compile(r"sub-section-desktop"))
        if desktop:
            fields = desktop.find_all("div", class_=re.compile(r"section-field"))
            print(f"\nJob: {title} (id={job_id})")
            for f in fields:
                label = f.find("span", class_="section-label")
                val_div = f.find("div", id=re.compile(r"desktop-section-.+-value"))
                if label and val_div:
                    print(f"  {label.get_text(strip=True)}: {val_div.get_text(strip=True)}")

    # Check total from main page more carefully
    print("\n=== Total count from main page ===")
    r_main = client.get(f"{BASE}/search/",
                        params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"},
                        headers={**HEADERS, "Accept": "text/html"})
    soup_main = BeautifulSoup(r_main.text, "html.parser")

    # Look for showing X to Y of Z jobs text
    showing = re.search(r'Showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)', r_main.text)
    if showing:
        print(f"Showing {showing.group(1)} to {showing.group(2)} of {showing.group(3)}")

    count_els = soup_main.find_all(text=re.compile(r'\d+\s*(?:Jobs?|Results?)'))
    for c in count_els[:5]:
        print("Count text:", c.strip())

    # Look for total in script
    total_scripts = re.findall(r'(?:total|count|numFound|totalResults)\s*[=:]\s*["\']?(\d+)', r_main.text, re.IGNORECASE)
    print("Total in main scripts:", total_scripts[:10])
