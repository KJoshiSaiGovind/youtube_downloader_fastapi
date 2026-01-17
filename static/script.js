document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('download-form');
    const input = document.getElementById('url-input');
    const btn = document.getElementById('download-btn');
    const loader = document.getElementById('loader');
    const videoList = document.getElementById('video-list');
    const toast = document.getElementById('toast');
    let pollInterval = null;

    // Initial Fetch
    fetchVideos();
    startPolling();

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
                showToast('Download started in background!', 'success');
                input.value = '';
                fetchVideos(); // Refresh list immediately
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

            // Check if any video is still processing
            const processing = videos.some(v => v.status === 'pending' || v.status === 'processing');
            if (processing && !pollInterval) {
                startPolling();
            } else if (!processing && pollInterval) {
                stopPolling();
            }
        } catch (error) {
            console.error('Failed to fetch videos', error);
        }
    }

    function startPolling() {
        if (pollInterval) return;
        pollInterval = setInterval(fetchVideos, 5000); // Poll every 5s
    }

    function stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
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

            let statusBadge = '';
            let statusClass = '';

            if (video.status === 'completed') {
                statusClass = video.is_deleted ? 'status-deleted' : 'status-available';
                statusBadge = video.is_deleted ? 'Deleted' : 'Available';
            } else if (video.status === 'failed') {
                statusClass = 'status-deleted';
                statusBadge = 'Failed';
            } else {
                statusClass = 'status-available'; // Creating a reuse for processing color
                statusBadge = video.status === 'processing' ? 'Processing...' : 'Pending';
                // Override color for processing
                if (video.status === 'processing' || video.status === 'pending') {
                    // Quick inline style hack or just use reuse
                }
            }

            const item = document.createElement('div');
            item.className = 'video-item';

            let html = `
                <div class="video-info">
                    <div class="video-title" title="${video.title}">${video.title}</div>
                    <div class="video-date">${date}</div>
            `;

            if (video.status === 'failed') {
                html += `<div style="color: #ff3333; font-size: 0.8rem; margin-top: 5px;">${video.error_msg || 'Unknown error'}</div>`;
            }

            html += `</div>
                <span class="status-badge ${statusClass}" style="${(video.status === 'processing' || video.status === 'pending') ? 'background: rgba(255, 200, 0, 0.1); color: #ffcc00;' : ''}">${statusBadge}</span>
            `;

            item.innerHTML = html;
            videoList.appendChild(item);
        });
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btn.disabled = true;
            btn.textContent = 'Starting...';
        } else {
            btn.disabled = false;
            btn.textContent = 'Download Video';
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
