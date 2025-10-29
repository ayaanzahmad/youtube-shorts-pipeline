import streamlit as st
import json
import os
import subprocess
import sys
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="TikTok to YouTube Shorts",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Status file path
STATUS_FILE = "pipeline_status.json"

def load_status():
    """Load pipeline status from file"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'current_step': None,
        'step1_download': {'status': 'pending', 'message': '', 'count': 0},
        'step2_resize': {'status': 'pending', 'message': '', 'count': 0},
        'step3_metadata': {'status': 'pending', 'message': '', 'count': 0},
        'step4_upload': {'status': 'pending', 'message': '', 'count': 0},
        'start_time': None,
        'end_time': None,
        'running': False
    }

def save_status(status):
    """Save pipeline status to file"""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF006E, #8338EC, #3A86FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .step-box {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .status-success { color: #28a745; font-weight: bold; }
    .status-processing { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def check_directories():
    dirs = {
        'raw_videos': 'videos/raw_videos',
        'edited': 'videos/edited',
        'final': 'videos/final',
        'uploaded': 'videos/uploaded',
    }
    return dirs

def count_files_in_dir(directory):
    if os.path.exists(directory):
        return len([f for f in os.listdir(directory) if f.endswith('.mp4')])
    return 0

def get_video_files(directory):
    if os.path.exists(directory):
        return sorted([f for f in os.listdir(directory) if f.endswith('.mp4')])
    return []

# Main UI
def main():
    st.markdown('<h1 class="main-header">🎬 TikTok to YouTube Shorts</h1>', unsafe_allow_html=True)
    st.markdown("### Automated Pipeline for Converting TikTok Videos to YouTube Shorts")
    
    # Load current status
    status = load_status()
    
    # Sidebar
    with st.sidebar:
        st.markdown("---")
        st.title("📊 Pipeline Status")
        
        # Status indicators
        if status.get('current_step'):
            st.info(f"🏃 {status['current_step']}")
        elif status.get('running'):
            st.warning("⏳ Pipeline running...")
        else:
            st.success("✅ Ready")
        
        if status.get('start_time'):
            try:
                start = datetime.fromisoformat(status['start_time'])
                elapsed = datetime.now() - start
                st.caption(f"⏱️ Elapsed: {str(elapsed).split('.')[0]}")
            except:
                pass
        
        st.markdown("---")
        st.title("📁 Video Directories")
        
        dirs = check_directories()
        for name, path in dirs.items():
            count = count_files_in_dir(path)
            if count > 0:
                st.write(f"📁 {name.replace('_', ' ').title()}: {count} files")
        
        st.markdown("---")
        
        # Statistics
        st.title("📊 Statistics")
        
        if os.path.exists('tiktok_data.json'):
            try:
                with open('tiktok_data.json', 'r') as f:
                    data = json.load(f)
                    st.write(f"📥 Downloaded: {len(data.get('downloaded_videos', []))} videos")
            except:
                pass
        
        if os.path.exists('uploaded_videos.json'):
            try:
                with open('uploaded_videos.json', 'r') as f:
                    data = json.load(f)
                    st.write(f"📤 Uploaded: {len(data.get('uploaded_hashes', []))} videos")
            except:
                pass
    
    # Main content area
    tabs = st.tabs(["🚀 Run Pipeline", "📝 Edit URLs", "📊 Statistics", "📁 View Files"])
    
    with tabs[0]:
        st.header("Pipeline Execution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Start Pipeline")
            st.markdown("Run the complete automation pipeline:")
            if st.button("▶️ Start Pipeline", type="primary", use_container_width=True, disabled=status.get('running', False)):
                subprocess.Popen([sys.executable, "run.py"])
                st.success("🚀 Pipeline started! Refreshing status...")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            st.markdown("### Reset Status")
            st.markdown("Clear current pipeline status:")
            if st.button("🔄 Reset Status", use_container_width=True):
                new_status = load_status()
                for key in new_status:
                    if isinstance(new_status[key], dict) and 'status' in new_status[key]:
                        new_status[key]['status'] = 'pending'
                        new_status[key]['message'] = ''
                        new_status[key]['count'] = 0
                new_status['current_step'] = None
                new_status['running'] = False
                save_status(new_status)
                st.rerun()
        
        # Pipeline steps display
        st.markdown("---")
        st.subheader("📋 Pipeline Steps")
        
        # Step 1: Download
        step1_status = status['step1_download']['status']
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 📥 Step 1: Download TikTok Videos")
                if status['step1_download']['count'] > 0:
                    st.success(f"✅ Downloaded {status['step1_download']['count']} videos")
            with col2:
                if step1_status == 'processing':
                    st.markdown('<p class="status-processing">⏳ Processing</p>', unsafe_allow_html=True)
                elif step1_status == 'success':
                    st.markdown('<p class="status-success">✅ Complete</p>', unsafe_allow_html=True)
                elif step1_status == 'error':
                    st.markdown('<p class="status-error">❌ Error</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p>⏸️ Pending</p>', unsafe_allow_html=True)
        
        # Step 2: Resize
        step2_status = status['step2_resize']['status']
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 🛠️ Step 2: Resize Videos to 720x1280")
            with col2:
                if step2_status == 'processing':
                    st.markdown('<p class="status-processing">⏳ Processing</p>', unsafe_allow_html=True)
                elif step2_status == 'success':
                    st.markdown('<p class="status-success">✅ Complete</p>', unsafe_allow_html=True)
                elif step2_status == 'error':
                    st.markdown('<p class="status-error">❌ Error</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p>⏸️ Pending</p>', unsafe_allow_html=True)
        
        # Step 3: Metadata
        step3_status = status['step3_metadata']['status']
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 🧠 Step 3: Generate Metadata (GPT + Whisper)")
            with col2:
                if step3_status == 'processing':
                    st.markdown('<p class="status-processing">⏳ Processing</p>', unsafe_allow_html=True)
                elif step3_status == 'success':
                    st.markdown('<p class="status-success">✅ Complete</p>', unsafe_allow_html=True)
                elif step3_status == 'error':
                    st.markdown('<p class="status-error">❌ Error</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p>⏸️ Pending</p>', unsafe_allow_html=True)
        
        # Step 4: Upload
        step4_status = status['step4_upload']['status']
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 📤 Step 4: Upload to YouTube Shorts")
            with col2:
                if step4_status == 'processing':
                    st.markdown('<p class="status-processing">⏳ Processing</p>', unsafe_allow_html=True)
                elif step4_status == 'success':
                    st.markdown('<p class="status-success">✅ Complete</p>', unsafe_allow_html=True)
                elif step4_status == 'error':
                    st.markdown('<p class="status-error">❌ Error</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p>⏸️ Pending</p>', unsafe_allow_html=True)
        
        # Auto-refresh
        if status.get('running'):
            time.sleep(2)
            st.rerun()
    
    with tabs[1]:
        st.header("📝 Manage TikTok URLs")
        st.markdown("Add or remove TikTok video URLs to download.")
        
        file_path = "scripts/tiktok_scraper.py"
        if os.path.exists(file_path):
            # Read the file and extract URLs
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract URLs from the file
            urls = []
            in_list = False
            for line in content.split('\n'):
                if 'tech_video_urls = [' in line or (in_list and line.strip().startswith('"')):
                    in_list = True
                    if '"https://www.tiktok.com' in line or '"https://tiktok.com' in line:
                        url = line.strip().replace('"', '').replace(',', '').replace("'", '')
                        urls.append(url)
                if in_list and line.strip() == ']':
                    in_list = False
            
            # Display current URLs in an editable format
            st.subheader("Current URLs")
            st.caption("One URL per line. Make sure URLs are fresh and working.")
            
            # Store URLs in session state if not already there
            if 'tiktok_urls' not in st.session_state:
                st.session_state.tiktok_urls = '\n'.join(urls) if urls else ''
            
            # Editable text area
            new_urls = st.text_area(
                "Edit URLs:", 
                value=st.session_state.tiktok_urls,
                height=200,
                help="Enter TikTok video URLs, one per line"
            )
            
            st.session_state.tiktok_urls = new_urls
            
            # URL validation function
            def is_valid_tiktok_url(url):
                url = url.strip()
                # Strip query parameters for validation
                url_clean = url.split('?')[0]
                return (
                    'tiktok.com' in url_clean and 
                    '/video/' in url_clean and
                    url_clean.startswith('http')
                )
            
            # Buttons to add and save
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save URLs to File", type="primary"):
                    # Parse URLs from text area and strip query parameters
                    all_urls = [url.strip() for url in new_urls.split('\n') if url.strip()]
                    url_list = []
                    invalid_urls = []
                    for url in all_urls:
                        if is_valid_tiktok_url(url):
                            # Strip query parameters before saving
                            clean_url = url.split('?')[0].strip()
                            url_list.append(clean_url)
                        else:
                            invalid_urls.append(url)
                    
                    if invalid_urls:
                        st.warning(f"⚠️ {len(invalid_urls)} invalid URL(s) found and skipped:")
                        for url in invalid_urls:
                            st.text(f"  • {url}")
                    
                    if url_list:
                        # Update the tiktok_scraper.py file
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                        
                        # Find the tech_video_urls list and replace it
                        new_lines = []
                        in_list = False
                        skip_until_bracket = False
                        
                        for i, line in enumerate(lines):
                            if 'tech_video_urls = [' in line:
                                new_lines.append(line)
                                in_list = True
                                # Skip existing URLs and add new ones
                                skip_until_bracket = True
                            elif skip_until_bracket and ']' in line and in_list:
                                # Add the new URLs
                                for url in url_list:
                                    new_lines.append(f'            "{url}",\n')
                                new_lines.append(line)
                                in_list = False
                                skip_until_bracket = False
                            elif skip_until_bracket:
                                # Skip old URLs
                                continue
                            else:
                                new_lines.append(line)
                        
                        # Write back to file
                        with open(file_path, 'w') as f:
                            f.writelines(new_lines)
                        
                        st.success(f"✅ Saved {len(url_list)} valid URL(s) to tiktok_scraper.py!")
                        st.rerun()
                    else:
                        st.error("❌ No valid TikTok URLs found. Please add proper URLs.")
                        st.info("""
                        **Valid TikTok URL format:**
                        ```
                        https://www.tiktok.com/@username/video/1234567890
                        ```
                        """)
            
            with col2:
                if st.button("➕ Quick Add URL"):
                    st.info("Enter a URL in the text area above, then click 'Save URLs to File'")
            
            # Show preview with validation
            st.markdown("### 📋 Preview & Validation")
            url_list_preview = [url.strip() for url in new_urls.split('\n') if url.strip()]
            valid_urls = [url.split('?')[0] for url in url_list_preview if is_valid_tiktok_url(url)]
            invalid_urls = [url for url in url_list_preview if not is_valid_tiktok_url(url) and url]
            
            if invalid_urls:
                st.error("❌ **Invalid URLs (these won't work):**")
                for url in invalid_urls:
                    st.text(f"  • {url}")
                st.caption("Make sure your URL looks like: https://www.tiktok.com/@username/video/1234567890")
            
            if valid_urls:
                st.success(f"✅ **{len(valid_urls)} Valid URL(s) ready to save:**")
                for i, url in enumerate(valid_urls, 1):
                    st.text(f"{i}. {url}")
            elif url_list_preview:
                st.warning("⚠️ No valid URLs yet. Check the format above.")
            else:
                st.info("💡 No URLs entered yet. Copy TikTok video URLs and paste them above.")
            
            # Instructions
            st.markdown("---")
            st.markdown("### ℹ️ Instructions")
            st.success("""
            **How to get TikTok URLs (IMPORTANT):**
            
            1. Go to [TikTok.com](https://tiktok.com) and log in if needed
            2. Search for #tech, #technology, #gadgets, etc.
            3. **Click on a video** - don't just copy from search results
            4. **Wait for the video to load** - you should see the full video page
            5. Look at your browser URL bar - it should look like:
               ```
               https://www.tiktok.com/@username/video/1234567890
               ```
            6. **Copy the entire URL** from the address bar (Cmd+L or F6 to select it)
            7. Paste it above (one URL per line)
            8. Click "💾 Save URLs to File"
            
            ⚠️ **Common mistakes:**
            - Don't copy from search result thumbnails
            - Don't copy share links
            - Make sure URL has `/video/` in it
            """)
            
        else:
            st.error("File not found: scripts/tiktok_scraper.py")
    
    with tabs[2]:
        st.header("📊 Statistics & Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if os.path.exists('tiktok_data.json'):
                try:
                    with open('tiktok_data.json', 'r') as f:
                        data = json.load(f)
                        count = len(data.get('downloaded_videos', []))
                        st.metric("Total Downloaded", count)
                except:
                    st.metric("Total Downloaded", "N/A")
            else:
                st.metric("Total Downloaded", 0)
        
        with col2:
            if os.path.exists('uploaded_videos.json'):
                try:
                    with open('uploaded_videos.json', 'r') as f:
                        data = json.load(f)
                        count = len(data.get('uploaded_hashes', []))
                        st.metric("Total Uploaded", count)
                except:
                    st.metric("Total Uploaded", "N/A")
            else:
                st.metric("Total Uploaded", 0)
        
        with col3:
            final_dir = "videos/final"
            count = count_files_in_dir(final_dir)
            st.metric("Ready for Upload", count)
        
        with col4:
            uploaded_dir = "videos/uploaded"
            count = count_files_in_dir(uploaded_dir)
            st.metric("Successfully Uploaded", count)
        
        st.markdown("---")
        st.subheader("📁 Current Videos in Directories")
        
        # Show videos in each directory
        dirs = check_directories()
        for name, path in dirs.items():
            files = get_video_files(path)
            if files or True:  # Always show to let user know directory exists
                with st.expander(f"📁 {name.replace('_', ' ').title()} ({len(files)} files)"):
                    if files:
                        for file in files:
                            st.write(f"📹 {file}")
                    else:
                        st.write("*No videos in this directory*")
    
    with tabs[3]:
        st.header("📁 Browse Video Files")
        
        for name, path in check_directories().items():
            files = get_video_files(path)
            if files:
                st.subheader(f"📁 {name.replace('_', ' ').title()}")
                for file in files:
                    file_size = os.path.getsize(os.path.join(path, file))
                    size_mb = file_size / (1024 * 1024)
                    st.write(f"📹 {file} ({size_mb:.2f} MB)")
                st.markdown("---")

if __name__ == "__main__":
    main()
