"""
TikTok Categorizer - Enhanced version of oembed.py
Fetches TikTok metadata and categorizes videos by author, keywords, hashtags, etc.
"""

import requests
import time
import re
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

INPUT_FILE = "tiktoks_cleaned.txt"
OUTPUT_DIR = "categorized_tiktoks"
METADATA_FILE = "tiktok_metadata.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "application/json",
}

# Keywords for auto-categorization
CATEGORY_KEYWORDS = {
    "Cooking": ["recipe", "cooking", "food", "baking", "chef", "meal", "cook"],
    "Fitness": ["workout", "fitness", "gym", "exercise", "health", "training"],
    "Comedy": ["funny", "comedy", "humor", "laugh", "joke", "meme"],
    "DIY": ["diy", "craft", "howto", "tutorial", "make", "build"],
    "Beauty": ["makeup", "beauty", "skincare", "hair", "cosmetic"],
    "Dance": ["dance", "dancing", "choreography", "moves"],
    "Music": ["music", "song", "singing", "cover", "artist"],
    "Travel": ["travel", "vacation", "trip", "adventure", "explore"],
    "Fashion": ["fashion", "style", "outfit", "clothing", "ootd"],
    "Tech": ["tech", "technology", "gadget", "phone", "computer", "ai"],
    "Pets": ["pet", "dog", "cat", "animal", "puppy", "kitten"],
    "Education": ["learn", "education", "tutorial", "howto", "lesson", "teach"],
    "Gaming": ["game", "gaming", "gamer", "gameplay", "stream"],
}


def normalize_tiktok_url(url: str) -> str:
    """Convert tiktokv.com links to canonical tiktok.com format."""
    match = re.search(r'/video/(\d+)', url)
    if match:
        video_id = match.group(1)
        return f"https://www.tiktok.com/@_/video/{video_id}"
    return url


def extract_hashtags(text: str) -> Set[str]:
    """Extract hashtags from text."""
    if not text:
        return set()
    return set(re.findall(r'#(\w+)', text.lower()))


def categorize_by_keywords(title: str, description: str = "") -> List[str]:
    """Automatically categorize based on keywords in title/description."""
    text = f"{title} {description}".lower()
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)
    
    return categories if categories else ["Uncategorized"]


def fetch_tiktok_metadata(video_url: str) -> Optional[Dict]:
    """Fetch TikTok metadata via oEmbed API."""
    try:
        normalized = normalize_tiktok_url(video_url)
        r = requests.get(
            "https://www.tiktok.com/oembed",
            params={"url": normalized},
            headers=HEADERS,
            timeout=10,
        )

        if r.status_code == 200:
            data = r.json()
            
            # Extract metadata
            metadata = {
                "url": video_url,
                "normalized_url": normalized,
                "title": data.get("title", ""),
                "author_name": data.get("author_name", ""),
                "author_url": data.get("author_url", ""),
                "thumbnail_url": data.get("thumbnail_url", ""),
                "provider_name": data.get("provider_name", ""),
                "version": data.get("version", ""),
                "html": data.get("html", ""),
            }
            
            # Extract hashtags from title
            metadata["hashtags"] = list(extract_hashtags(metadata["title"]))
            
            # Auto-categorize
            metadata["categories"] = categorize_by_keywords(metadata["title"])
            
            return metadata
        else:
            print(f"❌ Failed to fetch: {video_url} (Status: {r.status_code})")
            return None

    except Exception as e:
        print(f"❌ Error fetching {video_url}: {e}")
        return None


def save_metadata(all_metadata: List[Dict], filename: str):
    """Save all metadata to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved metadata to {filename}")


def organize_by_categories(all_metadata: List[Dict], output_dir: str):
    """Organize TikToks into category files."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Group by categories
    category_videos = defaultdict(list)
    
    for video in all_metadata:
        for category in video.get("categories", ["Uncategorized"]):
            category_videos[category].append(video)
    
    # Save each category to a file
    for category, videos in sorted(category_videos.items()):
        filename = Path(output_dir) / f"{category.lower().replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for video in videos:
                f.write(f"{video['url']}\n")
                f.write(f"  Title: {video['title']}\n")
                f.write(f"  Author: {video['author_name']}\n")
                if video.get('hashtags'):
                    f.write(f"  Hashtags: {', '.join(video['hashtags'])}\n")
                f.write("\n")
        
        print(f"📁 {category}: {len(videos)} videos → {filename}")


def organize_by_authors(all_metadata: List[Dict], output_dir: str):
    """Organize TikToks by author."""
    author_dir = Path(output_dir) / "by_author"
    author_dir.mkdir(exist_ok=True)
    
    # Group by author
    author_videos = defaultdict(list)
    
    for video in all_metadata:
        author = video.get("author_name", "Unknown")
        author_videos[author].append(video)
    
    # Save each author to a file
    for author, videos in sorted(author_videos.items()):
        safe_author = re.sub(r'[<>:"/\\|?*]', '_', author)
        filename = author_dir / f"{safe_author}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Videos by {author} ({len(videos)} total)\n\n")
            for video in videos:
                f.write(f"{video['url']}\n")
                f.write(f"  {video['title']}\n\n")
        
    print(f"👤 Organized by {len(author_videos)} authors → {author_dir}")


