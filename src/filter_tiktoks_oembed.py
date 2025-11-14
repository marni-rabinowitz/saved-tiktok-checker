import requests
import time
import re

INPUT_FILE = "tiktoks_dead.txt"
OUTPUT_FILE = "tiktoks_cleaned.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "application/json",
}

def normalize_tiktok_url(url: str) -> str:
    """Convert tiktokv.com links to canonical tiktok.com format."""
    match = re.search(r'/video/(\d+)', url)
    if match:
        video_id = match.group(1)
        return f"https://www.tiktok.com/@_/video/{video_id}"
    return url

def tiktok_exists(video_url):
    try:
        normalized = normalize_tiktok_url(video_url)
        r = requests.get(
            "https://www.tiktok.com/oembed",
            params={"url": normalized},
            headers=HEADERS,
            timeout=10,
        )

        if r.status_code == 200:
            return True
        else:
            # Uncomment next line if you want to see failed reason
            # print(f"❌ {r.status_code} for {normalized}")
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
        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(good_links))

    print(f"\nDone! Saved {len(good_links)} valid links to {OUTPUT_FILE}")
    print(f"Removed {total - len(good_links)} dead links.")


if __name__ == "__main__":
    main()
