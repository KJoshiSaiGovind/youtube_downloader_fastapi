import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import yt_dlp

# Create FastAPI app
app = FastAPI(title="YouTube Downloader")

# Templates folder
templates = Jinja2Templates(directory="templates")

# Downloads folder
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- API STATUS ROUTE ----------------
@app.get("/api")
def api_status():
    return {"message": "YouTube Downloader API is running"}

# ---------------- HOME PAGE (HTML FORM) ----------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------- DOWNLOAD ROUTE ----------------
@app.post("/download", response_class=HTMLResponse)
async def download_video(request: Request, url: str = Form(...)):
    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "format": "best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return templates.TemplateResponse(
            "success.html",
            {
                "request": request,
                "message": "Video downloaded successfully!"
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(e)
            }
        )
