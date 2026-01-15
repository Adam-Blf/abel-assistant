// A.B.E.L - J.A.R.V.I.S. Interface
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const { getCurrentWindow } = window.__TAURI__.window;
const { openUrl } = window.__TAURI__.opener;

// === STATE ===
let isRunning = false;
let isStarting = false;

// === ELEMENTS ===
const statusDot = document.getElementById('statusDot');
const statusLabel = document.getElementById('statusLabel');
const progressContainer = document.getElementById('progressContainer');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const logContainer = document.getElementById('logContainer');
const dataStream = document.getElementById('dataStream');
const datetimeEl = document.getElementById('datetime');

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', async () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);

    startDataStream();

    // Listen for events from Rust
    await listen('status', (event) => {
        updateStatus(event.payload.running, event.payload.starting);
    });

    await listen('log', (event) => {
        addLog(event.payload.message, event.payload.level, event.payload.timestamp);
    });

    // Check initial status
    try {
        const running = await invoke('check_status');
        updateStatus(running, false);
        if (running) {
            addLog('DOCKER SERVICES DETECTED - SYSTEM OPERATIONAL', 'success');
        } else {
            addLog('SYSTEM READY FOR INITIALIZATION', 'info');
        }
    } catch (e) {
        addLog('STATUS CHECK FAILED', 'warning');
    }
});

// === DATETIME ===
function updateDateTime() {
    const now = new Date();
    const date = now.toISOString().split('T')[0].replace(/-/g, '.');
    const time = now.toTimeString().split(' ')[0];
    datetimeEl.textContent = `${date} // ${time}`;
}

// === DATA STREAM ===
function startDataStream() {
    setInterval(() => {
        const lat = (Math.random() * 180 - 90).toFixed(4);
        const lon = (Math.random() * 360 - 180).toFixed(4);
        const seq = `V.${String(Math.floor(Math.random() * 100)).padStart(2, '0')}.${String(Math.floor(Math.random() * 100)).padStart(2, '0')}`;
        const hex = `0x${Math.floor(Math.random() * 65535).toString(16).toUpperCase().padStart(4, '0')}`;
        dataStream.textContent = `${lat}N ${lon}E  //  ${seq}  //  ${hex}  //  FREQ:${(Math.random() * 1000).toFixed(2)}MHz`;
    }, 100);
}

// === STATUS ===
function updateStatus(running, starting) {
    isRunning = running;
    isStarting = starting;

    statusDot.className = 'status-dot';
    statusLabel.className = 'status-label';

    if (starting) {
        statusDot.classList.add('starting');
        statusLabel.classList.add('starting');
        statusLabel.textContent = 'INITIALIZING...';
        progressContainer.classList.add('visible');
        startBtn.disabled = true;
        stopBtn.disabled = true;
    } else if (running) {
        statusDot.classList.add('running');
        statusLabel.classList.add('running');
        statusLabel.textContent = 'SYSTEM ONLINE';
        progressContainer.classList.remove('visible');
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusLabel.textContent = 'SYSTEM OFFLINE';
        progressContainer.classList.remove('visible');
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// === LOGGING ===
function addLog(message, level = 'info', timestamp = null) {
    if (!timestamp) {
        const now = new Date();
        timestamp = `${now.toTimeString().split(' ')[0]}.${String(now.getMilliseconds()).padStart(3, '0')}`;
    }

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">[${timestamp}]</span>
        <span class="log-msg ${level}">${message}</span>
    `;

    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;

    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

// === COMMANDS ===
async function startServices() {
    try {
        await invoke('start_services');
    } catch (e) {
        addLog(`ERROR: ${e}`, 'error');
        updateStatus(false, false);
    }
}

async function stopServices() {
    try {
        await invoke('stop_services');
    } catch (e) {
        addLog(`ERROR: ${e}`, 'error');
    }
}

// === WINDOW CONTROLS ===
async function minimizeWindow() {
    const win = getCurrentWindow();
    await win.minimize();
}

async function closeWindow() {
    const win = getCurrentWindow();
    await win.close();
}

// === LINKS ===
async function openLink(url) {
    try {
        await openUrl(url);
    } catch (e) {
        // Fallback
        window.open(url, '_blank');
    }
}

// === KEYBOARD SHORTCUTS ===
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeWindow();
    }
    if (e.ctrlKey && e.key === 'Enter') {
        if (!isRunning && !isStarting) {
            startServices();
        }
    }
});

// === HOVER SOUND EFFECT (Optional) ===
document.querySelectorAll('.btn, .link-card').forEach(el => {
    el.addEventListener('mouseenter', () => {
        // Could add hover sound here
    });
});
