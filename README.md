# 🎬 TikTok to YouTube Shorts Automation

Automated pipeline to download TikTok videos, process them, and upload to YouTube Shorts with AI-generated titles and descriptions.

## ✨ Features

- 🎥 **Download TikTok Videos**: Automated download using yt-dlp
- 🛠️ **Video Processing**: Auto-resize to YouTube Shorts format (720x1280)
- 🧠 **AI Metadata**: GPT-3.5 generates titles and descriptions
- 🎙️ **Speech Recognition**: OpenAI Whisper transcribes audio
- 📤 **Auto-Upload**: Direct upload to YouTube Shorts
- 🎨 **Modern UI**: Beautiful Streamlit dashboard with real-time progress
- 🔄 **Duplicate Detection**: Prevents re-uploading the same video
- 📊 **Statistics**: Track downloads and uploads

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd tiktok-to-youtube-shorts

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. **Set up OpenAI API Key**: Update `config.json` with your OpenAI API key
2. **YouTube OAuth**: Place your `client_secrets.json` file in the root directory
3. **Add TikTok URLs**: Edit `scripts/tiktok_scraper.py` and add video URLs

### 3. Launch UI

```bash
# Launch the Streamlit UI
streamlit run app.py

# Or use the launch script
./launch_ui.sh
```

The UI will open at `http://localhost:8501`

## 📱 Using the UI

### Pipeline Execution Tab
- **Start Pipeline**: Run the complete automation
- **Real-time Progress**: Watch each step update in real-time
- **Reset Status**: Clear current status
- Live status indicators for:
  - 📥 Downloading videos
  - 🛠️ Resizing videos
  - 🧠 Generating metadata
  - 📤 Uploading to YouTube

### Edit URLs Tab
- View current TikTok URLs
- Instructions for adding new URLs
- Edit `scripts/tiktok_scraper.py` to update URLs

### Statistics Tab
- Total videos downloaded
- Total videos uploaded
- Videos ready for upload
- Successfully uploaded videos

### View Files Tab
- Browse videos in each directory
- File sizes and counts
- Navigate through processed files

## 🎯 How to Get Fresh TikTok Videos

Since TikTok blocks automated scraping, you need to manually add fresh video URLs:

### Step 1: Find Tech Videos on TikTok
1. Go to [TikTok.com](https://tiktok.com)
2. Search for hashtags like: #tech #technology #gadgets #ai #innovation
3. Browse and find videos you like

### Step 2: Copy Video URLs
1. Click on a video you want to download
2. Copy the URL from your browser (e.g., `https://www.tiktok.com/@username/video/1234567890`)
3. Make sure the video has good engagement (likes, views)

### Step 3: Add URLs to Scraper
1. Open `scripts/tiktok_scraper.py`
2. Find the `tech_video_urls` list (around line 80)
3. Add your URLs like this:
```python
tech_video_urls = [
    "https://www.tiktok.com/@username/video/1234567890",
    "https://www.tiktok.com/@username/video/0987654321",
    # Add more URLs here
]
```

### Step 4: Run via UI
1. Launch the UI: `streamlit run app.py`
2. Click "▶️ Start Pipeline" button
3. Watch real-time progress in the UI

## 🔄 Daily Workflow

1. **Morning**: Find 3-5 fresh tech TikTok videos
2. **Add URLs**: Update `scripts/tiktok_scraper.py` with new URLs
3. **Launch UI**: Run `streamlit run app.py`
4. **Start Pipeline**: Click the "Start Pipeline" button
5. **Monitor Progress**: Watch real-time updates in the UI
6. **Check Results**: Videos automatically uploaded to YouTube

## 📁 Project Structure

```
tiktok-to-youtube-shorts/
├── app.py                 # Streamlit UI application
├── run.py                 # Main pipeline script
├── uploader.py           # YouTube upload functionality
├── requirements.txt      # Python dependencies
├── launch_ui.sh         # Launch script
├── scripts/
│   ├── tiktok_scraper.py # TikTok video scraper
│   ├── editor.py         # Video resizing
│   └── openai_helper.py  # AI metadata generation
├── videos/
│   ├── raw_videos/       # Downloaded videos
│   ├── final/            # Processed videos ready for upload
│   ├── uploaded/         # Successfully uploaded videos
│   └── processed/        # Intermediate processing files
└── README.md
```

## ⚠️ Important Notes

- **Fresh URLs Only**: Old URLs expire quickly
- **Quality Content**: Choose videos with good engagement
- **Upload Limits**: YouTube has daily upload limits
- **No Duplicates**: System automatically prevents re-uploads
- **Real-time Updates**: UI auto-refreshes during pipeline execution

## 🛠️ Troubleshooting

- **UI not updating**: Click the refresh button or restart the app
- **404 Errors**: URLs are expired, get fresh ones
- **Upload Limits**: Wait 24 hours for quota reset
- **No Videos**: Add more URLs to the scraper
- **Authentication**: Re-run OAuth if YouTube auth expires

## 📊 Features

- ✅ Beautiful modern UI with real-time progress
- ✅ Pipeline status tracking
- ✅ Video statistics and analytics
- ✅ Duplicate detection
- ✅ AI content generation
- ✅ Auto-refresh during pipeline execution
- ✅ Detailed error messages
- ✅ Video file browser

## 🎉 Success!

The pipeline is now fully automated with a beautiful UI. Just add fresh TikTok URLs and click start!
