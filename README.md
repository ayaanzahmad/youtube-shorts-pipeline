# TikTok to YouTube Shorts Automation

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
2. Find the `tech_video_urls` list (around line 50)
3. Add your URLs like this:
```python
tech_video_urls = [
    "https://www.tiktok.com/@username/video/1234567890",
    "https://www.tiktok.com/@username/video/0987654321",
    # Add more URLs here
]
```

### Step 4: Run the Pipeline
```bash
python3 run.py
```

## 🔄 Daily Workflow

1. **Morning**: Find 3-5 fresh tech TikTok videos
2. **Add URLs**: Update the scraper with new URLs
3. **Run Pipeline**: Execute `python3 run.py`
4. **Check Results**: Videos will be uploaded to YouTube automatically

## ⚠️ Important Notes

- **Fresh URLs Only**: Old URLs expire quickly
- **Quality Content**: Choose videos with good engagement
- **Upload Limits**: YouTube has daily upload limits
- **No Duplicates**: System automatically prevents re-uploads

## 🛠️ Troubleshooting

- **404 Errors**: URLs are expired, get fresh ones
- **Upload Limits**: Wait 24 hours for quota reset
- **No Videos**: Add more URLs to the scraper
- **Authentication**: Re-run if YouTube auth expires

## 📊 Current Status

- ✅ Pipeline: Working perfectly
- ✅ Duplicate Detection: Active
- ✅ AI Content Generation: Generating great titles/descriptions
- ⚠️ TikTok URLs: Need to be updated manually
- ⚠️ Upload Quota: Reset daily
