// Common utility functions for Media Viewer

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Get file extension
function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}

// Check if file is an image
function isImage(filename) {
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'];
    return imageExtensions.includes(getFileExtension(filename).toLowerCase());
}

// Check if file is a video
function isVideo(filename) {
    const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'];
    return videoExtensions.includes(getFileExtension(filename).toLowerCase());
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'danger');
    });
}

// Download file
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Handle loading states
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.getAttribute('data-original-text') || element.innerHTML;
    }
}

// Save original button text for loading states
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        if (!button.getAttribute('data-original-text')) {
            button.setAttribute('data-original-text', button.innerHTML);
        }
    });
});

function aiTagImage(imageName, btn) {
    const tagSpan = document.getElementById(`tags-${imageName}`);
    const spinner = btn.querySelector('.spinner-border');
    btn.disabled = true;
    if (spinner) spinner.style.display = 'inline-block';
    fetch(`/api/ai_tag/${imageName}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (tagSpan) tagSpan.innerText = data.tags.join(', ');
            showToast('Tags updated!', 'success');
        })
        .catch(() => {
            showToast('Failed to generate tags.', 'danger');
        })
        .finally(() => {
            btn.disabled = false;
            if (spinner) spinner.style.display = 'none';
        });
}

function createMediaCard(item) {
    const fileName = getFileName(item.gcs_path);
    const isVideo = item.gcs_path.match(/\.(mp4|avi|mov|wmv|flv|webm|mkv)$/i);
    const isImage = item.gcs_path.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i);
    let mediaIcon = '<i class="fas fa-file fa-2x text-secondary"></i>';
    if (isVideo) {
        mediaIcon = '<i class="fas fa-video fa-2x text-info"></i>';
    } else if (isImage) {
        mediaIcon = '<i class="fas fa-image fa-2x text-success"></i>';
    }
    // Add AI Tag button and tag display
    const tags = item.tags ? item.tags.join(', ') : '';
    return `
        <div class="col-lg-3 col-md-4 col-sm-6 mb-4">
            <div class="card h-100 border-0 shadow-sm media-card" onclick="openMediaModal('${item.id}')">
                <div class="card-body p-3 text-center">
                    <div class="media-thumbnail mb-3">
                        ${mediaIcon}
                    </div>
                    <h6 class="card-title small text-truncate">${fileName}</h6>
                    <p class="card-text small text-muted">Click to view details</p>
                    <div class="mt-2">
                        <small class="text-muted">${formatFileSize(item.metadata?.size || 0)}</small>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-info" onclick="event.stopPropagation(); aiTagImage('${fileName}', this)">
                            <span class="spinner-border spinner-border-sm me-1" style="display:none;"></span>
                            <i class="fas fa-magic me-1"></i>AI Tag/Refresh Tag
                        </button>
                        <div class="mt-1"><strong>Tags:</strong> <span id="tags-${fileName}">${tags}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `;
} 