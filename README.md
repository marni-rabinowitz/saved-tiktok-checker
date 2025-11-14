# TikTok Link Tools

This repository contains two Python utilities for working with large lists of TikTok video links:

1. **filter_tiktoks_oembed.py** — Checks which TikTok links are still valid using TikTok’s oEmbed API and generates a cleaned list.
2. **open_tiktoks.py** — Opens TikTok links in your browser in user-controlled batches for manual review.

---

## 📌 Features

### ✅ 1. Filter TikTok Links (Automatic Validation)

`filter_tiktoks_oembed.py` reads a text file containing TikTok URLs and checks each one to determine whether it still exists.

- Normalizes TikTok URL formats  
- Uses TikTok's oEmbed endpoint  
- Detects:  
  - Working videos  
  - Deleted videos  
  - Private or restricted videos  
  - Invalid URLs  
- Outputs only valid links to a clean file  
- Shows progress while scanning  
- Includes a delay to avoid rate limits  

**Default Input:** `tiktoks_dead.txt`  
**Default Output:** `tiktoks_cleaned.txt`

---

### 🔍 2. Open TikTok Links in Batches

`open_tiktoks.py` allows you to open large lists of TikTok links in batches without overwhelming your browser.

- Opens links in groups (default: 5 at a time)  
- Pauses between batches until you press Enter  
- Useful for manual review or verification  
- Configurable batch size and source file  

**Default Input:** `tiktoks.txt`

---

## 📂 File Overview

### `filter_tiktoks_oembed.py`

This script:

- Normalizes TikTok URLs  
- Sends requests to TikTok’s oEmbed API  
- Checks if each video exists  
- Prints a status line for every link  
- Saves all valid links to `tiktoks_cleaned.txt`  

Good for cleaning large datasets of TikTok links.

---

### `open_tiktoks.py`

This tool:

- Loads links from a text file  
- Opens them in browser tabs in configurable batches  
- Waits for user input between batches  

Perfect for human review workflows.

---

## 🚀 Usage

### 1. Install dependency
```bash
pip install requests
python filter_tiktoks_oembed.py
python open_tiktoks.py