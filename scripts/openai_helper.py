import os
import json
import subprocess
import shutil
import cv2
import numpy as np
import easyocr
from openai import OpenAI
from dotenv import load_dotenv

# ----- Env + OpenAI client ---------------------------------------------------
load_dotenv()  # reads .env in the project root
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Put it in your .env and keep .env out of git.")

client = OpenAI(api_key=OPENAI_API_KEY)

# ----- Paths -----------------------------------------------------------------
FINAL_DIR = os.path.join("videos", "final")
PROCESSED_AUDIO_DIR = os.path.join("videos", "processed", "audio")
PROCESSED_TRANSCRIPTS_DIR = os.path.join("videos", "processed", "transcripts")

os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
os.makedirs(PROCESSED_TRANSCRIPTS_DIR, exist_ok=True)

# ----- OCR -------------------------------------------------------------------
# GPU=False avoids surprise CUDA issues on laptops
ocr_reader = easyocr.Reader(['en'], gpu=False)

# ----- Helpers ---------------------------------------------------------------
def run_ffmpeg(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def extract_audio(video_path, audio_path):
    """Extract mono 16kHz WAV from video using ffmpeg."""
    cmd = ["ffmpeg", "-i", video_path, "-ac", "1", "-ar", "16000", "-vn", audio_path, "-y"]
    run_ffmpeg(cmd)
    print("🎵 Audio extracted:", audio_path)

def transcribe_with_whisper(audio_path) -> str:
    """Transcribe with Whisper API. Returns plain text (or '')."""
    print(f"🧠 Transcribing {audio_path} with {WHISPER_MODEL}...")
    try:
        with open(audio_path, "rb") as f:
            tx = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=f,
                response_format="text"
            )
        text = (tx or "").strip()
        return text
    except Exception as e:
        print(f"❌ Whisper API error: {e}")
        return ""

def extract_text_with_ocr(video_path) -> str:
    """Sample frames and OCR any on-screen text."""
    print(f"📸 OCR scanning video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Could not open video for OCR.")
        return ""

    text_chunks = []
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 15
    frame_interval = max(int(fps * 2), 15)  # every ~2s

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            try:
                result = ocr_reader.readtext(gray)
                frame_text = " ".join([t[1] for t in result if len(t) >= 2]).strip()
                if frame_text:
                    text_chunks.append(frame_text)
            except Exception as e:
                print("OCR error on frame:", e)
        frame_count += 1

    cap.release()
    extracted = " ".join(text_chunks).strip()
    if extracted:
        print("✅ OCR found text (first 300 chars):", extracted[:300])
    else:
        print("⚠️ No readable on-screen text via OCR.")
    return extracted

def generate_metadata(prompt_text) -> str:
    """Use Chat Completions to produce Title + Description."""
    print("🤖 Generating title/description with OpenAI...")
    try:
        resp = client.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a YouTube Shorts coach for tech content. Be concise and punchy."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return ""

def process_videos():
    print("🚀 Script started!\n")
    if not os.path.isdir(FINAL_DIR):
        print(f"❌ Final directory not found: {FINAL_DIR}")
        return

    files = [f for f in os.listdir(FINAL_DIR) if f.lower().endswith(".mp4")]
    if not files:
        print("ℹ️ No .mp4 files found in videos/final.")
        return

    for file in files:
        base = os.path.splitext(file)[0]
        video_path = os.path.join(FINAL_DIR, file)
        audio_path = os.path.join(FINAL_DIR, base + ".wav")
        transcript_path = os.path.join(PROCESSED_TRANSCRIPTS_DIR, base + ".txt")
        json_path = os.path.join(FINAL_DIR, base + ".json")

        print(f"\n🧪 Processing {file}...")

        extract_audio(video_path, audio_path)
        transcript = transcribe_with_whisper(audio_path)

        # Fallback to OCR if Whisper is too short
        if not transcript or len(transcript.split()) < 10:
            print("⚠️ Whisper transcript short. Falling back to OCR…")
            transcript = extract_text_with_ocr(video_path)

        if not transcript or len(transcript.split()) < 10:
            print("❌ No usable transcript found. Skipping this video.")
            # Clean temp audio if created
            if os.path.exists(audio_path):
                os.remove(audio_path)
            continue

        # Build prompt for metadata
        prompt = (
            "Create a Title (<=10 words) and a Description (short summary + 10–12 trending hashtags) "
            "for a YouTube Short about this transcript:\n\n"
            f"{transcript}\n\n"
            "Format strictly as:\n"
            "Title: <title>\n"
            "Description: <one short paragraph + hashtags>"
        )

        metadata_response = generate_metadata(prompt)

        # Parse the response
        title = ""
        description = ""
        for line in metadata_response.splitlines():
            lower = line.lower().strip()
            if lower.startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif lower.startswith("description:"):
                description = line.split(":", 1)[1].strip()
            elif title and line.strip():
                description += (" " + line.strip())

        metadata = {"title": title, "description": description}

        # Save .json metadata
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Metadata saved for {file}!")
        print(f"⬆️ Title: {title}")
        print(f"📝 Description: {description[:120]}...")

        # Move processed artifacts
        if os.path.exists(audio_path):
            shutil.move(audio_path, os.path.join(PROCESSED_AUDIO_DIR, os.path.basename(audio_path)))
        with open(transcript_path, "w") as f:
            f.write(transcript)

    print("\n✅ All videos processed!")

if __name__ == "__main__":
    process_videos()
