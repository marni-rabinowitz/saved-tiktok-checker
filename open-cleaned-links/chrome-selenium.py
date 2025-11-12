from playwright.sync_api import sync_playwright

INPUT_FILE = "tiktoks_dead.txt"
OUTPUT_ALIVE = "tiktoks_alive.txt"
OUTPUT_DEAD = "tiktoks_dead_real.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

alive, dead = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(locale="en-US")
    page = context.new_page()

    for i, url in enumerate(links, 1):
        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(1200)
            html = page.content().lower()
            if "<video" in html and "this video is unavailable" not in html:
                alive.append(url)
                status = "✅ Alive"
            else:
                dead.append(url)
                status = "❌ Dead"
        except Exception:
            dead.append(url)
            status = "❌ Error"

        print(f"[{i}/{len(links)}] {status} – {url}")

    browser.close()

with open(OUTPUT_ALIVE, "w", encoding="utf-8") as f:
    f.write("\n".join(alive))
with open(OUTPUT_DEAD, "w", encoding="utf-8") as f:
    f.write("\n".join(dead))
