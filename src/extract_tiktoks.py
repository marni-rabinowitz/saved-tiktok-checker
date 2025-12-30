import re

def extract_tiktok_links(input_file="uncategorized.txt", output_file="uncategorized_formatted.txt"):
    # Updated regex to match tiktokv.com as well
    pattern = re.compile(
        r"(https?://(?:www\.)?tiktok[a-z]*\.com/[^\s]+)",
        re.IGNORECASE
    )
    
    links = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            matches = pattern.findall(line)
            links.extend(matches)

    seen = set()
    unique_links = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    with open(output_file, "w", encoding="utf-8") as out:
        for link in unique_links:
            out.write(link + "\n")

    print(f"Done! Extracted {len(unique_links)} TikTok links into {output_file}")


extract_tiktok_links()
