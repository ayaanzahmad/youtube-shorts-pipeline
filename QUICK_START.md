# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Launch the UI

```bash
streamlit run app.py
```

The UI will automatically open in your browser at `http://localhost:8501`

## Step 3: Add TikTok URLs

1. Click on **"📝 Edit URLs"** tab in the UI
2. Follow the instructions to add TikTok video URLs
3. Edit `scripts/tiktok_scraper.py` and add URLs to the `tech_video_urls` list

## Step 4: Run the Pipeline

1. Go to **"🚀 Run Pipeline"** tab
2. Click **"▶️ Start Pipeline"** button
3. Watch real-time progress as the pipeline runs!

## What the UI Shows

### Real-Time Progress
- ✅ Which step is currently running
- ✅ Progress of each step (pending → processing → complete/error)
- ✅ Number of videos downloaded/uploaded
- ✅ Elapsed time

### Statistics
- 📊 Total downloads
- 📊 Total uploads
- 📊 Files ready for upload
- 📊 Files in each directory

### File Browser
- 📁 Browse all videos in different directories
- 📁 See file sizes
- 📁 View processed files

## Troubleshooting

**UI not showing updates?**
- Click "🔄 Reset Status" button
- Or restart the app

**No videos downloading?**
- Check if TikTok URLs are added in `scripts/tiktok_scraper.py`
- URLs expire quickly - add fresh ones

**Authentication errors?**
- Run the pipeline once to authenticate
- Or delete `token.pickle` and re-authenticate

## Tips

- ✅ Keep the UI open while pipeline runs for real-time updates
- ✅ The UI auto-refreshes every 2 seconds during pipeline execution
- ✅ Check the Statistics tab for overall progress
- ✅ Use View Files tab to browse all processed videos

Enjoy your automated TikTok to YouTube Shorts pipeline! 🎬

