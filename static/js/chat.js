class ChatManager {
    constructor() {
        this.currentBot = 'ai-assistant';
        this.bots = {
            'ai-assistant': {
                name: 'Sarah Chen',
                subtitle: 'Friend',
                avatar: '/static/images/sarah-chen.png',
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
                avatar: '/static/images/alex-rodriguez.png',
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
                avatar: '/static/images/maya-patel.png',
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
                avatar: '/static/images/david-kim.png',
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
                avatar: '/static/images/elena-kowalski.png',
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
                avatar: '/static/images/ryan-oconnor.png',
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
        const contactAvatarImg = document.querySelector('.contact-avatar .profile-pic-large');
        if (contactAvatarImg) {
            contactAvatarImg.src = bot.avatar;
            contactAvatarImg.alt = bot.name;
        }

        // Clear messages and load bot's intro
        this.loadBotMessages(botId);
    }

    loadBotMessages(botId) {
        const messagesContainer = document.getElementById('messagesContainer');
        const bot = this.bots[botId];
        
        messagesContainer.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <div class="avatar-circle ${bot.class}">
                        ${bot.avatar}
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
        
        // Quick client-side PII detection
        const quickPII = window.piiDetector.quickDetectPII(message);
        
        if (quickPII.length > 0) {
            // Show PII confirmation dialog
            window.piiDetector.showPIIConfirmation(message, quickPII, async (action) => {
                if (action === 'cancel') {
                    return; // Don't send message
                }
                
                const sendRedacted = action === 'redacted';
                await this.processSendMessage(message, sendRedacted);
            });
        } else {
            // No PII detected, send normally
            await this.processSendMessage(message, false);
        }
        
        // Clear input and PII warnings
        messageInput.value = '';
        this.clearPIIWarning();
    }

    async processSendMessage(message, sendRedacted) {
        try {
            // Add user message to UI immediately
            this.addMessage(message, 'user');
            
            // Send to backend for comprehensive PII analysis and bot response
            const result = await window.piiDetector.sendMessageWithPIIAnalysis(message, sendRedacted);
            
            if (result.success) {
                // Add bot response
                this.addMessage(result.bot_response, 'bot');
                
                // Show PII analysis results if any
                if (result.pii_analysis && result.pii_analysis.has_pii) {
                    this.showPIIAnalysisResult(result.pii_analysis);
                }
            } else {
                this.addMessage('Sorry, there was an error processing your message.', 'bot');
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
                    <img src="${bot.avatar}" alt="${bot.name}" class="profile-pic-chat">
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

    // Clear PII warning function
    clearPIIWarning() {
        const existingWarning = document.querySelector('.pii-warning-bar');
        if (existingWarning) {
            existingWarning.remove();
        }
        
        // Clear any modal overlays
        const existingModal = document.querySelector('.pii-modal-overlay');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Reset PII state
        if (window.piiDetector) {
            window.piiDetector.currentPIIDetected = [];
        }
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
        // Initialize with AI Assistant
        this.selectChat('ai-assistant');
    }

    // Real-time PII Detection
    detectPII(text) {
        if (!text.trim()) {
            this.hidePIIWarning();
            return;
        }

        const detectedPII = this.analyzePII(text);
        if (detectedPII.length > 0) {
            this.showPIIWarning(detectedPII);
        } else {
            this.hidePIIWarning();
        }
    }

    analyzePII(text) {
        const detectedTypes = [];
        
        // Email detection
        const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
        if (emailRegex.test(text)) {
            detectedTypes.push({ type: 'Email Address', icon: '📧', color: '#ff6b6b' });
        }

        // Phone number detection (various formats)
        const phoneRegex = /(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}|\+\d{1,3}[-.\s]?\d{1,14}/g;
        if (phoneRegex.test(text)) {
            detectedTypes.push({ type: 'Phone Number', icon: '📞', color: '#4ecdc4' });
        }

        // Credit card detection
        const creditCardRegex = /\b(?:\d{4}[-\s]?){3}\d{4}\b/g;
        if (creditCardRegex.test(text)) {
            detectedTypes.push({ type: 'Credit Card', icon: '💳', color: '#ffe66d' });
        }

        // Social Security Number
        const ssnRegex = /\b\d{3}-?\d{2}-?\d{4}\b/g;
        if (ssnRegex.test(text)) {
            detectedTypes.push({ type: 'SSN', icon: '🆔', color: '#ff6b6b' });
        }

        // Address detection (basic)
        const addressRegex = /\b\d+\s+([A-Za-z]+\s+){1,3}(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b/gi;
        if (addressRegex.test(text)) {
            detectedTypes.push({ type: 'Address', icon: '🏠', color: '#a8e6cf' });
        }

        // Date of birth
        const dobRegex = /\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12][0-9]|3[01])[\/\-](19|20)\d{2}\b/g;
        if (dobRegex.test(text)) {
            detectedTypes.push({ type: 'Date of Birth', icon: '🎂', color: '#ffb3ba' });
        }

        return detectedTypes;
    }

    showPIIWarning(detectedTypes) {
        let warningContainer = document.getElementById('pii-warning');
        if (!warningContainer) {
            warningContainer = document.createElement('div');
            warningContainer.id = 'pii-warning';
            warningContainer.className = 'pii-warning-container';
            
            const inputContainer = document.querySelector('.message-input-container');
            inputContainer.parentNode.insertBefore(warningContainer, inputContainer);
        }

        const typesHtml = detectedTypes.map(pii => 
            `<span class="pii-badge" style="background-color: ${pii.color}20; color: ${pii.color}; border: 1px solid ${pii.color}40;">
                ${pii.icon} ${pii.type}
            </span>`
        ).join('');

        warningContainer.innerHTML = `
            <div class="pii-warning-content">
                <div class="pii-warning-header">
                    <span class="warning-icon">⚠️</span>
                    <span class="warning-text">Sensitive information detected:</span>
                </div>
                <div class="pii-types">
                    ${typesHtml}
                </div>
                <div class="pii-warning-message">
                    Be careful sharing personal information in chats
                </div>
            </div>
        `;
        
        warningContainer.style.display = 'block';
    }

    hidePIIWarning() {
        const warningContainer = document.getElementById('pii-warning');
        if (warningContainer) {
            warningContainer.style.display = 'none';
        }
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
});