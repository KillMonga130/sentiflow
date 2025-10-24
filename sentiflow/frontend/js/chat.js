// SentiFlow Chat Interface JavaScript - Premium Edition

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
let conversationHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkHealth();
    console.log('✅ SentiFlow initialized - Premium Edition');
});

// Setup all event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
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
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    });
    
    // Focus effect
    messageInput.addEventListener('focus', () => {
        messageInput.parentElement.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.3)';
    });
    
    messageInput.addEventListener('blur', () => {
        messageInput.parentElement.style.boxShadow = 'none';
    });
}

// Send message with animations
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }
    
    // Add user message to chat with animation
    addMessage(message, 'user');
    conversationHistory.push({ role: 'user', message });
    
    // Clear input with smooth animation
    messageInput.value = '';
    messageInput.style.height = 'auto';
    messageInput.blur();
    
    // Set processing state
    isProcessing = true;
    sendBtn.disabled = true;
    sendBtn.style.opacity = '0.6';
    loadingIndicator.style.display = 'flex';
    
    // Add ripple effect to send button
    triggerRipple(sendBtn);
    
    try {
        // Call API with timeout
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 30000); // 30s timeout
        
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message }),
            signal: controller.signal
        });
        
        clearTimeout(timeout);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update sentiment indicator with animation
        if (data.sentiment) {
            updateSentimentIndicator(data.sentiment);
            updateBotAvatar(data.sentiment);
        }
        
        // Add assistant response with metadata
        addMessage(
            data.response,
            'assistant',
            data.sentiment,
            data.context
        );
        
        conversationHistory.push({ 
            role: 'assistant', 
            message: data.response,
            sentiment: data.sentiment 
        });
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        let errorMessage = '⚠️ Sorry, I encountered an error. Please try again.';
        if (error.name === 'AbortError') {
            errorMessage = '⏱️ Request timed out. Please try again.';
        }
        
        addMessage(errorMessage, 'assistant');
        
    } finally {
        // Reset processing state with smooth transition
        isProcessing = false;
        sendBtn.disabled = false;
        sendBtn.style.opacity = '1';
        loadingIndicator.style.display = 'none';
        messageInput.focus();
    }
}

// Strip markdown formatting from text
function stripMarkdown(text) {
    // Remove bold (**text** or __text__)
    text = text.replace(/\*\*(.*?)\*\*/g, '$1').replace(/__(.*?)__/g, '$1');
    
    // Remove italic (*text* or _text_)
    text = text.replace(/\*(.*?)\*/g, '$1').replace(/_(.*?)_/g, '$1');
    
    // Remove bullet points and convert to plain text
    text = text.replace(/^\s*[-*+]\s+/gm, '• ');
    
    // Remove code blocks
    text = text.replace(/`(.*?)`/g, '$1');
    
    // Remove headers
    text = text.replace(/^#+\s+/gm, '');
    
    // Remove links but keep text
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, '$1');
    
    // Clean up extra whitespace
    text = text.replace(/\n\n+/g, '\n');
    
    return text;
}

