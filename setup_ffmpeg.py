import os
import zipfile
import shutil
import urllib.request
import sys

FFMPEG_URL = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg")
ZIP_PATH = os.path.join(BASE_DIR, "ffmpeg.zip")

def download_ffmpeg():
    if os.path.exists(os.path.join(BASE_DIR, "ffmpeg.exe")):
        print("FFmpeg already exists.")
        return

    print(f"Downloading FFmpeg from {FFMPEG_URL}...")
    try:
        urllib.request.urlretrieve(FFMPEG_URL, ZIP_PATH)
        print("Download complete. Extracting...")
        
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(BASE_DIR)
            
        # Find the bin folder in extracted content
        extracted_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("ffmpeg-master")]
        if extracted_dirs:
            bin_dir = os.path.join(BASE_DIR, extracted_dirs[0], "bin")
            
            # Move ffmpeg.exe and ffprobe.exe to BASE_DIR
            for exe in ["ffmpeg.exe", "ffprobe.exe"]:
                src = os.path.join(bin_dir, exe)
                dst = os.path.join(BASE_DIR, exe)
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"Moved {exe} to project root.")
            
            # Cleanup
            print("Cleaning up...")
            shutil.rmtree(os.path.join(BASE_DIR, extracted_dirs[0]))
            os.remove(ZIP_PATH)
            print("FFmpeg setup complete.")
        else:
            print("Could not find extracted folder.")
            
    except Exception as e:
        print(f"Error installing FFmpeg: {e}")

if __name__ == "__main__":
    download_ffmpeg()
