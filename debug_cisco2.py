from playwright.sync_api import sync_playwright
import json

captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if any(k in url for k in ["jobs", "search", "api", "refine"]) and "cisco" in url:
            captured.append({"type": "REQ", "method": request.method, "url": url, "body": request.post_data})

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "json" in ct and any(k in url for k in ["jobs", "search", "api", "refine"]) and "cisco" in url:
            try:
                body = response.body()
                captured.append({"type": "RESP", "url": url, "body": body[:500].decode("utf-8", "replace")})
            except:
                pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading page 1...")
    page.goto("https://careers.cisco.com/global/en/search-results", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    # Click next page to capture pagination request
    print("Clicking next page...")
    try:
        next_btn = page.locator("button[aria-label*='next'], a[aria-label*='next'], [class*='next']").first
        next_btn.click(timeout=5000)
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Next page click failed: {e}")

    browser.close()

print(f"\nCaptured {len(captured)} events:")
for c in captured:
    if c["type"] == "REQ":
        print(f"REQ {c['method']} {c['url'][:120]}")
        if c["body"]:
            print(f"  body: {c['body'][:200]}")
    else:
        print(f"RESP {c['url'][:120]}")
        print(f"  {c['body'][:200]}")
    print()