// Add message to chat with premium animations
function addMessage(text, role, sentiment = null, context = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Create avatar with emoji
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.setAttribute('role', 'img');
    avatar.setAttribute('aria-label', role);
    avatar.textContent = role === 'user' ? '👤' : getAvatarEmoji(sentiment?.label);
    
    // Create content container
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Add message text (strip markdown formatting)
    const textP = document.createElement('p');
    textP.textContent = stripMarkdown(text);
    contentDiv.appendChild(textP);
    
    // Add metadata and interactions for assistant messages
    if (role === 'assistant' && (sentiment || context)) {
        // Metadata section
        const metadataDiv = document.createElement('div');
        metadataDiv.className = 'message-metadata';
        
        if (sentiment) {
            const sentimentSpan = document.createElement('span');
            sentimentSpan.innerHTML = `<strong>Sentiment:</strong> ${sentiment.emotion} (Confidence: ${Math.round(sentiment.confidence * 100)}%)`;
            metadataDiv.appendChild(sentimentSpan);
        }
        
        if (context && context.sources && context.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'context-sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong> ';
            
            context.sources.forEach(source => {
                const sourceTag = document.createElement('span');
                sourceTag.className = 'source-tag';
                sourceTag.title = source.title;
                sourceTag.textContent = source.title.length > 30 ? 
                    source.title.substring(0, 27) + '…' : source.title;
                sourcesDiv.appendChild(sourceTag);
            });
            
            metadataDiv.appendChild(sourcesDiv);
        }
        
        contentDiv.appendChild(metadataDiv);
        
        // Reactions bar
        const reactionsDiv = document.createElement('div');
        reactionsDiv.className = 'message-reactions';
        
        const reactions = [
            { emoji: '👍', label: 'Helpful' },
            { emoji: '👎', label: 'Not helpful' },
            { emoji: '🎯', label: 'Accurate' }
        ];
        
        reactions.forEach(({ emoji, label }) => {
            const btn = document.createElement('button');
            btn.className = 'reaction';
            btn.textContent = emoji;
            btn.title = label;
            btn.setAttribute('aria-label', label);
            btn.addEventListener('click', () => handleReaction(btn, emoji, label, text));
            reactionsDiv.appendChild(btn);
        });
        
        contentDiv.appendChild(reactionsDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat with animation
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom smoothly
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// Get avatar emoji based on sentiment
function getAvatarEmoji(label) {
    const avatarEmojis = {
        'positive': '😊',
        'neutral': '🤖',
        'negative': '😔',
        'frustrated': '🆘',
        'urgent': '⚡'
    };
    return avatarEmojis[label] || '🤖';
}

// Update sentiment indicator with smooth transitions
function updateSentimentIndicator(sentiment) {
    if (!sentiment) return;
    
    // Update badge class with animation
    sentimentBadge.style.animation = 'none';
    setTimeout(() => {
        sentimentBadge.className = `sentiment-badge ${sentiment.label}`;
        sentimentBadge.style.animation = '';
    }, 10);
    
    // Update icon
    sentimentIcon.textContent = getAvatarEmoji(sentiment.label);
    sentimentIcon.style.animation = 'pulse 0.5s ease-out';
    
    // Update text
    sentimentText.textContent = sentiment.emotion || sentiment.label;
    
    // Update confidence
    const confidencePercent = Math.round(sentiment.confidence * 100);
    sentimentConfidence.textContent = confidencePercent;
}

// Update all bot avatars based on sentiment
function updateBotAvatar(sentiment) {
    document.querySelectorAll('.message.assistant .message-avatar').forEach(avatar => {
        avatar.textContent = getAvatarEmoji(sentiment?.label);
    });
}

// Handle message reactions
function handleReaction(btn, emoji, label, messageText) {
    btn.classList.add('active');
    
    // Send telemetry
    console.log(`Reaction: ${emoji} (${label}) for message: "${messageText.slice(0, 50)}..."`);
    
    // Visual feedback
    setTimeout(() => btn.classList.remove('active'), 600);
}

// Reset conversation with confirmation
async function resetConversation() {
    if (conversationHistory.length === 0) {
        return;
    }
    
    if (!confirm('🔄 Start a new conversation? Current chat will be cleared.')) {
        return;
    }
    
    try {
        await fetch(`${API_BASE_URL}/api/reset`, {
            method: 'POST'
        });
        
        // Clear messages with fade effect
        chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-avatar" role="img" aria-label="assistant">🤖</div>
                <div class="message-content">
                    <p>Hello! I'm your SentiFlow support assistant. I understand customer emotions and adapt my responses accordingly. I'm here to help with your questions about returns, shipping, warranties, and more. How can I assist you today?</p>
                </div>
            </div>
        `;
        
        // Reset sentiment indicator
        updateSentimentIndicator({
            label: 'neutral',
            emotion: 'Neutral',
            confidence: 0
        });
        
        conversationHistory = [];
        
        console.log('✅ Conversation reset');
        messageInput.focus();
        
    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Failed to reset conversation. Please try again.');
    }
}

// Trigger ripple effect
function triggerRipple(element) {
    element.classList.add('ripple');
    setTimeout(() => element.classList.remove('ripple'), 600);
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
        console.log('✅ API Health:', data);
        return data;
    } catch (error) {
        console.error('⚠️ Health check failed:', error);
        return null;
    }
}

// Add CSS animation for pulse effect
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);
