import os
import json
import time
import shutil
import pickle
import hashlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Fallback hashtags if none are found in the description
DEFAULT_TECH_TAGS = [
    "FYP", "Tech", "AI", "Innovation", "YouTubeShorts", "Gadgets", "Trending",
    "SmartDevices", "FutureTech", "Robotics", "CyberSecurity", "MachineLearning",
    "WearableTech", "TechReview"
]

def extract_hashtags(description):
    """ Extract hashtags from description or fallback to defaults. """
    tags = [word for word in description.split() if word.startswith("#")]
    return tags if tags else DEFAULT_TECH_TAGS

def get_video_hash(video_path):
    """Generate hash of video file to detect duplicates"""
    hash_md5 = hashlib.md5()
    try:
        with open(video_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error generating hash for {video_path}: {e}")
        return None

def load_uploaded_videos():
    """Load list of already uploaded video hashes"""
    uploaded_file = "uploaded_videos.json"
    if os.path.exists(uploaded_file):
        with open(uploaded_file, 'r') as f:
            data = json.load(f)
            return set(data.get('uploaded_hashes', []))
    return set()

def save_uploaded_video(video_hash, video_id, title):
    """Save uploaded video info to prevent duplicates"""
    uploaded_file = "uploaded_videos.json"
    data = {
        'uploaded_hashes': list(load_uploaded_videos()),
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    data['uploaded_hashes'].append(video_hash)
    
    with open(uploaded_file, 'w') as f:
        json.dump(data, f, indent=2)

def upload_to_youtube():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print("Re-authenticating...")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)

    final_dir = os.path.join("videos", "final")
    uploaded_dir = os.path.join("videos", "uploaded")
    os.makedirs(uploaded_dir, exist_ok=True)

    files = sorted([f for f in os.listdir(final_dir) if f.endswith(".mp4")])
    
    # Load already uploaded videos to prevent duplicates
    uploaded_hashes = load_uploaded_videos()
    print(f"📋 Found {len(uploaded_hashes)} previously uploaded videos")

    uploaded_links = []

    for file in files:
        video_path = os.path.join(final_dir, file)
        json_path = os.path.join(final_dir, file.replace(".mp4", ".json"))

        if not os.path.exists(json_path):
            print(f"⚠️ Metadata missing for {file}, skipping...")
            continue

        # Check for duplicates using video hash
        video_hash = get_video_hash(video_path)
        if video_hash in uploaded_hashes:
            print(f"⏭️ Duplicate detected for {file}, skipping...")
            continue

        with open(json_path) as f:
            metadata = json.load(f)

        video_tags = extract_hashtags(metadata.get("description", ""))

        request_body = {
            "snippet": {
                "title": metadata.get("title", "Untitled Tech Short"),
                "description": metadata.get("description", ""),
                "tags": video_tags,
                "categoryId": "28",
            },
            "status": {
                "privacyStatus": "public",
                "madeForKids": False,
            }
        }

        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/*"
        )

        try:
            print(f"\n📤 Uploading: {file}")
            upload = youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=media
            )

            response = upload.execute()
            video_id = response.get("id")
            youtube_link = f"https://www.youtube.com/watch?v={video_id}"
            uploaded_links.append(youtube_link)

            print(f"✅ Uploaded: {video_id}")
            print(f"📺 Video URL: {youtube_link}")
            print(f"⬆️ Title: {request_body['snippet']['title']}")
            print(f"📝 Description: {request_body['snippet']['description']}")
            print(f"🏷️ Tags: {', '.join(video_tags)}")

            # Save video hash to prevent future duplicates
            save_uploaded_video(video_hash, video_id, request_body['snippet']['title'])

            shutil.move(video_path, os.path.join(uploaded_dir, file))
            shutil.move(json_path, os.path.join(uploaded_dir, file.replace(".mp4", ".json")))

        except Exception as e:
            print(f"❌ Upload failed for {file}: {e}")

        time.sleep(1)  # prevent hitting rate limits

    print("\n✅ All videos uploaded!")
    print("🔗 Uploaded video links:")
    for link in uploaded_links:
        print("   -", link)

    return uploaded_links

if __name__ == "__main__":
    upload_to_youtube()
