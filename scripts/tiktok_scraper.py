import os
import json
import subprocess
import hashlib
from datetime import datetime
import requests

class TikTokScraper:
    def __init__(self):
        self.output_dir = os.path.join("videos", "raw_videos")
        self.metadata_file = "tiktok_data.json"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load existing metadata to track downloaded videos
        self.downloaded_videos = self.load_downloaded_videos()
    
    def load_downloaded_videos(self):
        """Load list of already downloaded video IDs to prevent duplicates"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('downloaded_videos', []))
            except (json.JSONDecodeError, FileNotFoundError):
                return set()
        return set()
    
    def save_downloaded_videos(self):
        """Save the list of downloaded video IDs"""
        data = {
            'downloaded_videos': list(self.downloaded_videos),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def download_video(self, video_url, video_id):
        """Download a single video using yt-dlp"""
        if video_id in self.downloaded_videos:
            print(f"⏭️ Video {video_id} already downloaded, skipping...")
            return None
        
        filename = f"{video_id}.%(ext)s"
        filepath = os.path.join(self.output_dir, filename)
        
        cmd = [
            "yt-dlp",
            "-o", filepath,
            "--format", "best",
            "--no-playlist",
            "--no-warnings",
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Find the actual downloaded file
                for file in os.listdir(self.output_dir):
                    if file.startswith(video_id):
                        downloaded_file = os.path.join(self.output_dir, file)
                        print(f"✅ Downloaded: {file}")
                        self.downloaded_videos.add(video_id)
                        return downloaded_file
            else:
                print(f"❌ Failed to download {video_id}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"❌ Download timeout for {video_id}")
            return None
        except Exception as e:
            print(f"❌ Error downloading {video_id}: {e}")
            return None
    
    def scrape_and_download(self):
        """Download videos from a curated list of popular tech TikTok URLs"""
        
        # Fresh, working TikTok URLs (you'll need to update these regularly)
        tech_video_urls = [
            # Add fresh TikTok URLs here - these need to be updated regularly
            # You can find these by browsing TikTok and copying video URLs
        ]
        
        if not tech_video_urls:
            print("⚠️ No TikTok URLs configured. Please add fresh URLs to the scraper.")
            print("💡 To get fresh URLs:")
            print("   1. Browse TikTok.com")
            print("   2. Find tech videos you like")
            print("   3. Copy the video URL")
            print("   4. Add it to the tech_video_urls list in tiktok_scraper.py")
            return 0
        
        print(f"🎬 Attempting to download {len(tech_video_urls)} tech videos...")
        
        downloaded_count = 0
        for i, url in enumerate(tech_video_urls):
            if downloaded_count >= 5:  # Limit to 5 videos per run
                break
                
            # Extract video ID from URL
            video_id = url.split('/')[-1]
            print(f"\n[{i+1}/{len(tech_video_urls)}] Processing: {video_id}")
            
            video_file = self.download_video(url, video_id)
            if video_file:
                downloaded_count += 1
        
        # Save metadata
        self.save_downloaded_videos()
        
        print(f"\n✅ Successfully downloaded {downloaded_count} new videos")
        return downloaded_count

def main():
    scraper = TikTokScraper()
    
    # Download videos
    downloaded_count = scraper.scrape_and_download()
    
    if downloaded_count > 0:
        print(f"\n🎉 Successfully downloaded {downloaded_count} fresh TikTok videos!")
        print("📁 Videos saved to: videos/raw_videos/")
        print("🔄 Ready to run the pipeline!")
    else:
        print("\n⚠️ No new videos downloaded.")
        print("💡 To get fresh videos:")
        print("   1. Visit TikTok.com and find tech videos")
        print("   2. Copy video URLs")
        print("   3. Add them to scripts/tiktok_scraper.py")
        print("   4. Run the pipeline again")

if __name__ == "__main__":
    main()