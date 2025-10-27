import os
import json
import requests
import hashlib

# Paths
RAW_JSON_FILE = os.path.join("videos", "raw", "dataset_free-tiktok-scraper_2025-04-22_16-51-02-017.json")
DOWNLOAD_DIR = os.path.join("videos", "raw_videos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Load the JSON data
with open(RAW_JSON_FILE, "r") as f:
    data = json.load(f)

# Filter videos and collect URLs
filtered_videos = []
for item in data:
    digg_count = item.get("diggCount", 0)
    play_count = item.get("playCount", 0)
    media_urls = item.get("mediaUrls", [])

    if (
        media_urls and
        digg_count > 100 and
        play_count > 1000
    ):
        filtered_videos.append(media_urls[0])  # Use first media URL

print(f"Found {len(filtered_videos)} videos to download.\n")

# Download videos
def download_video(url, index):
    filename = hashlib.md5(url.encode()).hexdigest() + ".mp4"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[{index + 1}] Downloaded: {filename}")
    except Exception as e:
        print(f"[{index + 1}] Failed: {e}")

# Loop through and download
for idx, url in enumerate(filtered_videos):
    download_video(url, idx)
