"""
TikTok ML Categorizer - Advanced version using Machine Learning
Uses NLP and semantic analysis for smarter categorization of TikTok videos
"""

import requests
import time
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

# Try to import ML libraries, provide helpful error messages if missing
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not installed. Install with:")
    print("   pip install scikit-learn numpy")
    print("   Falling back to keyword-based categorization\n")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    # Try to download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("📥 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not installed. Install with: pip install nltk")

INPUT_FILE = "tiktoks_cleaned.txt"
OUTPUT_DIR = "categorized_tiktoks_ml"
METADATA_FILE = "tiktok_metadata_ml.json"
MODEL_FILE = "category_model.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "application/json",
}

# Enhanced category definitions with training examples
CATEGORY_TRAINING_DATA = {
    "Cooking & Food": [
        "recipe easy quick meal dinner lunch breakfast",
        "cooking baking chef food kitchen delicious",
        "ingredients cook prepare tasty yummy",
        "restaurant foodie cuisine dish plate",
        "homemade healthy eating nutrition diet",
    ],
    "Fitness & Health": [
        "workout exercise gym fitness training",
        "health wellness yoga pilates cardio",
        "muscle strength weight loss bodybuilding",
        "running jogging sports athlete",
        "meditation mindfulness mental health",
    ],
    "Comedy & Entertainment": [
        "funny hilarious laugh comedy humor",
        "joke meme viral trending prank",
        "skit parody satire entertainment",
        "relatable reaction fail",
        "stand up comedian lol lmao",
    ],
    "DIY & Crafts": [
        "diy craft handmade creative project",
        "tutorial howto make build create",
        "woodworking painting drawing art",
        "sewing knitting crochet crafting",
        "upcycle repurpose renovation",
    ],
    "Beauty & Skincare": [
        "makeup beauty cosmetics skincare",
        "hair hairstyle tutorial glam",
        "foundation lipstick eyeshadow mascara",
        "routine morning night self care",
        "product review recommendation",
    ],
    "Dance & Performance": [
        "dance dancing choreography moves",
        "ballet hiphop contemporary jazz",
        "dancer performance stage routine",
        "tiktok dance trend challenge",
        "movement rhythm freestyle",
    ],
    "Music & Audio": [
        "music song singing cover remix",
        "artist musician guitar piano drums",
        "vocals melody harmony lyrics",
        "production beat instrumental",
        "concert live performance band",
    ],
    "Travel & Adventure": [
        "travel vacation trip adventure explore",
        "destination tourist beach mountain",
        "journey wanderlust backpacking",
        "hotel flight airplane sightseeing",
        "culture experience abroad international",
    ],
    "Fashion & Style": [
        "fashion style outfit clothing ootd",
        "trendy chic vintage aesthetic",
        "dress shirt pants shoes accessories",
        "shopping haul wardrobe closet",
        "designer brand model runway",
    ],
    "Technology & Gadgets": [
        "tech technology gadget device phone",
        "computer laptop tablet smartphone",
        "software app coding programming",
        "ai artificial intelligence machine learning",
        "innovation digital smart automation",
    ],
    "Pets & Animals": [
        "pet dog cat puppy kitten",
        "animal cute adorable fur baby",
        "training tricks behavior vet",
        "wildlife nature zoo rescue",
        "bird fish hamster rabbit",
    ],
    "Education & Learning": [
        "learn education tutorial lesson teach",
        "study school college university",
        "knowledge facts science history",
        "tip trick hack lifehack",
        "explain guide howto information",
    ],
    "Gaming & Esports": [
        "game gaming gamer gameplay",
        "video game console pc xbox playstation",
        "stream streaming twitch esports",
        "minecraft fortnite roblox valorant",
        "multiplayer online rpg fps",
    ],
    "Business & Career": [
        "business career entrepreneur startup",
        "work job office productivity",
        "money finance investing stocks",
        "success motivation hustle grind",
        "marketing sales strategy growth",
    ],
    "Parenting & Family": [
        "parenting parent mom dad family",
        "baby toddler kids children pregnancy",
        "motherhood fatherhood raising",
        "family life home household",
        "advice tips tricks hacks",
    ],
    "Home & Interior": [
        "home decor interior design house",
        "room bedroom living room kitchen",
        "furniture organization cleaning",
        "renovation remodel makeover",
        "aesthetic cozy minimalist",
    ],
    "Relationships & Dating": [
        "relationship dating love couple",
        "boyfriend girlfriend husband wife",
        "romance date anniversary valentine",
        "advice tips communication trust",
        "marriage engagement wedding",
    ],
    "Motivation & Inspiration": [
        "motivation inspiration quote positive",
        "mindset success growth mindfulness",
        "self improvement confidence believe",
        "goals dreams achieve ambition",
        "励志 uplift encourage empower",
    ],
}


