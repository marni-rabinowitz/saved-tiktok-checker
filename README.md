# TikTok Link Tools

A comprehensive set of Python utilities for managing, validating, and organizing large collections of TikTok video links.

## 📌 Features

### ✅ 1. Validate TikTok Links (Automatic Validation)

`filter_tiktoks_oembed.py` reads a text file containing TikTok URLs and checks each one to determine whether it still exists.

- Normalizes TikTok URL formats
- Uses TikTok's oEmbed endpoint
- Detects working videos, deleted videos, private/restricted videos, and invalid URLs
- Outputs only valid links to a clean file
- Shows progress while scanning
- Includes a delay to avoid rate limits

**Default Input:** `tiktoks_dead.txt`  
**Default Output:** `tiktoks_cleaned.txt`

### 🔍 2. Open TikTok Links in Batches

`open_tiktoks.py` allows you to open large lists of TikTok links in batches without overwhelming your browser.

- Opens links in groups (default: 5 at a time)
- Pauses between batches until you press Enter
- Useful for manual review or verification
- Configurable batch size and source file

**Default Input:** `tiktoks.txt`

### 📊 3. Categorize and Organize TikToks

`categorize_tiktoks.py` automatically organizes your saved TikToks into categories based on content, authors, and hashtags.

- Extract metadata (title, author, thumbnail, hashtags)
- Auto-categorize by content type (Cooking, Fitness, Comedy, etc.)
- Group by author to see all videos from each creator
- Organize by hashtags to find videos with popular tags
- Generate detailed statistics about your collection

---

## 🚀 Usage

### Step 1: Install Dependencies

```bash
pip install requests
```

### Step 2: Validate Your Links

Clean your TikTok links to remove deleted or private videos:

```bash
python filter_tiktoks_oembed.py
```

This creates `tiktoks_cleaned.txt` with only valid links.

### Step 3: Categorize Your TikToks (Optional)

Organize your validated links into categories:

```bash
python categorize_tiktoks.py
```

This will:
1. Fetch metadata for each TikTok
2. Automatically categorize videos
3. Create organized folders with your videos

### Step 4: Batch Open Links for Review (Optional)

Manually review your TikToks in batches:

```bash
python open_tiktoks.py
```

---

## 📂 File Overview

### `filter_tiktoks_oembed.py`

This script normalizes TikTok URLs, sends requests to TikTok's oEmbed API, checks if each video exists, prints a status line for every link, and saves all valid links to `tiktoks_cleaned.txt`. Good for cleaning large datasets of TikTok links.

### `open_tiktoks.py`

This tool loads links from a text file, opens them in browser tabs in configurable batches, and waits for user input between batches. Perfect for human review workflows.

### `categorize_tiktoks.py`

This script fetches metadata for each TikTok, automatically categorizes videos based on content keywords, and organizes them into structured folders by category, author, and hashtag.

---

## 📁 Output Structure (After Categorization)

```
categorized_tiktoks/
├── cooking.txt              # Videos about cooking/food
├── fitness.txt              # Workout/health videos
├── comedy.txt               # Funny videos
├── diy.txt                  # DIY/tutorial videos
├── beauty.txt               # Makeup/beauty videos
├── dance.txt                # Dance videos
├── music.txt                # Music-related videos
├── travel.txt               # Travel/adventure videos
├── fashion.txt              # Fashion/style videos
├── tech.txt                 # Technology videos
├── pets.txt                 # Pet videos
├── education.txt            # Educational content
├── gaming.txt               # Gaming videos
├── uncategorized.txt        # Other videos
├── by_author/               # Videos organized by creator
│   ├── @username1.txt
│   ├── @username2.txt
│   └── ...
├── by_hashtag/              # Videos organized by hashtag
│   ├── #fyp.txt
│   ├── #viral.txt
│   └── ...
├── summary_report.txt       # Overall statistics
└── tiktok_metadata.json     # Full metadata for all videos
```

