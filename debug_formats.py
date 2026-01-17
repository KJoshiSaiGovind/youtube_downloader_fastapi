import yt_dlp

# Big Buck Bunny
URL = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"

ydl_opts = {
    "verbose": True,
    "listformats": True, # List formats instead of downloading
}

print(f"Listing formats for {URL}...")
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(URL, download=False)
except Exception as e:
    print(f"Extraction failed: {e}")
