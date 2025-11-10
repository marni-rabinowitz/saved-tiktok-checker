import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

INPUT_FILE = "tiktoks.txt"
OUTPUT_FILE = "tiktoks_cleaned_more.txt"
DEAD_FILE = "tiktoks_dead_less.txt"

MAX_WORKERS = 40

# Realistic TikTok mobile UA
TIKTOK_UA = (
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 "
    "AppName/TikTok AppVersion/34.1.3"
)

HEADERS = {
    "User-Agent": TIKTOK_UA,
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_maxsize=200, max_retries=1)
session.mount("https://", adapter)
session.mount("http://", adapter)


def expand_tiktokv(url):
    """Resolve tiktokv.com/share/video/... into a real TikTok URL."""
    try:
        r = session.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    except:
        return None

    # Final redirected URL
    final = r.url

    # Try to extract real redirect from meta refresh if stuck on tiktokv
    if "tiktokv.com" in final.lower():
        match = re.search(r'https://www\.tiktok\.com/[^\"]+', r.text)
        if match:
            return match.group(0)

    if "tiktok.com" in final.lower():
        return final

    return None


def check_exists(url):
    """
    Accurate existence check:
        ✅ 200 → ALIVE
        ✅ 301/302 → ALIVE
        ✅ 403 / Access Denied → ALIVE
        ✅ Bot-block pages → ALIVE
        ❌ 404 / 410 → DEAD
        ❌ Real "video unavailable" page → DEAD
    """
    try:
        r = session.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        txt = r.text.lower()

        # True dead detection
        if "video currently unavailable" in txt:
            return False
        if r.status_code in (404, 410):
            return False

        # ✅ Bot-block detection → ALIVE
        bot_block_signatures = [
            "access denied",
            "verify you're human",
            "verify you are human",
            "the request could not be satisfied",
            "cloudflare",
            "attention required",
            "please wait while we verify",
            "captcha",
            "restricted access",
        ]
        if any(sig in txt for sig in bot_block_signatures):
            return True

        # TikTok sometimes returns nearly empty HTML to bots
        if len(txt) < 500:
            return True

        # ✅ Normal success
        if r.status_code == 200:
            return True
        if r.status_code in (301, 302):
            return True
        if r.status_code == 403:
            return True  # always treat 403 as alive

    except:
        # Network failure → assume alive (fail-open)
        return True

    return True



def process(url):
    # Step 1: resolve share link
    real = expand_tiktokv(url)
    if not real:
        return (url, False)

    # Step 2: check if real link exists
    exists = check_exists(real)
    return (real, exists)


def main():
    with open(INPUT_FILE, "r") as f:
        links = [line.strip() for line in f if line.strip()]

    total = len(links)
    print(f"Loaded {total} links.\nResolving + checking...\n")

    good = []
    dead = []
    checked = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(process, url): url for url in links}

        for fut in as_completed(futures):
            orig = futures[fut]
            try:
                real, exists = fut.result()
            except:
                exists = True  # fail open (count as alive)
                real = orig

            checked += 1
            status = "✅ OK" if exists else "❌ Dead"
            print(f"[{checked}/{total}] {status} – {real}")

            if exists:
                good.append(real)
            else:
                dead.append(real)

    # Write results
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(good))

    with open(DEAD_FILE, "w") as f:
        f.write("\n".join(dead))

    print("\nFinished!")
    print(f"Alive:  {len(good)}")
    print(f"Dead:   {len(dead)}")


if __name__ == "__main__":
    main()