def organize_by_hashtags(all_metadata: List[Dict], output_dir: str):
    """Organize TikToks by hashtags."""
    hashtag_dir = Path(output_dir) / "by_hashtag"
    hashtag_dir.mkdir(exist_ok=True)
    
    # Group by hashtag
    hashtag_videos = defaultdict(list)
    
    for video in all_metadata:
        for hashtag in video.get("hashtags", []):
            hashtag_videos[hashtag].append(video)
    
    # Save top hashtags (at least 2 videos)
    popular_hashtags = {tag: videos for tag, videos in hashtag_videos.items() if len(videos) >= 2}
    
    for hashtag, videos in sorted(popular_hashtags.items(), key=lambda x: len(x[1]), reverse=True):
        filename = hashtag_dir / f"#{hashtag}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Hashtag: #{hashtag} ({len(videos)} videos)\n\n")
            for video in videos:
                f.write(f"{video['url']}\n")
                f.write(f"  {video['title']}\n")
                f.write(f"  by {video['author_name']}\n\n")
    
    print(f"#️⃣ Found {len(popular_hashtags)} popular hashtags → {hashtag_dir}")


def generate_summary_report(all_metadata: List[Dict], output_dir: str):
    """Generate a summary report."""
    report_file = Path(output_dir) / "summary_report.txt"
    
    # Collect statistics
    total_videos = len(all_metadata)
    unique_authors = len(set(v.get("author_name", "Unknown") for v in all_metadata))
    all_hashtags = set()
    category_counts = defaultdict(int)
    author_counts = defaultdict(int)
    
    for video in all_metadata:
        all_hashtags.update(video.get("hashtags", []))
        for category in video.get("categories", []):
            category_counts[category] += 1
        author_counts[video.get("author_name", "Unknown")] += 1
    
    # Top authors
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Write report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("TikTok Collection Summary Report\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"📊 Overall Statistics:\n")
        f.write(f"  Total Videos: {total_videos}\n")
        f.write(f"  Unique Authors: {unique_authors}\n")
        f.write(f"  Unique Hashtags: {len(all_hashtags)}\n\n")
        
        f.write(f"📁 Categories:\n")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_videos) * 100
            f.write(f"  {category}: {count} videos ({percentage:.1f}%)\n")
        
        f.write(f"\n👤 Top 10 Authors:\n")
        for i, (author, count) in enumerate(top_authors, 1):
            f.write(f"  {i}. {author}: {count} videos\n")
        
        f.write(f"\n#️⃣ Sample Hashtags ({min(20, len(all_hashtags))} of {len(all_hashtags)}):\n")
        sample_hashtags = sorted(list(all_hashtags))[:20]
        f.write(f"  {', '.join(f'#{tag}' for tag in sample_hashtags)}\n")
    
    print(f"📄 Summary report → {report_file}")


def main():
    # Load TikTok links
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE} not found!")
        print(f"Please make sure you have a file with TikTok links.")
        return

    total = len(links)
    print(f"🎬 Loaded {total} TikTok links")
    print(f"🔍 Fetching metadata and categorizing...\n")

    # Fetch metadata for all videos
    all_metadata = []
    for i, link in enumerate(links, 1):
        print(f"[{i}/{total}] Processing: {link[:50]}...")
        metadata = fetch_tiktok_metadata(link)
        
        if metadata:
            all_metadata.append(metadata)
            print(f"  ✅ Title: {metadata['title'][:60]}...")
            print(f"  👤 Author: {metadata['author_name']}")
            print(f"  📁 Categories: {', '.join(metadata['categories'])}")
        
        # Rate limiting
        time.sleep(0.5)
        print()

    if not all_metadata:
        print("❌ No metadata could be fetched. Exiting.")
        return

    print(f"\n{'='*60}")
    print(f"✅ Successfully fetched metadata for {len(all_metadata)}/{total} videos")
    print(f"{'='*60}\n")

    # Save metadata
    save_metadata(all_metadata, METADATA_FILE)

    # Organize videos
    print(f"\n📂 Organizing videos...\n")
    organize_by_categories(all_metadata, OUTPUT_DIR)
    organize_by_authors(all_metadata, OUTPUT_DIR)
    organize_by_hashtags(all_metadata, OUTPUT_DIR)
    
    # Generate summary
    generate_summary_report(all_metadata, OUTPUT_DIR)

    print(f"\n{'='*60}")
    print(f"✨ Done! Check the '{OUTPUT_DIR}' folder for organized videos.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
