# TikTok Categorizer

Automatically organize your saved TikToks into categories based on content, authors, and hashtags.

## Features

- ✅ **Validate TikTok links** - Check if videos still exist
- 📊 **Extract metadata** - Get title, author, thumbnail, hashtags
- 📁 **Auto-categorize** - Sort by content type (Cooking, Fitness, Comedy, etc.)
- 👤 **Group by author** - See all videos from each creator
- #️⃣ **Organize by hashtags** - Find videos with popular hashtags
- 📄 **Generate reports** - Get statistics about your collection

## Usage

### Step 1: Validate Your Links (Optional)

If you haven't already cleaned your links, run the validation script first:

```bash
python oembed.py
```

This creates `tiktoks_cleaned.txt` with only valid links.

### Step 2: Categorize Your TikToks

```bash
python categorize_tiktoks.py
```

This will:
1. Fetch metadata for each TikTok
2. Automatically categorize videos
3. Create organized folders with your videos

## Output Structure

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

## Category Keywords

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

## Customization

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

Modify these variables at the top of the script:

```python
INPUT_FILE = "tiktoks_cleaned.txt"  # Your input file
OUTPUT_DIR = "categorized_tiktoks"  # Where to save organized videos
METADATA_FILE = "tiktok_metadata.json"  # Metadata file name
```

## Requirements

```bash
pip install requests
```

## Tips

1. **Rate Limiting**: The script waits 0.5 seconds between requests to avoid being rate-limited
2. **Large Collections**: For 100+ videos, this may take several minutes
3. **Metadata File**: The JSON file contains all metadata and can be used for custom analysis
4. **Multiple Categories**: Videos can belong to multiple categories if they match multiple keywords

## Example Output

```
🎬 Loaded 150 TikTok links
🔍 Fetching metadata and categorizing...

[1/150] Processing: https://www.tiktok.com/@user/video/123...
  ✅ Title: Easy 5-Minute Pasta Recipe #cooking #recipe
  👤 Author: @chefmike
  📁 Categories: Cooking

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

## Troubleshooting

### "❌ Error: tiktoks_cleaned.txt not found!"
Run `oembed.py` first to create the cleaned links file.

### "❌ Failed to fetch" errors
Some videos may be private or deleted. The script will continue with the rest.

### Slow performance
The script respects rate limits. For large collections, consider:
- Running in batches
- Increasing `time.sleep()` value if you get rate limited

## Files in This Directory

- `oembed.py` - Original validation script
- `categorize_tiktoks.py` - **New!** Enhanced categorization script
- `tiktoks.txt` - Your original TikTok links
- `tiktoks_cleaned.txt` - Validated links (created by oembed.py)
- `tiktoks_dead.txt` - Links that no longer work

## License

Free to use and modify for personal projects.
