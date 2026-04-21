from playwright.sync_api import sync_playwright
import json

captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if "oracle" in url.lower() and any(k in url for k in ["job", "requisition", "search", "api", "hcm"]):
            if not any(x in url for x in ["analytics", "favicon", "cdn", "static", "css", "js", "png", "svg"]):
                captured.append({"type": "REQ", "method": request.method, "url": url, "body": request.post_data})

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "oracle" in url.lower() and "json" in ct and any(k in url for k in ["job", "requisition", "search", "api", "hcm"]):
            try:
                body = response.body()
                captured.append({"type": "RESP", "url": url, "body": body[:600].decode("utf-8", "replace")})
            except:
                pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading Oracle careers...")
    page.goto("https://careers.oracle.com/en/sites/jobsearch/jobs?mode=location", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)

    # Try clicking "Show More Jobs"
    try:
        btn = page.locator("button:has-text('Show More'), button:has-text('Load More'), button:has-text('more job')").first
        btn.click(timeout=5000)
        page.wait_for_timeout(3000)
        print("Clicked show more")
    except Exception as e:
        print(f"Show more click: {e}")

    browser.close()

print(f"\nCaptured {len(captured)} events:")
for c in captured:
    if c["type"] == "REQ":
        print(f"REQ {c['method']} {c['url'][:150]}")
        if c.get("body"):
            print(f"  body: {c['body'][:300]}")
    else:
        print(f"RESP {c['url'][:120]}")
        print(f"  {c['body'][:300]}")
    print()
