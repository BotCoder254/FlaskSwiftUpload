// File upload handling
const uploadForm = document.getElementById('uploadForm');
const dropzone = document.getElementById('dropzone-file');
const progressModal = document.getElementById('uploadProgress');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');

// File upload handling
dropzone.addEventListener('change', handleFileUpload);
uploadForm.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadForm.classList.add('border-blue-500');
});

uploadForm.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadForm.classList.remove('border-blue-500');
});

uploadForm.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadForm.classList.remove('border-blue-500');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

function handleFileUpload(e) {
    const files = e.target.files;
    handleFiles(files);
}

async function handleFiles(files) {
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files', file);
    });

    // Show progress modal
    progressModal.classList.remove('hidden');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                updateProgress(percentCompleted);
            }
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            // Refresh file list
            loadFiles();
            // Show success message
            showNotification('Files uploaded successfully!', 'success');
        } else {
            showNotification('Upload failed: ' + result.message, 'error');
        }
    } catch (error) {
        showNotification('Upload failed: ' + error.message, 'error');
    } finally {
        // Hide progress modal
        progressModal.classList.add('hidden');
        // Reset progress
        updateProgress(0);
    }
}

function updateProgress(percent) {
    progressBar.style.width = `${percent}%`;
    progressText.textContent = `${percent}%`;
}

// File listing
async function loadFiles(page = 1) {
    try {
        const response = await fetch(`/files?page=${page}`);
        const data = await response.json();
        
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        
        data.files.forEach(file => {
            const row = document.createElement('tr');
            row.className = 'bg-white border-b dark:bg-gray-800 dark:border-gray-700';
            row.innerHTML = `
                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    ${file.filename}
                </td>
                <td class="px-6 py-4">
                    ${file.mime_type}
                </td>
                <td class="px-6 py-4">
                    ${formatFileSize(file.size)}
                </td>
                <td class="px-6 py-4">
                    ${new Date(file.uploaded_at).toLocaleString()}
                </td>
                <td class="px-6 py-4">
                    <button onclick="downloadFile('${file._id}')" class="font-medium text-blue-600 dark:text-blue-500 hover:underline">Download</button>
                </td>
            `;
            fileList.appendChild(row);
        });
    } catch (error) {
        showNotification('Failed to load files: ' + error.message, 'error');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showNotification(message, type) {
    // Implementation depends on your preferred notification library
    console.log(`${type}: ${message}`);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});
