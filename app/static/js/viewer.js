// PDF.js Viewer with Analytics Tracking

let pdfDoc = null;
let pageNum = 1;
let pageRendering = false;
let pageNumPending = null;
let scale = 1.5;
let canvas = null;
let ctx = null;

// Analytics tracking
let viewerData = null;
let sessionId = null;
let linkCode = null;
let csrfToken = null;
let startTime = null;
let pageStartTime = null;
let pagesViewed = new Set();
let currentPage = 1;
let totalPages = 0;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize viewer
    canvas = document.getElementById('pdfCanvas');
    ctx = canvas.getContext('2d');

    // Get viewer data
    const dataEl = document.getElementById('viewerData');
    if (dataEl) {
        linkCode = dataEl.dataset.linkCode;
        sessionId = dataEl.dataset.sessionId;

        // Check if sessionId is valid (not 'None' string or empty)
        if (!sessionId || sessionId === 'None' || sessionId === 'null') {
            sessionId = null;
        }

        totalPages = parseInt(dataEl.dataset.pageCount) || 0;
        csrfToken = dataEl.dataset.csrfToken;

        startTime = Date.now();
        pageStartTime = Date.now();
    }

    // Load PDF
    const url = `/v/${linkCode}/document.pdf`;

    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    const loadingTask = pdfjsLib.getDocument(url);
    loadingTask.promise.then(function(pdf) {
        pdfDoc = pdf;
        totalPages = pdf.numPages;

        // Render first page
        renderPage(pageNum);

        // Track first page view
        trackPageView(pageNum);

        // Start heartbeat for analytics
        startAnalyticsHeartbeat();
    }, function(reason) {
        console.error('Error loading PDF:', reason);
    });

    // Button event listeners
    document.getElementById('prevPage').addEventListener('click', onPrevPage);
    document.getElementById('nextPage').addEventListener('click', onNextPage);

    // Track page visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Send final analytics on page unload
    window.addEventListener('beforeunload', function() {
        sendAnalyticsUpdate(true);
    });
});

function renderPage(num) {
    pageRendering = true;

    pdfDoc.getPage(num).then(function(page) {
        const viewport = page.getViewport({scale: scale});
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };

        const renderTask = page.render(renderContext);

        renderTask.promise.then(function() {
            pageRendering = false;
            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }

            // Update page info
            document.getElementById('pageInfo').textContent = `Page ${num} of ${totalPages}`;

            // Update button states
            document.getElementById('prevPage').disabled = (num <= 1);
            document.getElementById('nextPage').disabled = (num >= totalPages);
        });
    });
}

function queueRenderPage(num) {
    if (pageRendering) {
        pageNumPending = num;
    } else {
        renderPage(num);
    }
}

function onPrevPage() {
    if (pageNum <= 1) {
        return;
    }
    pageNum--;
    currentPage = pageNum;
    queueRenderPage(pageNum);
    trackPageView(pageNum);
}

function onNextPage() {
    if (pageNum >= totalPages) {
        return;
    }
    pageNum++;
    currentPage = pageNum;
    queueRenderPage(pageNum);
    trackPageView(pageNum);
}

function trackPageView(page) {
    pagesViewed.add(page);
    pageStartTime = Date.now();
}

function startAnalyticsHeartbeat() {
    // Send update every 5 seconds
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            sendAnalyticsUpdate(false);
        }
    }, 5000);
}

function sendAnalyticsUpdate(isFinal) {
    // Only send analytics if we have a valid session ID
    if (!sessionId || sessionId === 'None' || sessionId === 'null') {
        console.warn('No valid session ID for analytics tracking');
        return;
    }

    const duration = Math.floor((Date.now() - startTime) / 1000);

    const data = {
        session_id: sessionId,
        current_page: currentPage,
        pages_viewed: Array.from(pagesViewed),
        duration_seconds: duration,
        is_final: isFinal
    };

    // Use sendBeacon for final update (more reliable on page unload)
    if (isFinal && navigator.sendBeacon) {
        const formData = new FormData();
        formData.append('csrf_token', csrfToken);
        formData.append('data', JSON.stringify(data));
        navigator.sendBeacon(`/api/track/view`, formData);
    } else {
        // Use fetch for regular updates
        fetch('/api/track/view', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        }).catch(err => console.error('Analytics error:', err));
    }
}

function handleVisibilityChange() {
    if (document.visibilityState === 'hidden') {
        // Page is hidden, send update
        sendAnalyticsUpdate(false);
    } else {
        // Page is visible again, reset start time
        pageStartTime = Date.now();
    }
}
