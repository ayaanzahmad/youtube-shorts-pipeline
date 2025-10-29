from scripts.editor import resize_videos
from scripts.openai_helper import process_videos
from scripts.tiktok_scraper import TikTokScraper
from uploader import upload_to_youtube
import os
import json
from datetime import datetime

def update_status(step, status, message='', count=0):
    """Update pipeline status for UI"""
    status_file = "pipeline_status.json"
    try:
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                data = json.load(f)
        else:
            data = {
                'current_step': None,
                'step1_download': {'status': 'pending', 'message': '', 'count': 0},
                'step2_resize': {'status': 'pending', 'message': '', 'count': 0},
                'step3_metadata': {'status': 'pending', 'message': '', 'count': 0},
                'step4_upload': {'status': 'pending', 'message': '', 'count': 0},
                'start_time': None,
                'running': False
            }
        
        data['running'] = True
        data['current_step'] = step
        
        if step == 'step1_download':
            data['step1_download']['status'] = status
            if count > 0:
                data['step1_download']['count'] = count
        elif step == 'step2_resize':
            data['step2_resize']['status'] = status
        elif step == 'step3_metadata':
            data['step3_metadata']['status'] = status
        elif step == 'step4_upload':
            data['step4_upload']['status'] = status
        
        with open(status_file, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

print("🔥 TikTok to YouTube Shorts automation started.")

# Initialize status with start time
try:
    with open("pipeline_status.json", 'r') as f:
        status_data = json.load(f)
    status_data['start_time'] = datetime.now().isoformat()
    status_data['running'] = True
    with open("pipeline_status.json", 'w') as f:
        json.dump(status_data, f, indent=2)
except:
    pass

# Initialize status
update_status('step1_download', 'processing', 'Starting download...')

# Step 1: Always try to get fresh videos first
print("📥 Attempting to get fresh TikTok videos...\n")

try:
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
        update_status('step1_download', 'error', 'No new videos found', 0)
        exit()
    
    print(f"✅ Downloaded {downloaded_count} fresh videos!\n")
    update_status('step1_download', 'success', f'Downloaded {downloaded_count} videos', downloaded_count)
    
    # Step 2: Resize videos
    print("\n🛠️ Resizing videos...")
    update_status('step2_resize', 'processing', 'Resizing videos...')
    resize_videos()
    update_status('step2_resize', 'success', 'Videos resized')
    
    # Step 3: Transcribe + GPT Metadata
    print("\n🧠 Generating metadata...")
    update_status('step3_metadata', 'processing', 'Generating metadata...')
    process_videos()
    update_status('step3_metadata', 'success', 'Metadata generated')
    
    # Step 4: Upload
    print("\n📤 Uploading to YouTube Shorts...")
    update_status('step4_upload', 'processing', 'Uploading videos...')
    upload_to_youtube()
    update_status('step4_upload', 'success', 'Videos uploaded')
    
    print("\n✅ All done!")
    
    # Mark pipeline as complete
    try:
        with open("pipeline_status.json", 'r') as f:
            data = json.load(f)
        data['running'] = False
        data['current_step'] = None
        data['end_time'] = datetime.now().isoformat()
        with open("pipeline_status.json", 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    try:
        with open("pipeline_status.json", 'r') as f:
            data = json.load(f)
        data['running'] = False
        data['current_step'] = None
        with open("pipeline_status.json", 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass
    raise
