import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, HTMLResponse
import yt_dlp

app = FastAPI(title="YouTube Downloader")

# Setup a temporary download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def cleanup_file(filepath: str):
    """Deletes the file from the server after the user has downloaded it."""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serves a clean, simple web interface for the downloader."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python YouTube Downloader</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 500px; text-align: center; }
            h1 { color: #ff0000; margin-bottom: 20px; }
            input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; font-size: 16px; }
            button { width: 100%; background-color: #ff0000; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
            button:hover { background-color: #cc0000; }
            .footer { margin-top: 20px; font-size: 12px; color: #777; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouTube Downloader</h1>
            <p>Paste your YouTube link below to download the video in MP4 format.</p>
            <form action="/download" method="POST">
                <input type="text" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
                <button type="submit">Download Video</button>
            </form>
            <div class="footer">Powered by FastAPI & yt-dlp</div>
        </div>
    </body>
    </html>
    """

@app.post("/download")
async def download_youtube_video(background_tasks: BackgroundTasks, url: str = Form(...)):
    """Processes the YouTube URL, downloads it locally, and streams it to the user."""
    outtmpl = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    ydl_opts = {
        # This forces it to download a single file that already has video and audio combined
        'format': 'best[ext=mp4]', 
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video metadata and download it
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            
            # Formulate the expected final extension path
            base, _ = os.path.splitext(filename)
            final_path = f"{base}.mp4"

        if not os.path.exists(final_path):
            raise HTTPException(status_code=500, detail="The file could not be processed correctly.")

        # Prepare the clean file name for the browser attachment header
        display_name = os.path.basename(final_path)

        # Registers the background task to delete the file after sending it
        background_tasks.add_task(cleanup_file, final_path)

        return FileResponse(
            path=final_path, 
            filename=display_name, 
            media_type='video/mp4'
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process video: {str(e)}")