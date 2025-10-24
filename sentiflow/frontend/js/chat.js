// SentiFlow Chat Interface JavaScript

const API_BASE_URL = window.location.origin;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const sentimentBadge = document.getElementById('sentimentBadge');
const sentimentIcon = document.getElementById('sentimentIcon');
const sentimentText = document.getElementById('sentimentText');
const sentimentConfidence = document.getElementById('sentimentConfidence');

// State
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    // Microinteraction: ripple + checkmark on send
    sendBtn.addEventListener('click', function () {
        this.classList.add('ripple');
        setTimeout(() => this.classList.remove('ripple'), 600);
        const icon = document.createElement('span');
        icon.textContent = '✓';
        icon.className = 'send-success';
        this.appendChild(icon);
        setTimeout(() => icon.remove(), 1000);
    });
    resetBtn.addEventListener('click', resetConversation);
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    console.log('✅ SentiFlow initialized');
});

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Set processing state
    isProcessing = true;
    sendBtn.disabled = true;
    loadingIndicator.style.display = 'flex';
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update sentiment indicator
        updateSentimentIndicator(data.sentiment);
        
        // Add assistant response
        addMessage(
            data.response,
            'assistant',
            data.sentiment,
            data.context
        );
        // Update bot avatar based on sentiment
        updateBotAvatar(data.sentiment);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage(
            '⚠️ Sorry, I encountered an error. Please try again.',
            'assistant'
        );
    } finally {
        // Reset processing state
        isProcessing = false;
        sendBtn.disabled = false;
        loadingIndicator.style.display = 'none';
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(text, role, sentiment = null, context = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    contentDiv.appendChild(textP);
    
    // Add metadata for assistant messages
    if (role === 'assistant' && (sentiment || context)) {
        const metadataDiv = document.createElement('div');
        metadataDiv.className = 'message-metadata';
        
        if (sentiment) {
            const sentimentSpan = document.createElement('span');
            sentimentSpan.textContent = `Sentiment: ${sentiment.emotion} (${sentiment.label})`;
            metadataDiv.appendChild(sentimentSpan);
        }
        
        if (context && context.sources && context.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'context-sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong> ';
            
            context.sources.forEach(source => {
                const sourceTag = document.createElement('span');
                sourceTag.className = 'source-tag';
                sourceTag.textContent = source.title;
                sourcesDiv.appendChild(sourceTag);
            });
            
            metadataDiv.appendChild(sourcesDiv);
        }
        
        // Add reactions bar
        const reactionsDiv = document.createElement('div');
        reactionsDiv.className = 'message-reactions';
        ['👍','👎','🎯'].forEach(emoji => {
            const btn = document.createElement('button');
            btn.className = 'reaction';
            btn.dataset.emoji = emoji;
            btn.textContent = emoji;
            btn.title = `React ${emoji}`;
            btn.addEventListener('click', () => {
                console.log('Reaction:', emoji, 'for message:', text.slice(0, 40));
                btn.classList.add('active');
                setTimeout(() => btn.classList.remove('active'), 600);
            });
            reactionsDiv.appendChild(btn);
        });
        contentDiv.appendChild(reactionsDiv);

        contentDiv.appendChild(metadataDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update sentiment indicator
function updateSentimentIndicator(sentiment) {
    if (!sentiment) return;
    
    // Update badge class
    sentimentBadge.className = `sentiment-badge ${sentiment.label}`;
    
    // Update icon
    const icons = {
        positive: '😊',
        neutral: '😐',
        negative: '😟',
        frustrated: '😠',
        urgent: '⚡'
    };
    sentimentIcon.textContent = icons[sentiment.label] || '😐';
    
    // Update text
    sentimentText.textContent = sentiment.emotion || sentiment.label;
    
    // Update confidence
    const confidencePercent = Math.round(sentiment.confidence * 100);
    sentimentConfidence.textContent = confidencePercent;
}

// Update bot avatar based on sentiment
function updateBotAvatar(sentiment) {
    const avatarEmojis = {
        'positive': '😊',
        'neutral': '🤖',
        'negative': '😔',
        'frustrated': '🆘',
        'urgent': '⚡'
    };
    const emoji = avatarEmojis[sentiment?.label] || '🤖';
    document.querySelectorAll('.message.assistant .message-avatar').forEach(avatar => {
        avatar.textContent = emoji;
    });
}

// Reset conversation
async function resetConversation() {
    if (!confirm('Are you sure you want to reset the conversation?')) {
        return;
    }
    
    try {
        await fetch(`${API_BASE_URL}/api/reset`, {
            method: 'POST'
        });
        
        // Clear messages (keep welcome message)
        chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p>Hello! I'm your SentiFlow support assistant. I'm here to help with your questions about returns, shipping, warranties, and more. How can I assist you today?</p>
                </div>
            </div>
        `;
        
        // Reset sentiment indicator
        updateSentimentIndicator({
            label: 'neutral',
            emotion: 'Neutral',
            confidence: 0
        });
        
        console.log('✅ Conversation reset');
        
    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Failed to reset conversation. Please try again.');
    }
}

// Format timestamp
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Check API health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('API Health:', data);
        return data;
    } catch (error) {
        console.error('Health check failed:', error);
        return null;
    }
}

// Run health check on load
checkHealth();
