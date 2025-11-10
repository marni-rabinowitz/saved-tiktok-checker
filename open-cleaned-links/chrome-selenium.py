import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ---------------- CONFIG ----------------
INPUT_FILE = "tiktoks_dead.txt"           # original tiktokv.com links
CANONICAL_FILE = "tiktoks_canonical.txt"
OUTPUT_ALIVE = "tiktoks_alive.txt"
OUTPUT_DEAD = "tiktoks_dead_real.txt"

CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"  # full path if needed
PAGE_LOAD_WAIT = 2                   # seconds to wait per page
MAX_TABS = 5                         # number of tabs to open concurrently
# ---------------------------------------

# --- Selenium setup ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # comment out to see browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--lang=en-US")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# --- Load links ---
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

total = len(links)
canonical_links = []
alive_links = []
dead_links = []

print(f"Loaded {total} links. Resolving canonical URLs...")

# --- Step 1: Resolve tiktokv.com → canonical TikTok URLs ---
for idx, url in enumerate(links, 1):
    try:
        driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)
        final_url = driver.current_url
        if "tiktok.com" in final_url.lower() and "/video/" in final_url:
            canonical_links.append(final_url)
            status = "✅ Resolved"
        else:
            final_url = url
            status = "❌ Could not resolve"
    except Exception:
        final_url = url
        status = "❌ Error"

    print(f"[{idx}/{total}] {status} – {final_url}")

# Save canonical URLs
with open(CANONICAL_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(canonical_links))

print(f"\nResolved {len(canonical_links)} canonical URLs out of {total} links.\n")

# --- Step 2: Multi-tab video existence check ---
print("Checking video existence (private = dead)...")

# Open extra tabs
for _ in range(MAX_TABS - 1):
    driver.execute_script("window.open('');")

tab_handles = driver.window_handles

for idx, url in enumerate(canonical_links, 1):
    tab_idx = (idx - 1) % MAX_TABS
    driver.switch_to.window(tab_handles[tab_idx])

    try:
        driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)
        txt = driver.page_source.lower()
        current_url = driver.current_url.lower()

        # Dead if deleted/unavailable/private/404/redirected away
        if ("video currently unavailable" in txt
            or "sorry, this video is no longer available" in txt
            or "this video is private" in txt
            or "page not found" in txt
            or "404" in txt
            or ("/video/" not in current_url)):
            alive = False
        else:
            alive = True

    except Exception:
        alive = False

    if alive:
        alive_links.append(url)
        status = "✅ Alive"
    else:
        dead_links.append(url)
        status = "❌ Dead"

    print(f"[{idx}/{len(canonical_links)}] {status} – {url}")

# --- Save results ---
with open(OUTPUT_ALIVE, "w", encoding="utf-8") as f:
    f.write("\n".join(alive_links))

with open(OUTPUT_DEAD, "w", encoding="utf-8") as f:
    f.write("\n".join(dead_links))

driver.quit()

print("\nFinished!")
print(f"Alive videos: {len(alive_links)}")
print(f"Dead videos:  {len(dead_links)}")
