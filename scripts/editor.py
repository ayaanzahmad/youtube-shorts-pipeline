
import os
import shutil
import subprocess

def resize_videos():
    input_dir = os.path.join("videos", "raw_videos")  # Changed from "raw" to "raw_videos"
    edited_dir = os.path.join("videos", "edited")
    final_dir = os.path.join("videos", "final")

    os.makedirs(edited_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]
    if not files:
        print("⚠️ No videos found in /videos/raw_videos/")
        return

    processed_count = 0

    for file in files:
        input_path = os.path.join(input_dir, file)
        edited_path = os.path.join(edited_dir, file)
        final_path = os.path.join(final_dir, file)

        print(f"🎞️ Resizing {file}...")

        # Use FFmpeg to resize the video and optimize it
        command = [
            "ffmpeg", "-i", input_path,
            "-vf", "scale=720:1280",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # Better compression, fast preset
            "-c:a", "aac", "-b:a", "128k",
            "-y", edited_path
        ]

        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            shutil.copy(edited_path, final_path)  # Copy to final folder
            os.remove(input_path)  # Remove the original video from raw_videos
            os.remove(edited_path)  # Clean up edited video
            processed_count += 1
            print(f"✅ Successfully processed: {file}")

        except subprocess.CalledProcessError:
            print(f"❌ Failed to resize {file}. Skipping...")

    print(f"✅ Resized {processed_count} videos and moved to /videos/final/. Cleaned up /raw_videos/ and /edited/.")

if __name__ == "__main__":
    resize_videos()
