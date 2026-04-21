import httpx
import re

H = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

JS_FILES = [
    "/js/main.js?v=JSKKGm4LsUZTLcWndrDxIaG_q5TczK_S9CWnvcyEvQ0",
    "/js/searchmain.js?v=o5FlVLKFvMKo1l0jzGRuBQI1YMIvZrP8Mt2FojJERSc",
]
BASE = "https://nps.usajobs.gov"

with httpx.Client(timeout=30, headers=H, follow_redirects=True) as client:
    for path in JS_FILES:
        r = client.get(f"{BASE}{path}")
        js = r.text
        print(f"\n=== {path[:50]} ({len(js)} chars) ===")

        # data.usajobs references
        if "data.usajobs" in js:
            for m in re.finditer(r"data\.usajobs", js):
                ctx = js[max(0, m.start()-100):m.end()+150]
                print(f"  data.usajobs context: {ctx}")

        # API key patterns
        key_hits = re.findall(r"[\"'`]([A-Za-z0-9+/=]{20,60})[\"'`]", js)
        # Filter to likely API keys (alphanumeric 30+ chars)
        likely_keys = [k for k in key_hits if len(k) > 30 and not k.startswith("http")]
        print(f"  Likely keys: {likely_keys[:5]}")

        # Authorization header patterns
        auth_patterns = re.findall(r"[Aa]uthorization[^\"'`]{0,30}[\"'`]([^\"'`]{10,80})[\"'`]", js)
        print(f"  Auth patterns: {auth_patterns[:5]}")

        # usajobs API call patterns
        api_calls = re.findall(r"[\"'`](/api[^\"'`]{5,80})[\"'`]", js)
        print(f"  /api paths: {list(set(api_calls))[:10]}")

        # config/env vars
        configs = re.findall(r"(?:apiKey|apiUrl|baseUrl|ApiKey)[^\"'`]{0,20}[\"'`]([^\"'`]{5,80})[\"'`]", js)
        print(f"  Config values: {configs[:5]}")
