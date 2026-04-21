from playwright.sync_api import sync_playwright

captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        # Capture ALL cisco.com requests
        if "cisco.com" in url and not any(x in url for x in ["analytics", "google", "doubleclick", "linkedin", "bing", "adservice"]):
            captured.append({"type": "REQ", "method": request.method, "url": url, "body": request.post_data})

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "cisco.com" in url and not any(x in url for x in ["analytics", "google", "doubleclick", "linkedin", "bing"]):
            try:
                body = response.body()
                captured.append({"type": "RESP", "url": url, "ct": ct, "body": body[:300].decode("utf-8", "replace")})
            except:
                pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading page...")
    page.goto("https://careers.cisco.com/global/en/search-results", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)

    # Try clicking pagination - look for page 2 button
    try:
        page.locator("a[phw-tk='pagination_click']").nth(1).click(timeout=5000)
        page.wait_for_timeout(4000)
        print("Clicked pagination")
    except Exception as e:
        print(f"Pagination click: {e}")

    browser.close()

print(f"\nCaptured {len(captured)} cisco.com events:")
for c in captured:
    if c["type"] == "REQ":
        print(f"REQ {c['method']} {c['url'][:150]}")
        if c.get("body"):
            print(f"  body: {c['body'][:200]}")
    else:
        ct = c.get("ct","")
        if "json" in ct or "text" in ct:
            print(f"RESP [{ct[:30]}] {c['url'][:120]}")
            print(f"  {c['body'][:200]}")
    print()
