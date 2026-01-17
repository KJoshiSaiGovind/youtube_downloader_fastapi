import os
import yt_dlp
from fastapi import FastAPI, Form, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import init_db, get_db, Video
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI()

# Initialize DB
init_db()

# Templates & Static
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

def check_file_status(db: Session):
    videos = db.query(Video).all()
    for video in videos:
        if video.file_path and not os.path.exists(video.file_path):
            video.is_deleted = True
        else:
            video.is_deleted = False
    db.commit()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download")
async def download(
    background_tasks: BackgroundTasks, 
    url: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Use a safe filename template
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
        "merge_output_format": "mp4",
    }

    # Verify connection to ffmpeg
    if os.path.exists(os.path.join(BASE_DIR, "ffmpeg.exe")):
        ydl_opts["ffmpeg_location"] = BASE_DIR
    elif os.path.exists(os.path.join(BASE_DIR, "ffmpeg")):
        ydl_opts["ffmpeg_location"] = BASE_DIR

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown Title')
            
            # Save to DB
            new_video = Video(
                title=title,
                url=url,
                file_path=filename,
                downloaded_at=datetime.datetime.utcnow()
            )
            db.add(new_video)
            db.commit()
            db.refresh(new_video)
            
            return JSONResponse({"status": "success", "message": "Download started", "video": {
                "title": title,
                "file_path": filename
            }})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/videos")
async def get_videos(db: Session = Depends(get_db)):
    # Update status before returning
    check_file_status(db)
    videos = db.query(Video).order_by(Video.downloaded_at.desc()).all()
    return [{
        "id": v.id,
        "title": v.title,
        "url": v.url,
        "file_path": v.file_path,
        "downloaded_at": v.downloaded_at.isoformat(),
        "is_deleted": v.is_deleted
    } for v in videos]

@app.post("/check_status")
async def trigger_check_status(db: Session = Depends(get_db)):
    check_file_status(db)
    return {"status": "updated"}
