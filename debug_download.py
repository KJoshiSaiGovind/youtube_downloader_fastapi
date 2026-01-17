import yt_dlp
import os

# Test URL (Big Buck Bunny)
URL = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
OUTPUT_DIR = "debug_downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Options mirroring main.py but with verbose output
ydl_opts = {
    "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
    "format": "best[ext=mp4][protocol^=http][vcodec!=none][acodec!=none]",
    "noplaylist": True,
    "verbose": True, # Enable verbose logging
}

print(f"Attempting download of {URL}...")
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])
    print("Download success!")
except Exception as e:
    print(f"Download failed: {e}")
