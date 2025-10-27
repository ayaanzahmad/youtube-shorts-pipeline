from scripts.editor import resize_videos
from scripts.openai_helper import process_videos
from scripts.tiktok_scraper import TikTokScraper
from uploader import upload_to_youtube
import os

print("🔥 TikTok to YouTube Shorts automation started.")

# Step 1: Always try to get fresh videos first
print("📥 Attempting to get fresh TikTok videos...\n")

scraper = TikTokScraper()
downloaded_count = scraper.scrape_and_download()

if downloaded_count == 0:
    print("⚠️ No fresh videos downloaded.")
    print("💡 To get fresh videos:")
    print("   1. Visit TikTok.com and find tech videos")
    print("   2. Copy video URLs") 
    print("   3. Add them to scripts/tiktok_scraper.py")
    print("   4. Run the pipeline again")
    print("\n🛑 Exiting - no new content to process.")
    exit()

print(f"✅ Downloaded {downloaded_count} fresh videos!\n")

# Step 2: Resize videos
print("\n🛠️ Resizing videos...")
resize_videos()

# Step 3: Transcribe + GPT Metadata
print("\n🧠 Generating metadata...")
process_videos()

# Step 4: Upload
print("\n📤 Uploading to YouTube Shorts...")
upload_to_youtube()

print("\n✅ All done!")
