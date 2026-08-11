// Meeting Mind AI - Javascript behaviors

// 1. Tab Switching
function switchTab(tab) {
    const fileTab = document.getElementById('file-tab');
    const textTab = document.getElementById('text-tab');
    const fileBtn = document.getElementById('tab-file-btn');
    const textBtn = document.getElementById('tab-text-btn');
    const sourceType = document.getElementById('source_type');

    if (!fileTab || !textTab || !fileBtn || !textBtn || !sourceType) return;

    if (tab === 'file') {
        fileTab.classList.add('active');
        textTab.classList.remove('active');
        fileBtn.classList.add('active');
        textBtn.classList.remove('active');
        sourceType.value = 'file';
    } else {
        textTab.classList.add('active');
        fileTab.classList.remove('active');
        textBtn.classList.add('active');
        fileBtn.classList.remove('active');
        sourceType.value = 'text';
    }
}

// 2. File Select & Drag-and-Drop Interaction
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

if (dropZone && fileInput) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Toggle visual drop zone hover state
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function triggerFileInput(event) {
    // Prevent browser file dialog if click was on the remove action button
    if (event.target.closest('.btn-remove')) return;
    if (fileInput) fileInput.click();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
        if (fileInput) {
            fileInput.files = files; // Assign files to file input
            handleFileSelect({ target: fileInput });
        }
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];

    // Client-side validations (for warning feedback)
    if (!file.name.toLowerCase().endsWith('.txt')) {
        showToast("Error: Only .txt transcript files are supported.");
        removeSelectedFile();
        return;
    }

    if (file.size > 2 * 1024 * 1024) {
        showToast("Error: File exceeds the 2 MB maximum limit.");
        removeSelectedFile();
        return;
    }

    // Display selected file card preview
    const promptView = document.getElementById('drop-zone-prompt');
    const cardView = document.getElementById('file-selected-card');
    const filenameText = document.getElementById('selected-filename');
    const filesizeText = document.getElementById('selected-filesize');

    if (promptView && cardView && filenameText && filesizeText) {
        filenameText.innerText = file.name;
        filesizeText.innerText = `${(file.size / 1024).toFixed(1)} KB`;

        promptView.classList.add('hidden');
        cardView.classList.remove('hidden');
    }
}

function removeSelectedFile(event) {
    if (event) event.stopPropagation();

    if (fileInput) fileInput.value = '';

    const promptView = document.getElementById('drop-zone-prompt');
    const cardView = document.getElementById('file-selected-card');

    if (promptView && cardView) {
        cardView.classList.add('hidden');
        promptView.classList.remove('hidden');
    }
}

// 3. Paste Word Counter
function updateWordCount(textarea) {
    const wordCounter = document.getElementById('word-counter');
    if (!wordCounter) return;

    const text = textarea.value.trim();
    const wordCount = text === '' ? 0 : text.split(/\s+/).length;

    wordCounter.innerText = `${wordCount} / 1500 words`;

    if (wordCount > 1500) {
        wordCounter.classList.add('over-limit');
    } else {
        wordCounter.classList.remove('over-limit');
    }
}

// Trigger initial word count on load if text is pre-populated
document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.getElementById('text-input');
    if (textarea && textarea.value.trim() !== '') {
        updateWordCount(textarea);
    }
});

// 4. Loading state validation on Form Submit
function showLoadingState(event) {
    const sourceType = document.getElementById('source_type').value;
    const loadingContainer = document.getElementById('loading-container');
    const inputCard = document.querySelector('.input-card');

    if (sourceType === 'file') {
        const hasFile = fileInput && fileInput.files.length > 0;
        if (!hasFile) {
            showToast("Please select a .txt transcript file to upload.");
            event.preventDefault();
            return;
        }
    } else {
        const textarea = document.getElementById('text-input');
        const text = textarea ? textarea.value.trim() : '';
        if (!text) {
            showToast("Please paste your transcript text first.");
            event.preventDefault();
            return;
        }

        const wordCount = text.split(/\s+/).length;
        if (wordCount > 1500) {
            showToast("Word count exceeds the 1500 limit. Please shorten your text.");
            event.preventDefault();
            return;
        }
    }

    // Hide input card and display loading spinner
    if (inputCard && loadingContainer) {
        inputCard.classList.add('hidden');
        loadingContainer.classList.remove('hidden');
    }
}

// 5. Copy Actions
function copyMarkdown() {
    const markdownElem = document.getElementById('markdown-raw');
    if (!markdownElem) return;

    const text = markdownElem.textContent;
    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied Markdown report to clipboard!");
    }).catch(err => {
        showToast("Copy failed: " + err);
    });
}

function copyJSON() {
    const jsonElem = document.getElementById('json-raw');
    if (!jsonElem) return;

    const text = jsonElem.textContent;
    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied raw JSON schema data to clipboard!");
    }).catch(err => {
        showToast("Copy failed: " + err);
    });
}

// 6. Alert toast trigger
function showToast(message) {
    const toast = document.getElementById('toast-container');
    if (!toast) return;

    toast.innerText = message;
    toast.classList.remove('hidden');
    
    // Clear any previous timeout
    if (window.toastTimeout) clearTimeout(window.toastTimeout);

    window.toastTimeout = setTimeout(() => {
        toast.classList.add('hidden');
    }, 2500);
}
