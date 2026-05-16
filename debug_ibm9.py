import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

# Find the full context around 'careers' appId
idx = js.find('appId:"careers"')
if idx < 0:
    idx = js.find("appId:'careers'")
print("Context around careers appId:")
print(js[max(0,idx-200):idx+500])

print()
# Find all URL patterns built by string concatenation
# Look for http patterns in different string forms
for pat in [
    r'["\'](https?://[^"\']{20,120})["\']',
    r'\.get\(["\']([^"\']{10,80})["\']',
    r'\.post\(["\']([^"\']{10,80})["\']',
    r'url\s*[:=]\s*["\']([^"\']{10,100})["\']',
    r'host\s*[:=]\s*["\']([^"\']{5,60})["\']',
]:
    hits = re.findall(pat, js)
    relevant = [h for h in hits if any(k in h.lower() for k in ['ibm', 'search', 'api', 'career', 'job'])]
    if relevant:
        print(f"Pattern {pat[:30]}:")
        for h in list(dict.fromkeys(relevant))[:10]:
            print(f"  {h}")
        print()
