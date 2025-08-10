class ChatManager {
    constructor() {
        this.currentBot = 'ai-assistant';
        this.bots = {
            'ai-assistant': {
                name: 'Sarah Chen',
                subtitle: 'AI Assistant',
                avatar: '👩‍💼',
                class: 'ai-avatar',
                responses: [
                    "Hey there! 😊 I'm Sarah and I love chatting about anything - movies, books, life experiences, dreams, you name it! What's been on your mind lately?",
                    "That sounds really interesting! I love hearing people's stories and experiences. Tell me more!",
                    "I'm always curious about different perspectives on life. What's something that's made you happy recently?",
                    "Nice to meet you! I enjoy deep conversations about anything from hobbies to life philosophy. What are you passionate about?",
                    "I find everyone has such unique stories to tell. What's something exciting happening in your life right now?",
                    "I love getting to know new people! What kind of stuff do you enjoy doing in your free time?"
                ]
            },
            'pii-detector': {
                name: 'Alex Rodriguez',
                subtitle: 'Security Expert',
                avatar: '👨‍🔒',
                class: 'security-avatar',
                responses: [
                    "What's up! I'm Alex and I'm really into cybersecurity and tech stuff. But I also love talking about sports, travel, and random life stories. What's going on with you?",
                    "That's awesome! I love hearing about people's adventures. Any cool travel stories or favorite places you've been?",
                    "Nice! I work in tech but I'm also into hiking and photography. What kind of hobbies are you into?",
                    "Sounds interesting! I've been working in cybersecurity for years, but I find people's personal stories way more fascinating. Tell me more!",
                    "Cool! I love meeting new people and hearing about their experiences. What's been the highlight of your week?",
                    "I'm always down for good conversations about anything - work, life, dreams, you name it. What's on your mind today?"
                ]
            },
            'news-bot': {
                name: 'Maya Patel',
                subtitle: 'News Reporter',
                avatar: '👩‍📺',
                class: 'news-avatar',
                responses: [
                    "Hi! Maya here - I'm a journalist so I'm always curious about people's stories and experiences. Tell me something interesting about your day or life!",
                    "That's so cool! I love hearing unique perspectives. Being a reporter has taught me everyone has amazing stories to tell. What's yours?",
                    "Interesting! I work in journalism but I'm fascinated by all kinds of conversations - from personal experiences to random thoughts. What's been on your mind?",
                    "Nice to meet you! I spend my days interviewing people, and I've learned that the most ordinary moments can be extraordinary. Share something with me!",
                    "I love that! Working as a reporter, I've met so many different people with incredible stories. What's something that's made you smile recently?",
                    "That sounds great! I'm always curious about people's lives and experiences. What's the most interesting thing that's happened to you lately?"
                ]
            },
            'weather-bot': {
                name: 'David Kim',
                subtitle: 'Meteorologist',
                avatar: '👨‍🔬',
                class: 'weather-avatar',
                responses: [
                    "Hello! I'm David, and while I work with weather data, I'm fascinated by all kinds of conversations - from science to hobbies to personal experiences. What brings you here today?",
                    "That's awesome! I love hearing about people's interests. I work as a meteorologist but I'm into so many other things too. What are you passionate about?",
                    "Cool! You know, working with weather patterns is interesting, but I find people's stories even more fascinating. Tell me about yourself!",
                    "Nice to meet you! I study weather for a living, but I love chatting about everything - travel, food, books, life experiences. What's been exciting for you lately?",
                    "That sounds great! I spend my days analyzing atmospheric data, but I much prefer learning about people's adventures and dreams. What's on your mind?",
                    "Interesting! I've been a meteorologist for years, but I find human conversations way more unpredictable than weather patterns. What's your story?"
                ]
            },
            'translator-bot': {
                name: 'Elena Kowalski',
                subtitle: 'Linguist',
                avatar: '👩‍🏫',
                class: 'translator-avatar',
                responses: [
                    "¡Hola! I'm Elena and I absolutely love languages and cultures. I enjoy chatting about travel, food, music, or just everyday life. How are you doing?",
                    "That's wonderful! I work with languages but I'm curious about people's lives and experiences. What's something fun you've been up to?",
                    "Nice to meet you! I speak several languages and have lived in different countries. I love hearing about people's adventures and stories. Tell me about yours!",
                    "That sounds interesting! Working with languages has shown me how diverse and fascinating people's experiences can be. What's been going on in your world?",
                    "Cool! I've studied linguistics but I find personal conversations much more engaging than textbooks. What's something that's made you happy recently?",
                    "Great to chat with you! I love learning about different cultures and people's lives. Share something interesting about yourself!"
                ]
            },
            'code-helper': {
                name: 'Ryan O\'Connor',
                subtitle: 'Senior Developer',
                avatar: '👨‍💻',
                class: 'code-avatar',
                responses: [
                    "Hey! I'm Ryan, a developer who loves coding but also enjoys gaming, music, and deep conversations about life. What's on your mind today?",
                    "That's cool! I work with code all day, but I find people's stories and experiences way more interesting. Tell me about yourself!",
                    "Nice to meet you! I've been coding for years, but I love chatting about all sorts of stuff - hobbies, travel, dreams, random thoughts. What brings you here?",
                    "Awesome! You know, I spend a lot of time debugging code, but I'd rather debug life's mysteries through good conversations. What's been happening with you?",
                    "That sounds interesting! I'm a developer by trade but I enjoy talking about everything - from personal experiences to philosophical questions. Share something with me!",
                    "Great to chat with you! I love technology but I find human connections even more fascinating. What's something that's been on your mind lately?"
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

        // Real-time PII detection
        messageInput.addEventListener('input', (e) => {
            this.detectPII(e.target.value);
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
        document.querySelector('.contact-avatar .avatar-circle').className = `avatar-circle ${bot.class}`;
        document.querySelector('.contact-avatar .avatar-circle').innerHTML = bot.avatar;

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

    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        messageInput.value = '';

        // Simulate bot response
        setTimeout(() => {
            this.addBotResponse();
        }, 1000 + Math.random() * 2000);
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
                    <div class="avatar-circle ${bot.class}">
                        ${bot.avatar}
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
                <div class="avatar-circle ${bot.class}">
                    ${bot.avatar}
                </div>
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