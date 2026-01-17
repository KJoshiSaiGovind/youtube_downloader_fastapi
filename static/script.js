document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('download-form');
    const input = document.getElementById('url-input');
    const btn = document.getElementById('download-btn');
    const loader = document.getElementById('loader');
    const videoList = document.getElementById('video-list');
    const toast = document.getElementById('toast');

    // Initial Fetch
    fetchVideos();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = input.value.trim();
        if (!url) return;

        setLoading(true);

        const formData = new FormData();
        formData.append('url', url);

        try {
            const response = await fetch('/download', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                showToast('Video downloaded successfully!', 'success');
                input.value = '';
                fetchVideos(); // Refresh list
            } else {
                showToast('Error: ' + data.message, 'error');
            }
        } catch (error) {
            showToast('Network error occurred', 'error');
        } finally {
            setLoading(false);
        }
    });

    async function fetchVideos() {
        try {
            const response = await fetch('/videos');
            const videos = await response.json();
            renderVideos(videos);
        } catch (error) {
            console.error('Failed to fetch videos', error);
        }
    }

    function renderVideos(videos) {
        videoList.innerHTML = '';
        if (videos.length === 0) {
            videoList.innerHTML = '<div style="text-align:center; color: #666; padding: 20px;">No downloads yet</div>';
            return;
        }

        videos.forEach(video => {
            const date = new Date(video.downloaded_at).toLocaleDateString();
            const statusClass = video.is_deleted ? 'status-deleted' : 'status-available';
            const statusText = video.is_deleted ? 'Deleted' : 'Available';

            const item = document.createElement('div');
            item.className = 'video-item';
            item.innerHTML = `
                <div class="video-info">
                    <div class="video-title" title="${video.title}">${video.title}</div>
                    <div class="video-date">${date}</div>
                </div>
                <span class="status-badge ${statusClass}">${statusText}</span>
            `;
            videoList.appendChild(item);
        });
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btn.disabled = true;
            btn.textContent = 'Downloading...';
            loader.style.display = 'block';
        } else {
            btn.disabled = false;
            btn.textContent = 'Download Video';
            loader.style.display = 'none';
        }
    }

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.style.borderColor = type === 'success' ? '#00ff88' : '#ff3333';
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
