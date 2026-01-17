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
def process_video(video_id: int, url: str, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return

    video.status = "processing"
    db.commit()

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

    # Add cookies for authentication
    cookies_path = os.path.join(BASE_DIR, "cookies.txt")
    if os.path.exists(cookies_path):
        ydl_opts["cookiefile"] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown Title')
            
            # Update success
            video.status = "completed"
            video.title = title
            video.file_path = filename
            db.commit()
            
    except Exception as e:
        # Update failure
        video.status = "failed"
        video.error_msg = str(e)
        db.commit()

@app.post("/download")
async def download(
    background_tasks: BackgroundTasks, 
    url: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Create DB entry immediately
    new_video = Video(
        title="Processing...",
        url=url,
        status="pending"
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    # Start background task
    background_tasks.add_task(process_video, new_video.id, url, db)

    return JSONResponse({"status": "success", "message": "Download started in background"})

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
        "is_deleted": v.is_deleted,
        "status": v.status,
        "error_msg": v.error_msg
    } for v in videos]

@app.post("/check_status")
async def trigger_check_status(db: Session = Depends(get_db)):
    check_file_status(db)
    return {"status": "updated"}
