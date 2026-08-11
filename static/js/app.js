let currentAnalysisData = null;
let currentMarkdownReport = "";
let selectedFile = null;

function switchTab(tab) {
    const fileTab = document.getElementById('file-tab');
    const textTab = document.getElementById('text-tab');
    const fileBtn = document.getElementById('tab-file-btn');
    const textBtn = document.getElementById('tab-text-btn');

    if (tab === 'file') {
        fileTab.classList.add('active');
        textTab.classList.remove('active');
        fileBtn.classList.add('active');
        textBtn.classList.remove('active');
    } else {
        textTab.classList.add('active');
        fileTab.classList.remove('active');
        textBtn.classList.add('active');
        fileBtn.classList.remove('active');
    }
}

function triggerFileInput(event) {
    // Prevent double trigger if clicking directly on remove button
    if (event.target.closest('.btn-remove')) return;
    const fileInput = document.getElementById('file-input');
    fileInput.click();
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files && files.length > 0) {
        selectedFile = files[0];
        showSelectedFileCard(selectedFile.name, selectedFile.size);
    }
}

function showSelectedFileCard(name, sizeInBytes) {
    const promptView = document.getElementById('drop-zone-prompt');
    const cardView = document.getElementById('file-selected-card');
    const filenameText = document.getElementById('selected-filename-text');
    const filesizeText = document.getElementById('selected-filesize-text');

    filenameText.innerText = name;
    filesizeText.innerText = `${(sizeInBytes / 1024).toFixed(1)} KB`;

    promptView.classList.add('hidden');
    cardView.classList.remove('hidden');
}

function removeSelectedFile(event) {
    if (event) event.stopPropagation();
    selectedFile = null;
    const fileInput = document.getElementById('file-input');
    fileInput.value = '';

    const promptView = document.getElementById('drop-zone-prompt');
    const cardView = document.getElementById('file-selected-card');

    cardView.classList.add('hidden');
    promptView.classList.remove('hidden');
}

async function submitAnalysis() {
    const loadingContainer = document.getElementById('loading-container');
    const errorContainer = document.getElementById('error-container');
    const resultsSection = document.getElementById('results-section');

    // Reset UI state
    errorContainer.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingContainer.classList.remove('hidden');

    const activeTab = document.getElementById('file-tab').classList.contains('active') ? 'file' : 'text';
    const formData = new FormData();

    if (activeTab === 'file') {
        const fileInput = document.getElementById('file-input');
        if (!selectedFile && fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
        }
        if (!selectedFile) {
            showError("Please select a .txt transcript file first.");
            loadingContainer.classList.add('hidden');
            return;
        }
        formData.append('transcript_file', selectedFile);
    } else {
        const textContent = document.getElementById('text-input').value.trim();
        if (!textContent) {
            showError("Please paste transcript text first.");
            loadingContainer.classList.add('hidden');
            return;
        }
        formData.append('transcript_text', textContent);
    }

    try {
        const response = await fetch('/api/analyze/', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || "Failed to analyze transcript.");
        }

        currentAnalysisData = result.data;
        currentMarkdownReport = result.markdown;

        renderResults(result.data);
        resultsSection.classList.remove('hidden');

    } catch (err) {
        showError(err.message);
    } finally {
        loadingContainer.classList.add('hidden');
    }
}

function showError(msg) {
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    errorMessage.innerText = msg;
    errorContainer.classList.remove('hidden');
}

function renderResults(data) {
    // 1. Executive Summary
    document.getElementById('summary-content').innerText = data.summary;

    // 2. Action Items Table (Renders EVERY action item)
    const tbody = document.getElementById('action-items-tbody');
    const countBadge = document.getElementById('action-items-count');
    tbody.innerHTML = '';

    const items = data.action_items || [];
    countBadge.innerText = `${items.length} item${items.length === 1 ? '' : 's'}`;

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No action items identified.</td></tr>';
    } else {
        items.forEach((item, index) => {
            const tr = document.createElement('tr');
            
            let pClass = 'badge-low';
            if (item.priority.toLowerCase().includes('high')) pClass = 'badge-high';
            else if (item.priority.toLowerCase().includes('medium')) pClass = 'badge-medium';

            const criteriaList = item.acceptance_criteria
                ? item.acceptance_criteria.map(c => `• ${escapeHtml(c)}`).join('<br>')
                : 'N/A';

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td><strong>${escapeHtml(item.task_title)}</strong></td>
                <td>${escapeHtml(item.assigned)}</td>
                <td><span class="badge ${pClass}">${escapeHtml(item.priority)}</span></td>
                <td><span class="badge badge-effort">${escapeHtml(item.effort)}</span></td>
                <td>${escapeHtml(item.timeline)}</td>
                <td><small>${criteriaList}</small></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // 3. Architecture & Design Decisions
    const decisionsContent = document.getElementById('decisions-content');
    decisionsContent.innerHTML = '';
    const decisions = data.decisions || [];
    if (decisions.length === 0) {
        decisionsContent.innerHTML = '<p>No decisions identified.</p>';
    } else {
        decisions.forEach((dec, idx) => {
            const div = document.createElement('div');
            div.className = 'item-box';
            div.innerHTML = `
                <h4>Decision ${idx + 1}: ${escapeHtml(dec.decision)}</h4>
                <p><strong>Rationale:</strong> ${escapeHtml(dec.rationale)}</p>
            `;
            decisionsContent.appendChild(div);
        });
    }

    // 4. Risk & Blocker Matrix Table
    const blockersTbody = document.getElementById('blockers-tbody');
    blockersTbody.innerHTML = '';
    const blockers = data.blockers || [];
    if (blockers.length === 0) {
        blockersTbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">No blockers or risks identified.</td></tr>';
    } else {
        blockers.forEach((b, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td><strong>${escapeHtml(b.blocker)}</strong></td>
                <td>${escapeHtml(b.impact)}</td>
            `;
            blockersTbody.appendChild(tr);
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function copyMarkdown() {
    if (!currentMarkdownReport) return;
    navigator.clipboard.writeText(currentMarkdownReport).then(() => {
        showToast("Copied Markdown report to clipboard! Ready to paste into Teams or Notion.");
    }).catch(err => {
        showError("Could not copy text: " + err);
    });
}

function showToast(message) {
    const toast = document.getElementById('toast-container');
    toast.innerText = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function downloadJSON() {
    if (!currentAnalysisData) return;
    const blob = new Blob([JSON.stringify(currentAnalysisData, null, 4)], { type: 'application/json' });
    downloadBlob(blob, 'meeting_analysis.json');
}

function downloadMarkdown() {
    if (!currentMarkdownReport) return;
    const blob = new Blob([currentMarkdownReport], { type: 'text/markdown' });
    downloadBlob(blob, 'meeting_report.md');
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