class MLCategorizer:
    """Machine Learning-based categorizer using TF-IDF and cosine similarity."""
    
    def __init__(self):
        self.vectorizer = None
        self.category_vectors = {}
        self.categories = list(CATEGORY_TRAINING_DATA.keys())
        self.stop_words = self._get_stop_words()
        
    def _get_stop_words(self):
        """Get stop words for text preprocessing."""
        if NLTK_AVAILABLE:
            try:
                return set(stopwords.words('english'))
            except:
                pass
        # Fallback to basic stop words
        return {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags markers (keep the words)
        text = re.sub(r'[@#]', '', text)
        
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stop words if NLTK is available
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
                text = ' '.join([w for w in tokens if w not in self.stop_words and len(w) > 2])
            except:
                pass
        
        return text
    
    def train(self):
        """Train the categorizer on category examples."""
        if not ML_AVAILABLE:
            print("⚠️  ML not available, using keyword matching")
            return False
        
        print("🧠 Training ML categorizer...")
        
        # Prepare training data
        training_texts = []
        for category, examples in CATEGORY_TRAINING_DATA.items():
            training_texts.extend(examples)
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=1,
            max_df=0.95,
            stop_words='english'
        )
        
        # Fit vectorizer on all training data
        self.vectorizer.fit(training_texts)
        
        # Create vector representations for each category
        for category, examples in CATEGORY_TRAINING_DATA.items():
            # Combine all examples for this category
            category_text = ' '.join(examples)
            vector = self.vectorizer.transform([category_text])
            self.category_vectors[category] = vector
        
        print("✅ Training complete!")
        return True
    
    def categorize(self, text: str, top_n: int = 3, threshold: float = 0.15) -> List[Tuple[str, float]]:
        """
        Categorize text using ML.
        
        Args:
            text: Text to categorize
            top_n: Number of top categories to return
            threshold: Minimum similarity score to include category
            
        Returns:
            List of (category, confidence_score) tuples
        """
        if not ML_AVAILABLE or not self.vectorizer:
            # Fallback to keyword matching
            return self._keyword_categorize(text, top_n)
        
        # Preprocess and vectorize input text
        processed_text = self._preprocess_text(text)
        if not processed_text:
            return [("Uncategorized", 0.0)]
        
        text_vector = self.vectorizer.transform([processed_text])
        
        # Calculate similarity with each category
        similarities = {}
        for category, category_vector in self.category_vectors.items():
            similarity = cosine_similarity(text_vector, category_vector)[0][0]
            if similarity >= threshold:
                similarities[category] = similarity
        
        # Sort by similarity score
        sorted_categories = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_categories:
            return [("Uncategorized", 0.0)]
        
        return sorted_categories[:top_n]
    
    def _keyword_categorize(self, text: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Fallback keyword-based categorization."""
        text_lower = text.lower()
        scores = {}
        
        for category, examples in CATEGORY_TRAINING_DATA.items():
            # Extract keywords from examples
            keywords = set()
            for example in examples:
                keywords.update(example.split())
            
            # Count matching keywords
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                scores[category] = matches / len(keywords)
        
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_categories:
            return [("Uncategorized", 0.0)]
        
        return sorted_categories[:top_n]


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


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """Extract important keywords from text using simple frequency analysis."""
    if not text:
        return []
    
    # Simple preprocessing
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    words = text.split()
    
    # Common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are'}
    
    # Filter and count
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    word_counts = Counter(filtered_words)
    
    return [word for word, count in word_counts.most_common(top_n)]


def fetch_tiktok_metadata(video_url: str, categorizer: MLCategorizer) -> Optional[Dict]:
    """Fetch TikTok metadata via oEmbed API and categorize using ML."""
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
            title = data.get("title", "")
            author = data.get("author_name", "")
            
            metadata = {
                "url": video_url,
                "normalized_url": normalized,
                "title": title,
                "author_name": author,
                "author_url": data.get("author_url", ""),
                "thumbnail_url": data.get("thumbnail_url", ""),
                "provider_name": data.get("provider_name", ""),
            }
            
            # Extract hashtags
            metadata["hashtags"] = list(extract_hashtags(title))
            
            # Extract keywords
            metadata["keywords"] = extract_keywords(title)
            
            # ML-based categorization
            text_to_categorize = f"{title} {author}"
            category_results = categorizer.categorize(text_to_categorize, top_n=3, threshold=0.1)
            
            # Store categories with confidence scores
            metadata["categories"] = []
            metadata["category_scores"] = {}
            
            for category, score in category_results:
                metadata["categories"].append(category)
                metadata["category_scores"][category] = float(score)
            
            # Primary category is the one with highest confidence
            metadata["primary_category"] = category_results[0][0] if category_results else "Uncategorized"
            metadata["confidence"] = float(category_results[0][1]) if category_results else 0.0
            
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
    """Organize TikToks into category files with ML confidence scores."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Group by primary category
    category_videos = defaultdict(list)
    
    for video in all_metadata:
        primary = video.get("primary_category", "Uncategorized")
        category_videos[primary].append(video)
    
    # Save each category to a file
    for category, videos in sorted(category_videos.items()):
        # Sort by confidence score
        videos.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        filename = Path(output_dir) / f"{category.lower().replace(' ', '_').replace('&', 'and')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {category} ({len(videos)} videos)\n")
            f.write(f"# Sorted by ML confidence score\n\n")
            
            for video in videos:
                confidence = video.get("confidence", 0)
                f.write(f"{video['url']}\n")
                f.write(f"  Title: {video['title']}\n")
                f.write(f"  Author: {video['author_name']}\n")
                f.write(f"  Confidence: {confidence:.2%}\n")
                
                # Show all categories if multiple
                if len(video.get("categories", [])) > 1:
                    other_cats = [f"{cat} ({video['category_scores'].get(cat, 0):.2%})" 
                                 for cat in video['categories'][1:]]
                    f.write(f"  Also: {', '.join(other_cats)}\n")
                
                if video.get('keywords'):
                    f.write(f"  Keywords: {', '.join(video['keywords'])}\n")
                if video.get('hashtags'):
                    f.write(f"  Hashtags: {', '.join(video['hashtags'])}\n")
                f.write("\n")
        
        avg_confidence = sum(v.get("confidence", 0) for v in videos) / len(videos)
        print(f"📁 {category}: {len(videos)} videos (avg confidence: {avg_confidence:.2%}) → {filename}")


