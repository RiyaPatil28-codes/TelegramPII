class ChatManager {
    constructor() {
        this.currentBot = 'ai-assistant';
        this.bots = {
            'ai-assistant': {
                name: 'AI Assistant',
                avatar: '<i class="fas fa-robot"></i>',
                class: 'ai-avatar',
                responses: [
                    "I'm here to help! What would you like to know?",
                    "That's an interesting question. Let me think about that...",
                    "I can help you with various tasks. What do you need assistance with?",
                    "Feel free to ask me anything - I'm here to help!",
                    "Is there something specific you'd like to discuss?"
                ]
            },
            'pii-detector': {
                name: 'PII Detector Bot',
                avatar: '<i class="fas fa-shield-alt"></i>',
                class: 'security-avatar',
                responses: [
                    "I'll scan your message for personal information. Please send the text you want me to analyze.",
                    "No PII detected in your message. It looks safe to share!",
                    "⚠️ I found potential personal information in your message. Please review before sharing.",
                    "I can detect emails, phone numbers, addresses, and other sensitive data.",
                    "Your privacy is important. I'll help you identify sensitive information."
                ]
            },
            'news-bot': {
                name: 'News Bot',
                avatar: '<i class="fas fa-newspaper"></i>',
                class: 'news-avatar',
                responses: [
                    "Here are today's top headlines from around the world:",
                    "Breaking news: Stay updated with the latest developments!",
                    "Would you like news from a specific category or region?",
                    "I can provide news on technology, sports, business, and more.",
                    "What type of news interests you most?"
                ]
            },
            'weather-bot': {
                name: 'Weather Bot',
                avatar: '<i class="fas fa-cloud-sun"></i>',
                class: 'weather-avatar',
                responses: [
                    "Today's weather: Sunny with a high of 24°C and low of 18°C",
                    "Perfect weather for outdoor activities! Clear skies expected.",
                    "Which city would you like the weather forecast for?",
                    "I can provide current conditions and 5-day forecasts.",
                    "Don't forget your umbrella - rain expected this evening!"
                ]
            },
            'translator-bot': {
                name: 'Translator Bot',
                avatar: '<i class="fas fa-language"></i>',
                class: 'translator-avatar',
                responses: [
                    "I can translate between over 100 languages. What would you like to translate?",
                    "Just send me the text and specify the target language!",
                    "Translation complete! Here's your text in the requested language:",
                    "I support real-time translation for instant communication.",
                    "Which languages would you like me to translate between?"
                ]
            },
            'code-helper': {
                name: 'Code Helper',
                avatar: '<i class="fas fa-code"></i>',
                class: 'code-avatar',
                responses: [
                    "I can help you with programming questions, code reviews, and debugging!",
                    "What programming language are you working with?",
                    "Here's a solution for your coding problem:",
                    "I support Python, JavaScript, Java, C++, and many other languages.",
                    "Need help with algorithms, data structures, or specific coding tasks?"
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
        const bot = this.bots[this.currentBot];
        const responses = bot.responses;
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        this.addMessage(randomResponse, 'bot');
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
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
});