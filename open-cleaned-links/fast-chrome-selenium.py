import time
import threading
from queue import Queue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ---------------- CONFIG ----------------
INPUT_FILE = "tiktoks_dead.txt"
CANONICAL_FILE = "tiktoks_canonical.txt"
OUTPUT_ALIVE = "tiktoks_alive.txt"
OUTPUT_DEAD = "tiktoks_dead_real.txt"

CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
PAGE_LOAD_WAIT = 0.45
MAX_TABS = 5
N_THREADS = 5  # number of parallel threads
# ---------------------------------------

# Thread-safe queues for results
canonical_queue = Queue()
alive_queue = Queue()
dead_queue = Queue()

# --- Load links ---
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

total_links = len(links)
print(f"Loaded {total_links} links.")

# --- Chrome options ---
def get_chrome_options():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.page_load_strategy = "eager"
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.fonts": 2,
        "profile.managed_default_content_settings.media": 2,
        "profile.managed_default_content_settings.stylesheets": 1,
        "profile.managed_default_content_settings.javascript": 1,
    }
    options.add_experimental_option("prefs", prefs)
    return options

# --- Worker thread ---
def worker(link_subset, thread_id):
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=get_chrome_options())
    
    # Open extra tabs
    for _ in range(MAX_TABS - 1):
        driver.execute_script("window.open('');")
    tabs = driver.window_handles

    for idx, url in enumerate(link_subset, 1):
        try:
            driver.get(url)
            time.sleep(PAGE_LOAD_WAIT)
            final_url = driver.current_url.lower()

            # --- Invalid @/video/ rule ---
            if "/@/video/" in final_url:
                dead_queue.put(final_url)
                print(f"[Thread {thread_id}] ❌ Invalid (@/video/) – {final_url}")
                continue

            # Canonical check
            if "tiktok.com" in final_url and "/video/" in final_url and "/@/" not in final_url:
                canonical_queue.put(final_url)
                print(f"[Thread {thread_id}] ✅ Canonical – {final_url}")
            else:
                dead_queue.put(url)
                print(f"[Thread {thread_id}] ❌ Could not resolve – {url}")
                continue

            # --- Multi-tab video existence check ---
            tab_idx = (idx - 1) % MAX_TABS
            driver.switch_to.window(tabs[tab_idx])
            driver.get(final_url)
            time.sleep(PAGE_LOAD_WAIT)
            page_source = driver.page_source.lower()
            current_url = driver.current_url.lower()

            if "/@/" not in current_url or "/video/" not in current_url:
                alive = False
            elif (
                "video currently unavailable" in page_source
                or "sorry, this video is no longer available" in page_source
                or "this video is private" in page_source
                or "page not found" in page_source
                or "404" in page_source
            ):
                alive = False
            else:
                alive = True

            if alive:
                alive_queue.put(final_url)
                print(f"[Thread {thread_id}] ✅ Alive – {final_url}")
            else:
                dead_queue.put(final_url)
                print(f"[Thread {thread_id}] ❌ Dead – {final_url}")

        except Exception as e:
            dead_queue.put(url)
            print(f"[Thread {thread_id}] ❌ Error – {url} – {e}")

    driver.quit()

# --- Split links for threads ---
def chunkify(lst, n):
    """Split list into n roughly equal parts"""
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

link_chunks = chunkify(links, N_THREADS)

# --- Start threads ---
threads = []
for i, chunk in enumerate(link_chunks):
    t = threading.Thread(target=worker, args=(chunk, i+1))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# --- Save results ---
canonical_links = list(canonical_queue.queue)
alive_links = list(alive_queue.queue)
dead_links = list(dead_queue.queue)

with open(CANONICAL_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(canonical_links))

with open(OUTPUT_ALIVE, "w", encoding="utf-8") as f:
    f.write("\n".join(alive_links))

with open(OUTPUT_DEAD, "w", encoding="utf-8") as f:
    f.write("\n".join(dead_links))

print("\nFinished!")
print(f"Canonical links: {len(canonical_links)}")
print(f"Alive videos: {len(alive_links)}")
print(f"Dead videos:  {len(dead_links)}")