def organize_by_authors(all_metadata: List[Dict], output_dir: str):
    """Organize TikToks by author with category distribution."""
    author_dir = Path(output_dir) / "by_author"
    author_dir.mkdir(exist_ok=True)
    
    # Group by author
    author_videos = defaultdict(list)
    
    for video in all_metadata:
        author = video.get("author_name", "Unknown")
        author_videos[author].append(video)
    
    # Save each author to a file (only authors with 2+ videos)
    saved_count = 0
    for author, videos in sorted(author_videos.items()):
        if len(videos) < 2:
            continue
            
        safe_author = re.sub(r'[<>:"/\\|?*]', '_', author)
        filename = author_dir / f"{safe_author}.txt"
        
        # Count category distribution
        category_counts = Counter(v.get("primary_category", "Uncategorized") for v in videos)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Videos by {author} ({len(videos)} total)\n\n")
            f.write(f"Category distribution:\n")
            for cat, count in category_counts.most_common():
                f.write(f"  - {cat}: {count} videos\n")
            f.write("\n" + "="*60 + "\n\n")
            
            for video in videos:
                f.write(f"{video['url']}\n")
                f.write(f"  {video['title']}\n")
                f.write(f"  Category: {video.get('primary_category', 'Uncategorized')} ({video.get('confidence', 0):.2%})\n\n")
        
        saved_count += 1
    
    print(f"👤 Organized {saved_count} authors (with 2+ videos) → {author_dir}")


