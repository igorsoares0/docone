// File upload handling
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('file');
    const fileName = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('border-primary-500', 'bg-primary-50');
    }

    function unhighlight() {
        dropZone.classList.remove('border-primary-500', 'bg-primary-50');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            updateFileName(files[0]);
        }
    }

    // Handle file input change
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            updateFileName(this.files[0]);
        }
    });

    function updateFileName(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (file.size > maxSize) {
            fileName.textContent = 'File too large! Maximum size is 50MB';
            fileName.classList.add('text-red-600');
            submitBtn.disabled = true;
            return;
        }

        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'];

        if (!allowedTypes.includes(file.type)) {
            fileName.textContent = 'Invalid file type! Please upload PDF, DOCX, or PPTX';
            fileName.classList.add('text-red-600');
            submitBtn.disabled = true;
            return;
        }

        fileName.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
        fileName.classList.remove('text-red-600');
        fileName.classList.add('text-green-600');
        submitBtn.disabled = false;
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    // Handle form submission with progress
    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files || fileInput.files.length === 0) {
            return;
        }

        // Show progress bar
        uploadProgress.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 inline-block mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Uploading...';

        // Simulate progress (real progress requires XHR instead of form submit)
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressBar.style.width = progress + '%';
                progressPercent.textContent = progress + '%';
            }
        }, 200);

        // Note: For real progress tracking, we'd need to use XMLHttpRequest
        // For now, this provides visual feedback during upload
    });
});
