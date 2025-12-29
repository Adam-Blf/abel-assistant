/**
 * A.B.E.L - Frontend Application
 * ==============================
 * J.A.R.V.I.S. style interface for A.B.E.L backend
 */

// ============================================
// Configuration
// ============================================

const CONFIG = {
    apiUrl: 'http://127.0.0.1:8080',
    wsUrl: 'ws://127.0.0.1:8080',
    checkInterval: 5000,
    maxMessages: 100,
};

// ============================================
// State
// ============================================

const STATE = {
    isConnected: false,
    isRecording: false,
    messageCount: 0,
    tokenCount: 0,
    startTime: Date.now(),
    mediaRecorder: null,
    audioChunks: [],
};

// ============================================
// DOM Elements
// ============================================

const elements = {
    loadingOverlay: document.getElementById('loading-overlay'),
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    voiceBtn: document.getElementById('voice-btn'),
    sendBtn: document.getElementById('send-btn'),
    timeDisplay: document.getElementById('time-display'),
    statusBackend: document.getElementById('status-backend'),
    statusOllama: document.getElementById('status-ollama'),
    statusDb: document.getElementById('status-db'),
    infoLatency: document.getElementById('info-latency'),
    infoUptime: document.getElementById('info-uptime'),
    statMessages: document.getElementById('stat-messages'),
    statTokens: document.getElementById('stat-tokens'),
    audioVisualizer: document.getElementById('audio-visualizer'),
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Start time updates
    updateTime();
    setInterval(updateTime, 1000);
    setInterval(updateUptime, 1000);

    // Check backend status
    await checkStatus();
    setInterval(checkStatus, CONFIG.checkInterval);

    // Setup event listeners
    setupEventListeners();

    // Hide loading after animation
    setTimeout(() => {
        elements.loadingOverlay.classList.add('hidden');
    }, 2500);
});

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Enter key to send
    elements.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Focus input on any key
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName !== 'INPUT' && !e.ctrlKey && !e.altKey && !e.metaKey) {
            if (e.key.length === 1) {
                elements.chatInput.focus();
            }
        }
    });
}

// ============================================
// Time & Status Updates
// ============================================

function updateTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    elements.timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
}

function updateUptime() {
    const elapsed = Date.now() - STATE.startTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    elements.infoUptime.textContent =
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

async function checkStatus() {
    const startTime = Date.now();

    try {
        const response = await fetch(`${CONFIG.apiUrl}/health`, {
            method: 'GET',
            timeout: 3000,
        });

        const latency = Date.now() - startTime;
        elements.infoLatency.textContent = `${latency}ms`;

        if (response.ok) {
            const data = await response.json();
            STATE.isConnected = true;

            elements.statusBackend.classList.add('online');
            elements.statusDb.classList.add('online');

            // Check Ollama separately
            checkOllama();
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        STATE.isConnected = false;
        elements.statusBackend.classList.remove('online');
        elements.statusDb.classList.remove('online');
        elements.statusOllama.classList.remove('online');
        elements.infoLatency.textContent = '--ms';
    }
}

async function checkOllama() {
    try {
        const response = await fetch('http://localhost:11434/api/tags', {
            method: 'GET',
            timeout: 2000,
        });

        if (response.ok) {
            elements.statusOllama.classList.add('online');
        } else {
            elements.statusOllama.classList.remove('online');
        }
    } catch {
        elements.statusOllama.classList.remove('online');
    }
}

// ============================================
// Chat Functions
// ============================================

async function sendMessage() {
    const message = elements.chatInput.value.trim();
    if (!message) return;

    // Clear input
    elements.chatInput.value = '';

    // Add user message
    addMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: null,
            }),
        });

        // Remove typing indicator
        hideTypingIndicator();

        if (response.ok) {
            const data = await response.json();
            addMessage('assistant', data.response || data.message || 'No response');

            // Update stats
            STATE.tokenCount += (data.tokens_used || 0);
            elements.statTokens.textContent = STATE.tokenCount;
        } else {
            addMessage('system', 'Error: Failed to get response from A.B.E.L');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('system', `Connection error: ${error.message}`);
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const senderLabel = role === 'user' ? 'YOU' : role === 'assistant' ? 'A.B.E.L' : 'SYSTEM';

    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-sender">${senderLabel}</span>
            <p>${formatMessage(content)}</p>
        </div>
    `;

    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    // Update message count
    STATE.messageCount++;
    elements.statMessages.textContent = STATE.messageCount;

    // Limit messages
    while (elements.chatMessages.children.length > CONFIG.maxMessages) {
        elements.chatMessages.removeChild(elements.chatMessages.firstChild);
    }
}

function formatMessage(content) {
    // Basic markdown-like formatting
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message assistant typing';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="message-content">
            <span class="message-sender">A.B.E.L</span>
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    elements.chatMessages.appendChild(indicator);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function clearChat() {
    elements.chatMessages.innerHTML = `
        <div class="message system">
            <div class="message-content">
                <span class="message-sender">SYSTEM</span>
                <p>Chat cleared. Ready for new conversation.</p>
            </div>
        </div>
    `;
    STATE.messageCount = 0;
    elements.statMessages.textContent = '0';
}

// ============================================
// Voice Functions
// ============================================

async function toggleVoice() {
    if (STATE.isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        STATE.mediaRecorder = new MediaRecorder(stream);
        STATE.audioChunks = [];

        STATE.mediaRecorder.ondataavailable = (event) => {
            STATE.audioChunks.push(event.data);
        };

        STATE.mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(STATE.audioChunks, { type: 'audio/webm' });
            await sendAudioToBackend(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        STATE.mediaRecorder.start();
        STATE.isRecording = true;
        elements.voiceBtn.classList.add('active');
        elements.audioVisualizer.classList.add('active');

    } catch (error) {
        console.error('Microphone access denied:', error);
        addMessage('system', 'Microphone access denied. Please allow microphone access.');
    }
}

function stopRecording() {
    if (STATE.mediaRecorder && STATE.isRecording) {
        STATE.mediaRecorder.stop();
        STATE.isRecording = false;
        elements.voiceBtn.classList.remove('active');
        elements.audioVisualizer.classList.remove('active');
    }
}

async function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    showTypingIndicator();

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/voice/listen`, {
            method: 'POST',
            body: formData,
        });

        hideTypingIndicator();

        if (response.ok) {
            const data = await response.json();
            if (data.text) {
                addMessage('user', data.text);
                // Automatically send to chat
                elements.chatInput.value = data.text;
                await sendMessage();
            }
        } else {
            addMessage('system', 'Voice recognition failed');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('system', `Voice error: ${error.message}`);
    }
}

