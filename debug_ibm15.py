"""
Capture the exact POST body and headers sent to www-api.ibm.com/search/api/v2.
"""
from playwright.sync_api import sync_playwright
import json

captured = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        if "www-api.ibm.com/search/api" in request.url:
            captured["url"] = request.url
            captured["method"] = request.method
            captured["headers"] = dict(request.headers)
            captured["post_data"] = request.post_data

    def on_response(response):
        if "www-api.ibm.com/search/api" in response.url:
            try:
                body = response.body()
                captured["response"] = body[:3000].decode("utf-8", "replace")
            except:
                pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading page...")
    page.goto("https://www.ibm.com/careers/search?sort=dcdate_desc", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    browser.close()

print("=== Request ===")
print(f"URL: {captured.get('url')}")
print(f"Method: {captured.get('method')}")
print(f"Headers: {json.dumps(captured.get('headers', {}), indent=2)}")
print(f"POST body: {captured.get('post_data', '')}")
print()
print("=== Response (first 2000 chars) ===")
resp = captured.get("response", "")
print(resp[:2000])

# Try to parse the response
try:
    data = json.loads(resp)
    hits = data.get("hits", {}).get("hits", [])
    print(f"\nTotal hits: {data['hits']['total']['value']}")
    print(f"Jobs in this page: {len(hits)}")
    if hits:
        print("First job sample:")
        print(json.dumps(hits[0].get("_source", {}), indent=2)[:1000])
except Exception as e:
    print(f"Parse error: {e}")
