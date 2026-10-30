"""Mobile layout check (390x844, headless Chrome). Every API call is mocked; nothing reaches a real backend.

Run: cd frontend && VITE_API_URL=http://localhost:8999 npx vite --port 5199
Then: uv run --no-project --with playwright python scripts/checks/mobile_layout_check.py http://localhost:5199 out/mobile

Expected: stats box fits; /workspace/chat and /workspace/pdf have docHeight == viewport and
topbarTop == 0, also after 6 chat turns. Screenshots go to <prefix>_landing.png and <prefix>_chat.png.
Needs Google Chrome installed (channel="chrome"); see fix/mobile-layout for the before/after numbers."""
import json
import sys

from playwright.sync_api import sync_playwright

BASE, PREFIX = sys.argv[1], sys.argv[2]
SESSION = {"id": "s1", "title": "New chat", "mode": "chat", "created_at": "2026-10-30T00:00:00",
           "updated_at": "2026-10-30T00:00:00", "messages": [], "session_id": None, "documents": []}


def mock(route):
    url, method = route.request.url, route.request.method
    if url.endswith("/health"):
        body = {"status": "ok"}
    elif "/api/chat" in url:
        body = {"reply": "A fairly long mocked answer that wraps across a few lines on a phone screen. " * 3}
    elif "/api/sessions" in url and method == "GET" and url.rstrip("/").endswith("/api/sessions"):
        body = []
    elif "/api/sessions" in url and method == "POST":
        body = SESSION
    elif "/api/sessions/" in url:
        return route.fulfill(status=404, content_type="application/json", body=json.dumps({"detail": "nf"}))
    else:
        body = {}
    route.fulfill(status=200, content_type="application/json", body=json.dumps(body),
                  headers={"Access-Control-Allow-Origin": "*"})


def doc_metrics(page):
    return page.evaluate("""() => ({
        viewport: innerHeight,
        docHeight: document.scrollingElement.scrollHeight,
        scrollY: Math.round(scrollY),
        topbarTop: Math.round(document.querySelector('main > div').getBoundingClientRect().top),
    })""")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True,
                              device_scale_factor=2)
    page = ctx.new_page()
    page.route("**/localhost:8999/**", mock)

    page.goto(f"{BASE}/")
    page.wait_for_timeout(800)
    stats = page.evaluate("""() => {
        const label = [...document.querySelectorAll('div')].find(d => d.textContent.trim() === 'Core engine');
        const box = label.closest('.rounded-xl').getBoundingClientRect();
        return {left: Math.round(box.left), right: Math.round(box.right), width: innerWidth};
    }""")
    print("landing stats box:", stats, "fits:", stats["left"] >= 0 and stats["right"] <= stats["width"])
    page.screenshot(path=f"{PREFIX}_landing.png")

    for path in ("chat", "pdf"):
        page.goto(f"{BASE}/workspace/{path}")
        page.wait_for_timeout(800)
        print(f"/workspace/{path} on load:", doc_metrics(page))

    page.goto(f"{BASE}/workspace/chat")
    page.wait_for_timeout(800)
    box = page.get_by_role("textbox")
    for i in range(6):
        box.fill(f"question {i}")
        box.press("Enter")
        page.wait_for_timeout(2500)
    m = doc_metrics(page)
    print("/workspace/chat after 6 turns:", m)
    last = page.evaluate("""() => { const b = document.querySelectorAll('textarea')[0].getBoundingClientRect();
                                    return {inputBottom: Math.round(b.bottom)}; }""")
    print("chat input:", last)
    page.screenshot(path=f"{PREFIX}_chat.png")
    browser.close()