---

## 🏷️ Category Keywords

Videos are automatically categorized based on these keywords in their titles:

- **Cooking**: recipe, cooking, food, baking, chef, meal, cook
- **Fitness**: workout, fitness, gym, exercise, health, training
- **Comedy**: funny, comedy, humor, laugh, joke, meme
- **DIY**: diy, craft, howto, tutorial, make, build
- **Beauty**: makeup, beauty, skincare, hair, cosmetic
- **Dance**: dance, dancing, choreography, moves
- **Music**: music, song, singing, cover, artist
- **Travel**: travel, vacation, trip, adventure, explore
- **Fashion**: fashion, style, outfit, clothing, ootd
- **Tech**: tech, technology, gadget, phone, computer, ai
- **Pets**: pet, dog, cat, animal, puppy, kitten
- **Education**: learn, education, tutorial, howto, lesson, teach
- **Gaming**: game, gaming, gamer, gameplay, stream

---

## ⚙️ Customization

### Add Your Own Categories

Edit the `CATEGORY_KEYWORDS` dictionary in `categorize_tiktoks.py`:

```python
CATEGORY_KEYWORDS = {
    "Cooking": ["recipe", "cooking", "food", "baking"],
    "YourCategory": ["keyword1", "keyword2", "keyword3"],
    # Add more categories...
}
```

### Change Input/Output Files

Modify these variables at the top of the scripts:

```python
INPUT_FILE = "tiktoks_cleaned.txt"  # Your input file
OUTPUT_DIR = "categorized_tiktoks"  # Where to save organized videos
METADATA_FILE = "tiktok_metadata.json"  # Metadata file name
```

---

## 💡 Tips

1. **Rate Limiting**: The scripts wait between requests to avoid being rate-limited
2. **Large Collections**: For 100+ videos, categorization may take several minutes
3. **Metadata File**: The JSON file contains all metadata and can be used for custom analysis
4. **Multiple Categories**: Videos can belong to multiple categories if they match multiple keywords
5. **Batch Size**: Adjust the batch size in `open_tiktoks.py` based on your browser's capabilities

---

## 📋 Example Output (Categorization)

```
🎬 Loaded 150 TikTok links
🔍 Fetching metadata and categorizing...

[1/150] Processing: https://www.tiktok.com/@user/video/123...
  ✅ Title: Easy 5-Minute Pasta Recipe #cooking #recipe
  👤 Author: @chefmike
  📂 Categories: Cooking

...

📂 Organizing videos...

📁 Cooking: 23 videos → categorized_tiktoks/cooking.txt
📁 Comedy: 45 videos → categorized_tiktoks/comedy.txt
📁 Fitness: 12 videos → categorized_tiktoks/fitness.txt
...

👤 Organized by 87 authors → categorized_tiktoks/by_author
#️⃣ Found 42 popular hashtags → categorized_tiktoks/by_hashtag
📄 Summary report → categorized_tiktoks/summary_report.txt

✨ Done! Check the 'categorized_tiktoks' folder for organized videos.
```

---

## 🔧 Troubleshooting

### "❌ Error: tiktoks_cleaned.txt not found!"
Run `filter_tiktoks_oembed.py` first to create the cleaned links file.

### "❌ Failed to fetch" errors
Some videos may be private or deleted. The script will continue with the rest.

### Slow performance
The scripts respect rate limits. For large collections, consider:
- Running in batches
- Increasing `time.sleep()` value if you get rate limited

---

## 📦 Files in This Repository

- `filter_tiktoks_oembed.py` - Validation script using oEmbed API
- `open_tiktoks.py` - Batch browser opening tool
- `categorize_tiktoks.py` - Enhanced categorization script
- `tiktoks.txt` - Your original TikTok links
- `tiktoks_cleaned.txt` - Validated links (created by filter script)
- `tiktoks_dead.txt` - Links that no longer work

---

## 📄 License

Free to use and modify for personal projects.
