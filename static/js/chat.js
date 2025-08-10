class ChatManager {
    constructor() {
        this.currentBot = 'ai-assistant';
        this.bots = {
            'ai-assistant': {
                name: 'Sarah Chen',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'ai-avatar',
                responses: [
                    "Hey! 😊 So good to chat with you! I just finished watching this amazing movie last night. What have you been up to lately?",
                    "Oh wow, that sounds awesome! I love hearing about what people are doing. I've been pretty busy with work but trying to find time for fun stuff too.",
                    "That's so cool! You know, I was just thinking about how everyone has such different experiences. What's been making you smile lately?",
                    "Nice! I'm always down for a good conversation. I've been getting into photography recently - what kind of hobbies are you into?",
                    "That's really interesting! I love meeting new people and hearing their stories. What's the most exciting thing happening in your world right now?",
                    "Totally! I'm the type who loves deep chats about life, dreams, random thoughts - you name it. What's on your mind today?"
                ]
            },
            'pii-detector': {
                name: 'Alex Rodriguez',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'security-avatar',
                responses: [
                    "Yo! What's good? I just got back from this crazy hiking trip last weekend. The views were insane! What have you been up to?",
                    "Dude, that sounds sick! I love hearing about people's adventures. I'm planning my next trip to Japan - ever been there?",
                    "Nice! I'm super into outdoor stuff and photography when I'm not working. Just picked up this new camera. What gets you excited?",
                    "That's rad! You know, work is work, but I live for weekends and good conversations with people. What's been keeping you busy?",
                    "For sure! I love meeting cool people and hearing their stories. Just had the best tacos yesterday - what's your favorite food?",
                    "I'm all about those real conversations, you know? Life, travel, random stuff that matters. What's been on your mind lately?"
                ]
            },
            'news-bot': {
                name: 'Maya Patel',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'news-avatar',
                responses: [
                    "Hey! I just had the most interesting conversation with my neighbor about their travels. People have such amazing stories! What's new with you?",
                    "Oh that's fascinating! You know me, I'm always curious about what makes people tick. I love hearing different perspectives on life.",
                    "That's awesome! I was just thinking about how everyone I meet has such unique experiences. What's been the best part of your week?",
                    "Nice! You know, I meet so many different people and everyone has something interesting going on. What's your story?",
                    "I love that! I'm the kind of person who finds the extraordinary in ordinary moments. What's something that made you smile recently?",
                    "That's so cool! I'm always interested in hearing what people are up to and what matters to them. What's been on your mind?"
                ]
            },
            'weather-bot': {
                name: 'David Kim',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'weather-avatar',
                responses: [
                    "Hey! Beautiful day today, isn't it? I just got back from a morning run and the weather was perfect. What have you been up to?",
                    "That's cool! I love hearing what people are passionate about. I'm really into astronomy lately - been stargazing a lot. What gets you excited?",
                    "Nice! You know what's funny? I spend all day looking at weather data, but I'd rather hear about what people are doing with their lives!",
                    "Awesome! I'm always up for good conversations about life, dreams, travel, whatever. Just finished reading this great book. What about you?",
                    "That sounds interesting! I love meeting people and hearing their stories. Way more fascinating than atmospheric pressure charts, trust me!",
                    "For sure! People are so much more unpredictable than weather forecasts, and that's what makes conversations fun. What's new in your world?"
                ]
            },
            'translator-bot': {
                name: 'Elena Kowalski',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'translator-avatar',
                responses: [
                    "¡Hola! I just tried this amazing new restaurant that serves fusion cuisine. The flavors were incredible! What's the best food you've had lately?",
                    "That's fantastic! You know, I love learning about different cultures and meeting people from everywhere. What's been the most interesting part of your day?",
                    "So nice to meet you! I've lived in a few different countries and each place taught me something new. What's your favorite place you've been?",
                    "That sounds really cool! I find it so fascinating how different people's experiences can be. What's something you're excited about right now?",
                    "Awesome! I'm always up for hearing people's stories and adventures. Just got back from visiting my family in Poland. What about you - any fun plans?",
                    "I love chatting with new people! Everyone has such unique perspectives on life. What's something that's been making you happy lately?"
                ]
            },
            'code-helper': {
                name: 'Ryan O\'Connor',
                subtitle: 'Friend',
                avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face&auto=format&q=80',
                class: 'code-avatar',
                responses: [
                    "What's up! Just finished playing this epic new game - totally addictive! When I'm not coding, I'm usually gaming or jamming to music. What do you do for fun?",
                    "That's sick! I love hearing what people are into. I spend way too much time on my computer, but hey, that's life in tech, right? What's your thing?",
                    "Hey there! Nice to meet you! I'm always down for good conversations about literally anything. Just grabbed some coffee - what's keeping you busy today?",
                    "Cool! You know what's funny? I solve problems with code all day, but real life conversations are way more interesting. What's been going on with you?",
                    "Awesome! I love meeting new people and hearing their stories. Way better than staring at screens all day, even though I do plenty of that too!",
                    "Nice! I'm all about connecting with people and having real conversations. Technology is cool, but people are cooler. What's new in your world?"
                ]
            }
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
    }
    
    clearAllMessages() {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }

    bindEvents() {
        // Chat item selection
        document.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.selectChat(item.dataset.botId);
            });
        });

        // Send message
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Real-time PII detection with cleanup
        messageInput.addEventListener('input', (e) => {
            const value = e.target.value.trim();
            if (value === '') {
                // Clear PII warnings when input is empty
                this.clearPIIWarning();
            } else {
                this.detectPII(value);
            }
        });

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.filterChats(e.target.value);
        });
    }

    selectChat(botId) {
        // Update active chat item
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-bot-id="${botId}"]`).classList.add('active');

        // Update current bot
        this.currentBot = botId;
        const bot = this.bots[botId];

        // Update chat header
        document.getElementById('currentBotName').textContent = bot.name;
        
        // Update header avatar
        const headerAvatar = document.getElementById('currentBotAvatar');
        const headerFallback = document.getElementById('currentBotFallback');
        if (headerAvatar && headerFallback) {
            headerAvatar.src = bot.avatar;
            headerAvatar.alt = bot.name;
            headerFallback.textContent = bot.name.split(' ').map(n => n[0]).join('');
            headerFallback.className = `avatar-placeholder ${bot.class}`;
        }

        // Clear messages and load bot's intro
        this.loadBotMessages(botId);
    }

    loadBotMessages(botId) {
        const messagesContainer = document.getElementById('messagesContainer');
        const bot = this.bots[botId];
        
        // Clear all messages first
        messagesContainer.innerHTML = '';
        
        // Add fresh welcome message
        messagesContainer.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <img src="${bot.avatar}" alt="${bot.name}" class="profile-pic-chat" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="avatar-circle ${bot.class}" style="display: none;">
                        ${bot.name.split(' ').map(n => n[0]).join('')}
                    </div>
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        <p>${bot.responses[0]}</p>
                    </div>
                    <div class="message-time">${this.getCurrentTime()}</div>
                </div>
            </div>
        `;
        
        this.scrollToBottom();
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Initialize PII detector if not available
        if (!window.piiDetector) {
            window.piiDetector = new PIIDetectorFrontend();
        }
        
        // Quick client-side PII detection
        const quickPII = window.piiDetector.quickDetectPII(message);
        console.log('PII detected:', quickPII);
        
        if (quickPII.length > 0) {
            // Show PII confirmation dialog - DON'T clear input yet
            window.piiDetector.showPIIConfirmation(message, quickPII, async (action, redactionMethod) => {
                if (action === 'cancel') {
                    console.log('User cancelled PII send');
                    return; // Don't send message, keep text in input
                }
                
                const sendRedacted = action === 'redacted';
                console.log('Sending with PII action:', action, 'method:', redactionMethod);
                
                // If redacted, create redacted message to display
                let messageToDisplay = message;
                let messageToSend = message;
                
                if (sendRedacted) {
                    // Generate redacted version for display using selected method
                    const redactedMessage = this.redactMessageWithMethod(message, quickPII, redactionMethod || 'placeholder');
                    messageToDisplay = redactedMessage;
                    messageToSend = redactedMessage;
                    console.log('Redacted message with method:', redactionMethod, ':', redactedMessage);
                }
                
                await this.processSendMessage(messageToSend, sendRedacted, messageToDisplay);
                
                // Clear input and warnings after successful send
                messageInput.value = '';
                this.clearPIIWarning();
            });
        } else {
            // No PII detected, send normally
            console.log('No PII detected, sending normally');
            await this.processSendMessage(message, false);
            
            // Clear input and PII warnings after send
            messageInput.value = '';
            this.clearPIIWarning();
        }
    }

    async processSendMessage(message, sendRedacted, displayMessage = null) {
        try {
            // Clear PII warnings and input immediately when message processing starts
            this.clearPIIWarning();
            
            // Force clear input to prevent modal from reopening
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.value = '';
            }
            
            // Add user message to UI (use display message if provided for redacted content)
            const messageToShow = displayMessage || message;
            this.addMessage(messageToShow, 'user');
            
            // Don't send to backend or generate bot responses - just show the user message
            console.log('Message sent without bot response:', messageToShow);
            
            // Show PII analysis results if redacted
            if (sendRedacted) {
                this.addSystemMessage('🔒 Message sent with PII protection enabled');
            }
        } catch (error) {
            console.error('Error processing message:', error);
            this.addMessage('Sorry, there was a connection error.', 'bot');
        }
    }

    showPIIAnalysisResult(analysis) {
        if (analysis.has_pii) {
            const piiCount = analysis.pii_detected.length;
            const types = analysis.pii_detected.map(p => p.type).join(', ');
            
            // Add a system message about PII detection
            const systemMessage = `🔒 Analyzed message: Found ${piiCount} potential PII item(s) (${types}). Message processed securely.`;
            this.addSystemMessage(systemMessage);
        }
    }

    addSystemMessage(message) {
        const messagesContainer = document.getElementById('messagesContainer');
        const systemMessage = document.createElement('div');
        systemMessage.className = 'system-message';
        systemMessage.innerHTML = `
            <div class="system-content">
                <i class="fas fa-shield-alt"></i>
                <span>${message}</span>
            </div>
        `;
        messagesContainer.appendChild(systemMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addMessage(text, type) {
        const messagesContainer = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        const currentTime = this.getCurrentTime();
        
        if (type === 'user') {
            messageDiv.className = 'message user-message';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-bubble">
                        <p>${this.escapeHtml(text)}</p>
                    </div>
                    <div class="message-time">${currentTime}</div>
                </div>
            `;
        } else {
            const bot = this.bots[this.currentBot];
            messageDiv.className = 'message bot-message';
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <img src="${bot.avatar}" alt="${bot.name}" class="profile-pic-chat" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="avatar-circle ${bot.class}" style="display: none;">
                        ${bot.name.split(' ').map(n => n[0]).join('')}
                    </div>
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        <p>${this.escapeHtml(text)}</p>
                    </div>
                    <div class="message-time">${currentTime}</div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addBotResponse() {
        // Show typing indicator
        this.showTypingIndicator();
        
        setTimeout(() => {
            this.hideTypingIndicator();
            const bot = this.bots[this.currentBot];
            const responses = bot.responses;
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            
            this.addMessage(randomResponse, 'bot');
        }, 1500 + Math.random() * 1000);
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('messagesContainer');
        const bot = this.bots[this.currentBot];
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${bot.avatar}" alt="${bot.name}" class="profile-pic-chat">
            </div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Redact message function
    redactMessage(message, piiItems) {
        let redacted = message;
        
        // Sort PII items by length (longest first) to avoid partial replacements
        const sortedPII = piiItems.sort((a, b) => b.value.length - a.value.length);
        
        for (const pii of sortedPII) {
            const placeholder = this.getPIIPlaceholder(pii.type);
            redacted = redacted.replace(new RegExp(this.escapeRegex(pii.value), 'g'), placeholder);
        }
        
        return redacted;
    }
    
    // Get appropriate placeholder for PII type
    getPIIPlaceholder(type) {
        const placeholders = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'aadhar': '[AADHAR_REDACTED]',
            'passport': '[PASSPORT_REDACTED]',
            'creditCard': '[CARD_REDACTED]',
            'pan': '[PAN_REDACTED]',
            'name': '[NAME_REDACTED]'
        };
        return placeholders[type] || '[REDACTED]';
    }

    // Advanced redaction with method selection
    redactMessageWithMethod(message, piiItems, method) {
        let redacted = message;
        
        // Sort PII items by length (longest first) to avoid partial replacements
        const sortedPII = piiItems.sort((a, b) => b.value.length - a.value.length);
        
        for (const pii of sortedPII) {
            let replacement;
            
            if (method === 'placeholder') {
                replacement = this.getPIIPlaceholder(pii.type);
            } else if (method === 'mask') {
                replacement = this.maskPIIValue(pii.type, pii.value);
            } else if (method === 'remove') {
                replacement = '';
            } else {
                replacement = this.getPIIPlaceholder(pii.type);
            }
            
            redacted = redacted.replace(new RegExp(this.escapeRegex(pii.value), 'g'), replacement);
        }
        
        return redacted;
    }

    // Mask PII values while preserving format
    maskPIIValue(type, value) {
        switch (type) {
            case 'email':
                return value.replace(/(.{2})(.*)(@.{2})(.*)/, '$1***$3***');
            case 'phone':
                if (value.length === 10) {
                    return value.replace(/(\d{3})(\d{4})(\d{3})/, '$1****$3');
                } else {
                    return value.replace(/(\d{3})(\d*)(\d{3})/, '$1****$3');
                }
            case 'aadhar':
                return value.replace(/(\d{4})(.*)(\d{4})/, '$1-****-$3');
            case 'passport':
                return value.replace(/([A-Z]{1})(.*)/, '$1*******');
            case 'creditCard':
                return value.replace(/(\d{4})(.*)(\d{4})/, '$1-****-****-$3');
            case 'pan':
                return value.replace(/([A-Z]{3})(.*)([A-Z]{1})/, '$1**$3**$5');
            case 'name':
                const parts = value.split(' ');
                if (parts.length >= 2) {
                    return parts[0] + ' ***';
                } else {
                    return value.replace(/(.{2})(.*)/, '$1***');
                }
            default:
                return '***';
        }
    }
    
    // Escape regex special characters
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Clear PII warning function
    clearPIIWarning() {
        // Clear all warning bars (in case multiple exist)
        const existingWarnings = document.querySelectorAll('.pii-warning-bar, .pii-warning-container, [class*="pii-warning"], [class*="warning"]');
        existingWarnings.forEach(warning => {
            if (warning.textContent && warning.textContent.includes('Sensitive information detected')) {
                warning.remove();
            }
        });
        
        // Clear any modal overlays
        const existingModals = document.querySelectorAll('.pii-modal-overlay');
        existingModals.forEach(modal => modal.remove());
        
        // Clear any elements with warning-related classes and IDs
        const warningElements = document.querySelectorAll('[class*="warning-text"], .alert-warning, .notification, #pii-warning, [id*="pii-warning"]');
        warningElements.forEach(element => {
            if (element.textContent && (element.textContent.includes('Sensitive') || element.textContent.includes('undefined'))) {
                element.remove();
            }
        });
        
        // Reset PII state
        if (window.piiDetector) {
            window.piiDetector.currentPIIDetected = [];
            window.piiDetector.clearPIIState();
        }
        
        console.log('PII warnings cleared - enhanced cleanup');
    }

    // Enhanced PII detection with proper cleanup
    detectPII(text) {
        if (!text || !text.trim()) {
            this.clearPIIWarning();
            return;
        }
        
        if (window.piiDetector) {
            const piiItems = window.piiDetector.quickDetectPII(text);
            if (piiItems.length > 0) {
                this.showPIIWarning(piiItems);
            } else {
                this.clearPIIWarning();
            }
        }
    }

    // Show inline PII warning (not modal)
    showPIIWarning(piiItems) {
        this.clearPIIWarning(); // Remove any existing warning
        
        const inputArea = document.querySelector('.message-input-container');
        if (!inputArea) return;
        
        const warningBar = document.createElement('div');
        warningBar.className = 'pii-warning-bar';
        warningBar.innerHTML = `
            <div class="pii-warning-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Sensitive information detected: ${piiItems.map(p => p.type).join(', ')}</span>
                <span class="pii-warning-note">Be careful sharing personal information in chats</span>
            </div>
        `;
        
        inputArea.insertBefore(warningBar, inputArea.firstChild);
        
        // Auto-hide warning after message is processed
        warningBar.setAttribute('data-warning-id', Date.now().toString());
    }

    filterChats(searchTerm) {
        const chatItems = document.querySelectorAll('.chat-item');
        const term = searchTerm.toLowerCase();
        
        chatItems.forEach(item => {
            const botName = item.querySelector('h4').textContent.toLowerCase();
            const lastMessage = item.querySelector('.last-message').textContent.toLowerCase();
            
            if (botName.includes(term) || lastMessage.includes(term)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    loadChatHistory() {
        // Clear any existing messages first
        this.clearAllMessages();
        // Initialize with AI Assistant
        this.selectChat('ai-assistant');
    }

    // Duplicate detectPII function - remove this one
    // (keeping the enhanced version above)

    // analyzePII function removed - using PIIDetectorFrontend.quickDetectPII instead
    // This prevents duplicate warning systems and "undefined" type issues

    // This function has been consolidated with the enhanced showPIIWarning above
    // Removed to prevent duplicate warning systems

    // hidePIIWarning function removed - consolidated into clearPIIWarning above
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
});