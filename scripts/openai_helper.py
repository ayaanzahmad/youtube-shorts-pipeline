import os
import json
import subprocess
import time
import shutil
import cv2
import numpy as np
import easyocr
import openai
from openai import OpenAI

# 🔐 Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")
# Directories
FINAL_DIR = os.path.join("videos", "final")
PROCESSED_AUDIO_DIR = os.path.join("videos", "processed", "audio")
PROCESSED_TRANSCRIPTS_DIR = os.path.join("videos", "processed", "transcripts")

# Ensure output directories exist
os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
os.makedirs(PROCESSED_TRANSCRIPTS_DIR, exist_ok=True)

# OCR reader
ocr_reader = easyocr.Reader(['en'])

def extract_audio(video_path, audio_path):
    """Extracts audio from video using ffmpeg"""
    cmd = ["ffmpeg", "-i", video_path, "-ac", "1", "-ar", "16000", "-vn", audio_path, "-y"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("🎵 Audio extracted.")

def transcribe_with_whisper(audio_path):
    """Uses OpenAI Whisper API to transcribe"""
    print(f"🧠 Transcribing {audio_path} using Whisper API...")
    try:
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        return transcript.strip()
    except Exception as e:
        print(f"❌ Whisper API error: {e}")
        return ""

def extract_text_with_ocr(video_path):
    print(f"📸 Extracting text from video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    text_data = []
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 2) if fps else 30

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            result = ocr_reader.readtext(gray)
            frame_text = " ".join([text[1] for text in result])
            if frame_text:
                text_data.append(frame_text)

        frame_count += 1

    cap.release()
    extracted = " ".join(text_data).strip()
    if extracted:
        print(f"✅ OCR Extracted Text:\n{extracted[:300]}")
    else:
        print("⚠️ No readable text found via OCR.")
    return extracted

def generate_metadata(prompt_text):
    print("🤖 Generating title and description with GPT...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_text}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT Error: {e}")
        return ""

def process_videos():
    print("🚀 Script started!\n")

    files = [f for f in os.listdir(FINAL_DIR) if f.endswith(".mp4")]
    for file in files:
        base = os.path.splitext(file)[0]
        video_path = os.path.join(FINAL_DIR, file)
        audio_path = os.path.join(FINAL_DIR, base + ".wav")
        transcript_path = os.path.join(FINAL_DIR, base + ".txt")
        json_path = os.path.join(FINAL_DIR, base + ".json")

        print(f"\n🧪 Processing {file}...")

        extract_audio(video_path, audio_path)
        transcript = transcribe_with_whisper(audio_path)

        if not transcript or len(transcript.split()) < 10:
            print("⚠️ Whisper transcript too short. Falling back to OCR...")
            transcript = extract_text_with_ocr(video_path)

        if not transcript or len(transcript.split()) < 10:
            print("❌ No usable transcript found. Skipping...")
            continue

        # Build GPT prompt
        prompt = f"""
You are a YouTube Shorts expert in the tech niche.
Here is the transcript of a TikTok video:
{transcript}

✅ Title (max 10 words):
✅ Description (short summary + 10-12 trending hashtags):
Format:
Title: ...
Description: ...
"""

        metadata_response = generate_metadata(prompt)

        # Parse the metadata response
        title = ""
        description = ""
        for line in metadata_response.splitlines():
            if line.lower().startswith("title:"):
                title = line.replace("Title:", "").strip()
            elif line.lower().startswith("description:"):
                description = line.replace("Description:", "").strip()
            elif title and line.strip():
                description += " " + line.strip()

        metadata = {
            "title": title,
            "description": description
        }

        # Save .json metadata
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Metadata saved for {file}!")
        print(f"⬆️ Title: {title}")
        print(f"📝 Description: {description[:100]}...")

        # Move processed files
        shutil.move(audio_path, os.path.join(PROCESSED_AUDIO_DIR, os.path.basename(audio_path)))
        with open(os.path.join(PROCESSED_TRANSCRIPTS_DIR, base + ".txt"), "w") as f:
            f.write(transcript)

    print("\n✅ All videos processed!")

# If run standalone
if __name__ == "__main__":
    process_videos()
