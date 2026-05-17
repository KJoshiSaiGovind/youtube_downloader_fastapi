# 🎥 Modern YouTube Video Downloader

A lightweight, containerized web application built with **Python** and **FastAPI** that allows users to download YouTube videos in maximum HD quality. By leveraging **Docker**, the application natively packages **FFmpeg** alongside the Python runtime, eliminating complex system dependency installations on the host machine.

---

## 🚀 Key Features

* **FastAPI Powered:** Utilizes a high-performance, asynchronous Python web framework for handling incoming requests and file streaming efficiently.
* **Dockerized FFmpeg Integration:** Automatically merges separate high-quality video and audio streams from YouTube into a clean `.mp4` container without requiring manual system setup.
* **Automatic Server Cleanup:** Employs FastAPI `BackgroundTasks` to automatically wipe downloaded video files from local storage immediately after the transfer to the client is completed, keeping your infrastructure clean.
* **Clean UI:** Minimalist, mobile-friendly HTML/CSS interface served straight out of the FastAPI backend.

---

## 🛠️ Built With

* **[Python 3.11](https://www.python.org/)** - The core programming language powering the application logic.
* **[FastAPI](https://fastapi.tiangolo.com/)** - Selected for its speed, ease of building async endpoints, and lightweight footprint.
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - An advanced, actively maintained YouTube downloader fork utilized as the underlying extraction engine.
* **[Docker](https://www.docker.com/)** - Used to encapsulate the Python runtime and system-level FFmpeg utilities into an isolated container.

---

## 📦 System Architecture

When downloading high-definition video (1080p, 4K) from YouTube, the platform serves the video track and audio track completely separately. This app solves that architecture bottleneck seamlessly:

1. **User Request:** The user submits a URL via the FastAPI web interface.
2. **Async Processing:** FastAPI invokes `yt-dlp` to fetch both individual streams simultaneously.
3. **Muxing via FFmpeg:** The internal Dockerized FFmpeg layer merges (`muxes`) the audio and video into a single `.mp4` file.
4. **Streaming Pipe:** FastAPI streams the completed file back to your browser as an attachment.
5. **Auto-Garbage Collection:** FastAPI fires a background hook to delete the file from the container's temporary storage.

---

## ⚙️ Quick Start via Docker

The recommended deployment method is via Docker, as it handles the FFmpeg utility requirement natively.

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Build the Docker Image

Navigate to the root directory containing your project files and build the image:

```bash
docker build -t yt-downloader .
```


### 2. Spin up the Container

Run the container in detached mode, mapping port 8000 of your machine to the container's app layer:

**Bash**

```
docker run -d -p 8000:8000 --name youtube-downloader-app yt-downloader
```

### 3. Open the App

Launch your web browser and visit:
👉 **`http://127.0.0.1:8000`**

---

## 🔧 Useful Container Commands

Manage your application execution with these standard Docker terminal commands:

* **Check application status:**
  **Bash**

  ```
  docker ps

  ```

```
*   **Inspect backend logs (useful for download tracking/debugging):**
    ```bash
    docker logs youtube-downloader-app
  
```

* **Stop the application:**
  **Bash**

  ```
  docker stop youtube-downloader-app

  ```

```
*   **Restart the application:**
    ```bash
    docker start youtube-downloader-app
  
```

---

## ⚖️ Disclaimer

This project is built strictly for  **educational and personal use** . Downloading copyrighted content from third-party platforms without explicit authorization violates their respective Terms of Service. Use responsibly.

```

### 💡 Formatting Tip
When you place this text into a file named exactly `README.md` in your project folder, code hosting platforms
```
