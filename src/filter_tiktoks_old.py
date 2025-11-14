import requests
import time

INPUT_FILE = "tiktoks_dead.txt"
OUTPUT_FILE = "tiktoks_cleaned.txt"

# TikTok often blocks bots; realistic headers help avoid false 403s.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "text/html"
}

def tiktok_exists(url):
    try:
        # Use HEAD first (fast)
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=8)
        
        # Some TikTok links need GET to verify properly
        if r.status_code in (403, 404, 410, 451, 400):
            # Try GET in case HEAD is misleading
            r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=8)

        # ✅ Video exists if TikTok redirects to a valid viewer page
        if r.status_code == 200 and "Video currently unavailable" not in r.text:
            return True
        
        return False

    except Exception:
        return False


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    total = len(links)
    print(f"Loaded {total} links.\nChecking...")

    good_links = []
    for i, link in enumerate(links, 1):
        exists = tiktok_exists(link)
        status = "✅ OK" if exists else "❌ Gone"
        print(f"[{i}/{total}] {status} – {link}")

        if exists:
            good_links.append(link)

        # Avoid hitting TikTok too fast
        time.sleep(0.2)

    # Write output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(good_links))

    print(f"\nDone! Saved {len(good_links)} valid links to {OUTPUT_FILE}")
    print(f"Removed {total - len(good_links)} dead links.")


if __name__ == "__main__":
    main()