def organize_by_hashtags(all_metadata: List[Dict], output_dir: str, min_videos: int = 3):
    """Organize TikToks by hashtags with ML category insights."""
    hashtag_dir = Path(output_dir) / "by_hashtag"
    hashtag_dir.mkdir(exist_ok=True)
    
    # Group by hashtag
    hashtag_videos = defaultdict(list)
    
    for video in all_metadata:
        for hashtag in video.get("hashtags", []):
            hashtag_videos[hashtag].append(video)
    
    # Save popular hashtags
    popular_hashtags = {tag: videos for tag, videos in hashtag_videos.items() if len(videos) >= min_videos}
    
    for hashtag, videos in sorted(popular_hashtags.items(), key=lambda x: len(x[1]), reverse=True):
        # Category distribution for this hashtag
        category_counts = Counter(v.get("primary_category", "Uncategorized") for v in videos)
        top_category = category_counts.most_common(1)[0][0] if category_counts else "Mixed"
        
        filename = hashtag_dir / f"#{hashtag}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Hashtag: #{hashtag} ({len(videos)} videos)\n")
            f.write(f"# Primary category: {top_category}\n\n")
            
            f.write(f"Category distribution:\n")
            for cat, count in category_counts.most_common():
                percentage = (count / len(videos)) * 100
                f.write(f"  - {cat}: {count} videos ({percentage:.1f}%)\n")
            f.write("\n" + "="*60 + "\n\n")
            
            for video in videos:
                f.write(f"{video['url']}\n")
                f.write(f"  {video['title']}\n")
                f.write(f"  by {video['author_name']}\n")
                f.write(f"  Category: {video.get('primary_category', 'Uncategorized')}\n\n")
    
    print(f"#️⃣ Found {len(popular_hashtags)} popular hashtags (≥{min_videos} videos) → {hashtag_dir}")


