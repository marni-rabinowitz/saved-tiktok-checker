#!/usr/bin/env python3
"""
Quick comparison script to show the difference between keyword and ML categorization
"""

import json
from pathlib import Path

def compare_categorizations():
    """Compare results from both categorization methods."""
    
    # Check if both metadata files exist
    keyword_file = "tiktok_metadata.json"
    ml_file = "tiktok_metadata_ml.json"
    
    if not Path(keyword_file).exists():
        print(f"❌ {keyword_file} not found. Run categorize_tiktoks.py first.")
        return
    
    if not Path(ml_file).exists():
        print(f"❌ {ml_file} not found. Run categorize_tiktoks_ml.py first.")
        return
    
    # Load both files
    with open(keyword_file, 'r', encoding='utf-8') as f:
        keyword_data = json.load(f)
    
    with open(ml_file, 'r', encoding='utf-8') as f:
        ml_data = json.load(f)
    
    # Create URL-based lookup
    keyword_lookup = {v['url']: v for v in keyword_data}
    ml_lookup = {v['url']: v for v in ml_data}
    
    # Find common URLs
    common_urls = set(keyword_lookup.keys()) & set(ml_lookup.keys())
    
    if not common_urls:
        print("❌ No common videos found between the two files.")
        return
    
    print("=" * 80)
    print("🔍 Comparing Keyword vs ML Categorization")
    print("=" * 80)
    print()
    
    # Statistics
    same_category = 0
    different_category = 0
    improvements = []
    
    for url in list(common_urls)[:20]:  # Show first 20
        kw_video = keyword_lookup[url]
        ml_video = ml_lookup[url]
        
        kw_cats = set(kw_video.get('categories', []))
        ml_cats = set(ml_video.get('categories', []))
        ml_primary = ml_video.get('primary_category', 'Uncategorized')
        ml_confidence = ml_video.get('confidence', 0)
        
        # Check if categories match
        if kw_cats & ml_cats:  # If there's any overlap
            same_category += 1
        else:
            different_category += 1
            improvements.append((url, kw_cats, ml_primary, ml_confidence))
        
        # Display
        print(f"📹 {kw_video['title'][:60]}...")
        print(f"   Keyword: {', '.join(list(kw_cats)[:2])}")
        print(f"   ML:      {ml_primary} ({ml_confidence:.1%} confidence)")
        
        if ml_confidence > 0.3:
            print(f"   ✅ High confidence categorization")
        elif ml_confidence > 0.15:
            print(f"   ⚠️  Medium confidence")
        else:
            print(f"   ⚠️  Low confidence - mixed themes")
        print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total videos compared: {len(common_urls)}")
    print(f"Similar categorization: {same_category}")
    print(f"Different categorization: {different_category}")
    print()
    
    if improvements:
        print("🎯 ML provided more nuanced categorization for these videos:")
        for url, kw_cats, ml_cat, conf in improvements[:5]:
            print(f"  • {ml_cat} (was: {', '.join(list(kw_cats)[:2])})")
    
    print()
    print("💡 Key Differences:")
    print("  • Keyword: Fast, simple pattern matching")
    print("  • ML: Semantic understanding, confidence scores, handles ambiguity better")
    print()

if __name__ == "__main__":
    compare_categorizations()
