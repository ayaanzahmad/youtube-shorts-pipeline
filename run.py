import os
import json
import shutil
from datetime import datetime
from scripts.editor import resize_videos
from scripts.openai_helper import process_videos
from scripts.tiktok_scraper import TikTokScraper
from uploader import upload_to_youtube

STATUS_FILE = "pipeline_status.json"

def update_status(step_key, status, message="", count=None):
    """Update pipeline status for UI."""
    try:
        with open(STATUS_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, create a default structure
        data = {
            'current_step': None,
            'step1_download': {'status': 'pending', 'message': '', 'count': 0},
            'step2_resize': {'status': 'pending', 'message': '', 'count': 0},
            'step3_metadata': {'status': 'pending', 'message': '', 'count': 0},
            'step4_upload': {'status': 'pending', 'message': '', 'count': 0},
            'start_time': None,
            'end_time': None,
            'running': False
        }

    # Update general status
    if status == 'processing':
        data['running'] = True
        data['current_step'] = f"Running: {step_key.replace('_', ' ').title()}"
    
    # Update specific step
    if step_key in data:
        data[step_key]['status'] = status
        data[step_key]['message'] = message
        if count is not None:
            data[step_key]['count'] = count
            
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clear_workspace():
    """Cleans up directories and data files from previous runs."""
    print("🧹 Clearing workspace...")
    
    # Reset status file
    status = {
        'current_step': "Cleaning up...",
        'step1_download': {'status': 'pending', 'message': '', 'count': 0},
        'step2_resize': {'status': 'pending', 'message': '', 'count': 0},
        'step3_metadata': {'status': 'pending', 'message': '', 'count': 0},
        'step4_upload': {'status': 'pending', 'message': '', 'count': 0},
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'running': True
    }
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

    # Directories to clear
    video_dirs = ['videos/raw_videos', 'videos/edited', 'videos/final']
    for directory in video_dirs:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
    
    # Data files to clear
    data_files = ['tiktok_data.json', 'uploaded_videos.json']
    for file in data_files:
        if os.path.exists(file):
            os.remove(file)
            
    print("✅ Workspace cleared.")

def main():
    failed_step = None
    try:
        clear_workspace()

        # Step 1: Download Videos
        update_status('step1_download', 'processing', 'Downloading new videos...')
        scraper = TikTokScraper()
        downloaded_count = scraper.scrape_and_download()
        
        if downloaded_count == 0:
            message = "No new videos found. Add URLs to scripts/tiktok_scraper.py"
            print(f"⚠️ {message}")
            update_status('step1_download', 'error', message)
            # Since this is a critical error, we can stop the pipeline
            raise Exception("No new videos to process.")
        
        update_status('step1_download', 'success', f'Downloaded {downloaded_count} new videos!', count=downloaded_count)

        # Step 2: Resize Videos
        update_status('step2_resize', 'processing', 'Resizing videos for YouTube Shorts...')
        resize_videos()
        update_status('step2_resize', 'success', 'Videos resized successfully.')

        # Step 3: Generate Metadata
        update_status('step3_metadata', 'processing', 'Generating metadata (transcripts, titles)...')
        process_videos()
        update_status('step3_metadata', 'success', 'Metadata generated successfully.')

        # Step 4: Upload to YouTube
        update_status('step4_upload', 'processing', 'Uploading videos to YouTube...')
        upload_to_youtube()
        update_status('step4_upload', 'success', 'Videos uploaded successfully.')

        print("\n✅ All done!")

    except Exception as e:
        print(f"\n❌ An error occurred during the pipeline: {e}")
        # Try to determine which step failed
        with open(STATUS_FILE, 'r') as f:
            status_data = json.load(f)
        
        # Find the first processing step that isn't success or error
        steps = ['step1_download', 'step2_resize', 'step3_metadata', 'step4_upload']
        for step in steps:
            if status_data[step]['status'] == 'processing':
                failed_step = step
                break
        
        if failed_step:
            update_status(failed_step, 'error', str(e))
        
        # Mark pipeline as not running
        with open(STATUS_FILE, 'r') as f:
            data = json.load(f)
        data['running'] = False
        data['current_step'] = f"Error in: {failed_step or 'Unknown Step'}"
        data['end_time'] = datetime.now().isoformat()
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    else:
        # Mark pipeline as complete if no exceptions
        with open(STATUS_FILE, 'r') as f:
            data = json.load(f)
        data['running'] = False
        data['current_step'] = "✅ Pipeline finished!"
        data['end_time'] = datetime.now().isoformat()
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    print("🔥 TikTok to YouTube Shorts automation started.")
    main()