def generate_ml_report(all_metadata: List[Dict], output_dir: str, categorizer: MLCategorizer):
    """Generate detailed ML analysis report."""
    report_file = Path(output_dir) / "ml_analysis_report.txt"
    
    # Collect statistics
    total_videos = len(all_metadata)
    unique_authors = len(set(v.get("author_name", "Unknown") for v in all_metadata))
    all_hashtags = set()
    category_counts = Counter()
    confidence_scores = []
    
    for video in all_metadata:
        all_hashtags.update(video.get("hashtags", []))
        primary_cat = video.get("primary_category", "Uncategorized")
        category_counts[primary_cat] += 1
        confidence_scores.append(video.get("confidence", 0))
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    high_confidence = sum(1 for s in confidence_scores if s >= 0.3)
    medium_confidence = sum(1 for s in confidence_scores if 0.15 <= s < 0.3)
    low_confidence = sum(1 for s in confidence_scores if s < 0.15)
    
    # Top authors by video count
    author_counts = Counter(v.get("author_name", "Unknown") for v in all_metadata)
    top_authors = author_counts.most_common(10)
    
    # Most common keywords
    all_keywords = []
    for video in all_metadata:
        all_keywords.extend(video.get("keywords", []))
    common_keywords = Counter(all_keywords).most_common(20)
    
    # Write report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("TikTok ML Categorization Analysis Report\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"🤖 ML MODEL INFORMATION:\n")
        f.write(f"  Algorithm: TF-IDF + Cosine Similarity\n")
        f.write(f"  Categories: {len(CATEGORY_TRAINING_DATA)}\n")
        f.write(f"  ML Available: {'Yes' if ML_AVAILABLE else 'No (using keyword fallback)'}\n\n")
        
        f.write(f"📊 OVERALL STATISTICS:\n")
        f.write(f"  Total Videos: {total_videos}\n")
        f.write(f"  Unique Authors: {unique_authors}\n")
        f.write(f"  Unique Hashtags: {len(all_hashtags)}\n")
        f.write(f"  Average Confidence: {avg_confidence:.2%}\n\n")
        
        f.write(f"🎯 CONFIDENCE DISTRIBUTION:\n")
        f.write(f"  High (≥30%):   {high_confidence} videos ({high_confidence/total_videos*100:.1f}%)\n")
        f.write(f"  Medium (15-30%): {medium_confidence} videos ({medium_confidence/total_videos*100:.1f}%)\n")
        f.write(f"  Low (<15%):    {low_confidence} videos ({low_confidence/total_videos*100:.1f}%)\n\n")
        
        f.write(f"📁 CATEGORY DISTRIBUTION:\n")
        for category, count in category_counts.most_common():
            percentage = (count / total_videos) * 100
            # Calculate average confidence for this category
            cat_videos = [v for v in all_metadata if v.get("primary_category") == category]
            cat_avg_conf = sum(v.get("confidence", 0) for v in cat_videos) / len(cat_videos)
            
            f.write(f"  {category:.<40} {count:>4} videos ({percentage:>5.1f}%) | Avg Conf: {cat_avg_conf:.2%}\n")
        
        f.write(f"\n👤 TOP 10 AUTHORS:\n")
        for i, (author, count) in enumerate(top_authors, 1):
            # Find most common category for this author
            author_videos = [v for v in all_metadata if v.get("author_name") == author]
            author_categories = Counter(v.get("primary_category") for v in author_videos)
            top_cat = author_categories.most_common(1)[0][0] if author_categories else "Mixed"
            
            f.write(f"  {i:>2}. {author:<30} {count:>3} videos (mainly {top_cat})\n")
        
        f.write(f"\n🔑 TOP 20 KEYWORDS:\n")
        for keyword, count in common_keywords:
            f.write(f"  {keyword:<20} {count:>3} occurrences\n")
        
        f.write(f"\n#️⃣ SAMPLE HASHTAGS ({min(30, len(all_hashtags))} of {len(all_hashtags)}):\n")
        sample_hashtags = sorted(list(all_hashtags))[:30]
        # Format in columns
        for i in range(0, len(sample_hashtags), 5):
            hashtag_row = sample_hashtags[i:i+5]
            f.write(f"  {' '.join(f'#{tag:<12}' for tag in hashtag_row)}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("💡 INSIGHTS:\n")
        
        # Generate insights
        top_category = category_counts.most_common(1)[0]
        f.write(f"  • Most common category: {top_category[0]} ({top_category[1]} videos)\n")
        
        if avg_confidence >= 0.3:
            f.write(f"  • High average confidence ({avg_confidence:.2%}) indicates clear categorization\n")
        elif avg_confidence >= 0.15:
            f.write(f"  • Medium average confidence ({avg_confidence:.2%}) - videos have mixed themes\n")
        else:
            f.write(f"  • Low average confidence ({avg_confidence:.2%}) - videos may need manual review\n")
        
        if len(category_counts) < 5:
            f.write(f"  • Your collection focuses on {len(category_counts)} main categories\n")
        else:
            f.write(f"  • Your collection is diverse with {len(category_counts)} different categories\n")
        
        if unique_authors < total_videos * 0.5:
            f.write(f"  • You follow many creators consistently (high author repetition)\n")
        else:
            f.write(f"  • You explore content from many different creators\n")
    
    print(f"📄 ML Analysis report → {report_file}")


def main():
    print("=" * 70)
    print("🤖 TikTok ML Categorizer")
    print("=" * 70)
    print()
    
    # Initialize ML categorizer
    categorizer = MLCategorizer()
    ml_success = categorizer.train()
    
    if not ml_success:
        print("⚠️  Using keyword-based fallback categorization")
    print()
    
    # Load TikTok links
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE} not found!")
        print(f"Please make sure you have a file with TikTok links.")
        print(f"Run 'oembed.py' first to create it.")
        return

    total = len(links)
    print(f"🎬 Loaded {total} TikTok links")
    print(f"🔍 Analyzing with ML categorization...\n")

    # Fetch metadata for all videos
    all_metadata = []
    for i, link in enumerate(links, 1):
        print(f"[{i}/{total}] Processing: {link[:55]}...")
        metadata = fetch_tiktok_metadata(link, categorizer)
        
        if metadata:
            all_metadata.append(metadata)
            categories_str = " | ".join([f"{cat} ({metadata['category_scores'].get(cat, 0):.2%})" 
                                        for cat in metadata['categories'][:2]])
            print(f"  ✅ {metadata['title'][:50]}...")
            print(f"  👤 {metadata['author_name']}")
            print(f"  🎯 {categories_str}")
        
        # Rate limiting
        time.sleep(0.5)
        print()

    if not all_metadata:
        print("❌ No metadata could be fetched. Exiting.")
        return

    print(f"\n{'='*70}")
    print(f"✅ Successfully analyzed {len(all_metadata)}/{total} videos")
    print(f"{'='*70}\n")

    # Save metadata
    save_metadata(all_metadata, METADATA_FILE)

    # Organize videos
    print(f"\n📂 Organizing videos...\n")
    organize_by_categories(all_metadata, OUTPUT_DIR)
    organize_by_authors(all_metadata, OUTPUT_DIR)
    organize_by_hashtags(all_metadata, OUTPUT_DIR)
    
    # Generate ML analysis report
    generate_ml_report(all_metadata, OUTPUT_DIR, categorizer)

    print(f"\n{'='*70}")
    print(f"✨ Done! Check the '{OUTPUT_DIR}' folder for ML-categorized videos.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
