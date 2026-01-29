/* JS Module: Chatbot - Handles n8n Chat integration for Harvest Sync */

/**
 * Harvest Sync Chatbot Configuration
 * Integrates n8n Chat widget with farmer ID, file uploads, voice recording,
 * and bilingual support (English + Malayalam)
 */

// i18n translations
const translations = {
    en: {
        title: 'Krishi AI Assistant 🌾',
        subtitle: "Your personal farming advisor. I'm here to help 24/7.",
        footer: '',
        getStarted: 'Start Chat',
        inputPlaceholder: 'Ask about crops, weather, diseases...',
        welcomeTitle: 'Hello, Farmer! 👋',
        welcomeSubtitle: 'I am your AI Agronomist. Ask me about crop diseases, weather alerts, best practices, and more.',
        voiceStart: 'Recording...',
        voiceStop: 'Tap to send',
        uploadImage: 'Upload crop image',
        uploadReport: 'Attach report'
    },
    ml: {
        title: 'കൃഷി AI സഹായി 🌾',
        subtitle: 'നിങ്ങളുടെ വ്യക്തിഗത കൃഷി ഉപദേശകൻ. ഞാൻ 24/7 സഹായിക്കാൻ ഇവിടെയുണ്ട്.',
        footer: '',
        getStarted: 'ചാറ്റ് ആരംഭിക്കുക',
        inputPlaceholder: 'വിളകൾ, കാലാവസ്ഥ, രോഗങ്ങൾ എന്നിവയെ കുറിച്ച് ചോദിക്കൂ...',
        welcomeTitle: 'ഹലോ, കർഷകരേ! 👋',
        welcomeSubtitle: 'ഞാൻ നിങ്ങളുടെ AI അഗ്രോണമിസ്റ്റ് ആണ്. വിള രോഗങ്ങൾ, കാലാവസ്ഥ അലേർട്ടുകൾ, മികച്ച രീതികൾ എന്നിവയെ കുറിച്ച് എന്നോട് ചോദിക്കൂ.',
        voiceStart: 'റെക്കോർഡിംഗ്...',
        voiceStop: 'അയയ്ക്കാൻ ടാപ്പ് ചെയ്യുക',
        uploadImage: 'വിള ചിത്രം അപ്‌ലോഡ് ചെയ്യുക',
        uploadReport: 'റിപ്പോർട്ട് അറ്റാച്ച് ചെയ്യുക'
    }
};

// Current language state
let currentLang = 'en';

/**
 * Voice Recorder Class
 * Handles voice message recording using MediaRecorder API
 */
class VoiceRecorder {
    constructor(onRecordingComplete) {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.onRecordingComplete = onRecordingComplete;
    }

    async start() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.onRecordingComplete(audioBlob);

                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            return true;
        } catch (error) {
            console.error('Voice recording error:', error);
            return false;
        }
    }

    stop() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
        }
    }
}

/**
 * Initialize the n8n Chatbot
 * @param {Object} config - Configuration object
 * @param {string} config.webhookUrl - n8n webhook URL
 * @param {string|number} config.farmerId - Farmer's unique ID from database
 * @param {string} config.farmerName - Farmer's name for personalization
 * @param {string} config.farmerLocation - Farmer's location
 */
export async function initChatbot(config) {
    const {
        webhookUrl,
        farmerId,
        farmerName = 'Farmer',
        farmerLocation = ''
    } = config;

    // Load n8n Chat CSS
    const chatStyles = document.createElement('link');
    chatStyles.rel = 'stylesheet';
    chatStyles.href = 'https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css';
    document.head.appendChild(chatStyles);

    // Wait for styles to load
    await new Promise(resolve => setTimeout(resolve, 100));

    // Dynamically import n8n chat
    const { createChat } = await import('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js');

    // Initialize n8n Chat with custom configuration
    const chat = createChat({
        webhookUrl: webhookUrl,
        webhookConfig: {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            }
        },
        target: '#n8n-chat',
        mode: 'window',
        chatInputKey: 'chatInput',
        chatSessionKey: 'sessionId',
        loadPreviousSession: false,

        // Farmer metadata sent with every message
        metadata: {
            farmerId: farmerId,
            farmerName: farmerName,
            farmerLocation: farmerLocation,
            role: 'farmer',
            platform: 'harvest_sync',
            language: currentLang
        },

        showWelcomeScreen: false,
        defaultLanguage: currentLang,

        // Initial greeting messages
        initialMessages: currentLang === 'en'
            ? [
                `Hello ${farmerName}! 🌾`,
                "I'm your AI Agronomist. How can I help you today?",
                "You can ask about crop diseases, weather, market prices, or upload a photo for analysis."
            ]
            : [
                `ഹലോ ${farmerName}! 🌾`,
                "ഞാൻ നിങ്ങളുടെ AI അഗ്രോണമിസ്റ്റ് ആണ്. ഇന്ന് ഞാൻ എങ്ങനെ സഹായിക്കും?",
                "വിള രോഗങ്ങൾ, കാലാവസ്ഥ, വിപണി വിലകൾ എന്നിവയെ കുറിച്ച് ചോദിക്കാം അല്ലെങ്കിൽ വിശകലനത്തിനായി ഒരു ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യാം."
            ],

        // i18n configuration
        i18n: {
            en: translations.en,
            ml: translations.ml
        },

        // Enable file uploads
        allowFileUploads: true,
        allowedFilesMimeTypes: 'image/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,audio/*',

        // Disable streaming to avoid response errors
        enableStreaming: false
    });

    // Add custom UI elements after chat is initialized
    setTimeout(() => {
        addLanguageToggle();
        addVoiceRecordButton(webhookUrl, farmerId, farmerName, farmerLocation);
        addCustomStyling();
    }, 500);

    return chat;
}

