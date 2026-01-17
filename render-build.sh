#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python Dependencies
pip install -r requirements.txt

# Download and install FFmpeg static build for Linux if not present
if [ ! -f ./ffmpeg ]; then
    echo "Downloading FFmpeg..."
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    
    echo "Extracting FFmpeg..."
    tar xvf ffmpeg-release-amd64-static.tar.xz
    
    # Move binaries to current folder so main.py can find them or add to PATH
    # The tar contains a folder like 'ffmpeg-6.1-amd64-static', find it and move binaries
    find . -name "ffmpeg" -type f -exec mv {} . \;
    find . -name "ffprobe" -type f -exec mv {} . \;
    
    # Cleanup
    rm ffmpeg-release-amd64-static.tar.xz
    rm -rf ffmpeg-*-amd64-static
    
    echo "FFmpeg installed."
fi
