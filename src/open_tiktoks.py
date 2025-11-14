import webbrowser

# --- CONFIGURATION ---
BATCH_SIZE = 10
LINKS_FILE = "tiktoks_cleaned.txt"
# ----------------------

def open_links_in_batches(file_path):
    # Read all links from the file (bottom to top)
    with open(file_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()][::-1]

    total = len(links)
    print(f"Loaded {total} TikTok links (reading from bottom to top).\n")

    # Process in batches
    for i in range(0, total, BATCH_SIZE):
        batch = links[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\nOpening batch {batch_num}:")
        for link in batch:
            print(f"  - {link}")
            webbrowser.open_new_tab(link)

        remaining = total - (i + BATCH_SIZE)
        if remaining > 0:
            print(f"\n{remaining} links remaining.")
            input("Press Enter to open the next batch...")
        else:
            print("\nAll links have been opened!")

if __name__ == "__main__":
    open_links_in_batches(LINKS_FILE)