/**
 * Add language toggle button to chat header
 */
function addLanguageToggle() {
    const chatHeader = document.querySelector('.n8n-chat .chat-header, .n8n-chat [class*="Header"]');
    if (!chatHeader) return;

    // Check if toggle already exists
    if (document.querySelector('.chat-lang-toggle')) return;

    const langToggle = document.createElement('div');
    langToggle.className = 'chat-lang-toggle';
    langToggle.innerHTML = `
        <button class="${currentLang === 'en' ? 'active' : ''}" data-lang="en">EN</button>
        <button class="${currentLang === 'ml' ? 'active' : ''}" data-lang="ml">മല</button>
    `;

    langToggle.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            const newLang = btn.dataset.lang;
            if (newLang !== currentLang) {
                currentLang = newLang;
                updateLanguage(newLang);
                langToggle.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            }
        });
    });

    chatHeader.style.position = 'relative';
    chatHeader.appendChild(langToggle);
}

/**
 * Update UI language
 */
function updateLanguage(lang) {
    const t = translations[lang];

    // Update placeholder
    const input = document.querySelector('.n8n-chat textarea, .n8n-chat .chat-input');
    if (input) {
        input.placeholder = t.inputPlaceholder;
    }

    // Store language preference
    localStorage.setItem('harvest_chat_lang', lang);
}

/**
 * Add voice recording button to input area
 */
function addVoiceRecordButton(webhookUrl, farmerId, farmerName, farmerLocation) {
    const inputContainer = document.querySelector('.n8n-chat .chat-input-container, .n8n-chat .chat-footer, .n8n-chat [class*="Input"]');
    if (!inputContainer) return;

    // Check if voice button already exists
    if (document.querySelector('.voice-record-btn')) return;

    const voiceBtn = document.createElement('button');
    voiceBtn.className = 'voice-record-btn';
    voiceBtn.type = 'button';
    voiceBtn.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    `;
    voiceBtn.title = translations[currentLang].uploadImage;

    // Voice recorder instance
    const recorder = new VoiceRecorder(async (audioBlob) => {
        // Convert blob to base64
        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];

            // Send voice message to webhook
            try {
                const response = await fetch(webhookUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ngrok-skip-browser-warning': 'true'
                    },
                    body: JSON.stringify({
                        action: 'sendMessage',
                        chatInput: '[Voice Message]',
                        sessionId: getSessionId(),
                        voiceMessage: base64Audio,
                        mimeType: 'audio/webm',
                        farmerId: farmerId,
                        farmerName: farmerName,
                        farmerLocation: farmerLocation,
                        role: 'farmer',
                        language: currentLang
                    })
                });

                if (response.ok) {
                    console.log('Voice message sent successfully');
                }
            } catch (error) {
                console.error('Failed to send voice message:', error);
            }
        };
        reader.readAsDataURL(audioBlob);
    });

    // Toggle recording on click
    voiceBtn.addEventListener('click', async () => {
        if (recorder.isRecording) {
            recorder.stop();
            voiceBtn.classList.remove('recording');
        } else {
            const started = await recorder.start();
            if (started) {
                voiceBtn.classList.add('recording');
            } else {
                alert(currentLang === 'en'
                    ? 'Could not access microphone. Please allow microphone permission.'
                    : 'മൈക്രോഫോൺ ആക്സസ് ചെയ്യാനായില്ല. ദയവായി മൈക്രോഫോൺ അനുമതി നൽകുക.');
            }
        }
    });

    // Insert before send button
    const sendBtn = inputContainer.querySelector('button[type="submit"], .chat-send-button');
    if (sendBtn) {
        sendBtn.parentNode.insertBefore(voiceBtn, sendBtn);
    } else {
        inputContainer.appendChild(voiceBtn);
    }
}

/**
 * Get or create session ID
 */
function getSessionId() {
    let sessionId = localStorage.getItem('harvest_chat_session');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('harvest_chat_session', sessionId);
    }
    return sessionId;
}

/**
 * Add custom styling enhancements
 */
function addCustomStyling() {
    // Ensure our custom styles take precedence
    const style = document.createElement('style');
    style.textContent = `
        .n8n-chat .chat-window,
        .n8n-chat [class*="Window"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Change chatbot language
 * @param {string} lang - 'en' or 'ml'
 */
export function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        updateLanguage(lang);
    }
}

/**
 * Get current language
 */
export function getLanguage() {
    return currentLang;
}
