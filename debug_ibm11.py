import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

# Look for ibm.com domain references
ibm_refs = re.findall(r'[a-z0-9._-]*ibm\.com[/a-zA-Z0-9._\-?=%&+:@]{0,150}', js)
print("=== ibm.com references ===")
for ref in list(dict.fromkeys(ibm_refs))[:30]:
    print(ref)

print()
# Find all strings that look like URL paths
path_refs = re.findall(r'["\'](/[a-zA-Z][a-zA-Z0-9/_\-.]{5,60}(?:\?[a-zA-Z]{2}[^"\'\s]{0,50})?)["\']', js)
print("=== path strings ===")
for p in list(dict.fromkeys(path_refs))[:30]:
    print(p)