// ============================================
// Quick Actions
// ============================================

async function quickAction(service) {
    let message = '';

    switch (service) {
        case 'weather':
            message = "Quel temps fait-il aujourd'hui ?";
            break;
        case 'crypto':
            message = "Donne-moi le prix du Bitcoin et Ethereum";
            break;
        case 'news':
            message = "Quelles sont les dernières actualités tech ?";
            break;
        case 'music':
            message = "Recommande-moi de la musique";
            break;
        case 'movies':
            message = "Quels sont les films populaires en ce moment ?";
            break;
        case 'translate':
            message = "Comment dit-on 'bonjour' en japonais ?";
            break;
        default:
            return;
    }

    elements.chatInput.value = message;
    await sendMessage();
}

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (e) => {
    // Ctrl+K: Clear chat
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        clearChat();
    }

    // Ctrl+M: Toggle voice
    if (e.ctrlKey && e.key === 'm') {
        e.preventDefault();
        toggleVoice();
    }

    // Escape: Stop recording
    if (e.key === 'Escape' && STATE.isRecording) {
        stopRecording();
    }
});

// ============================================
// Console Welcome
// ============================================

console.log(`
%c╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     █████╗    ██████╗   ███████╗  ██╗                    ║
║    ██╔══██╗   ██╔══██╗  ██╔════╝  ██║                    ║
║    ███████║   ██████╔╝  █████╗    ██║                    ║
║    ██╔══██║   ██╔══██╗  ██╔══╝    ██║                    ║
║    ██║  ██║ █ ██████╔╝ █ ███████╗ ███████╗               ║
║    ╚═╝  ╚═╝   ╚═════╝    ╚══════╝  ╚══════╝               ║
║                                                           ║
║    Autonomous Backend Entity for Living                   ║
║    Interface v2.0.0 - Open Source                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`, 'color: #00f3ff; font-family: monospace;');

console.log('%cKeyboard Shortcuts:', 'color: #ff6b35; font-weight: bold;');
console.log('%c  Ctrl+K: Clear chat', 'color: #8892a0;');
console.log('%c  Ctrl+M: Toggle voice', 'color: #8892a0;');
console.log('%c  Escape: Stop recording', 'color: #8892a0;');
