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
                    "Hi! I'm Sarah, your AI assistant. I love helping people solve problems and find answers.",
                    "That's a fascinating question! Let me share what I know about that topic...",
                    "I've been working in AI for several years now. What can I help you accomplish today?",
                    "Great to meet you! I enjoy having meaningful conversations and helping with various tasks.",
                    "As an AI specialist, I'm always excited to tackle new challenges. What's on your mind?",
                    "I find every conversation unique and interesting. How can I assist you right now?"
                ]
            },
            'pii-detector': {
                name: 'Alex Rodriguez',
                subtitle: 'Security Expert',
                avatar: '👨‍🔒',
                class: 'security-avatar',
                responses: [
                    "Hey there! Alex here. I'm a cybersecurity specialist. Send me text and I'll scan for sensitive info.",
                    "Perfect! No personal information detected in your message. You're all clear!",
                    "⚠️ Hold up! I spotted potential PII in that text. Let me highlight what I found...",
                    "As someone who's worked in data protection for 8 years, I can spot risky info instantly.",
                    "Your privacy matters to me. I'll help you identify emails, phones, SSNs, and more.",
                    "I've seen too many data breaches. Let me help keep your information secure!"
                ]
            },
            'news-bot': {
                name: 'Maya Patel',
                subtitle: 'News Reporter',
                avatar: '👩‍📺',
                class: 'news-avatar',
                responses: [
                    "Good day! Maya here, reporting live with today's most important stories.",
                    "Breaking update: I've got the latest news fresh from the newsroom!",
                    "As a journalist, I love keeping people informed. What news topics interest you?",
                    "I cover everything from tech breakthroughs to local community events. What would you like to hear about?",
                    "Just finished my morning briefing. Want the headlines or something more specific?",
                    "I've been in journalism for 10 years. News moves fast, but I'll keep you updated!"
                ]
            },
            'weather-bot': {
                name: 'David Kim',
                subtitle: 'Meteorologist',
                avatar: '👨‍🔬',
                class: 'weather-avatar',
                responses: [
                    "Hi! David here, your friendly neighborhood meteorologist. Beautiful day ahead!",
                    "Currently 24°C with sunny skies - perfect weather for any outdoor plans you might have!",
                    "I've been forecasting weather for 15 years. Which location would you like me to check?",
                    "Fun weather fact: This high-pressure system will keep us sunny for the next few days!",
                    "Planning something outdoors? I can give you hour-by-hour forecasts to help you decide.",
                    "As a meteorologist, I love talking about weather patterns. Tonight's looking clear and cool!"
                ]
            },
            'translator-bot': {
                name: 'Elena Kowalski',
                subtitle: 'Linguist',
                avatar: '👩‍🏫',
                class: 'translator-avatar',
                responses: [
                    "¡Hola! I'm Elena. I speak 12 languages fluently and love helping people communicate!",
                    "Bonjour! As a linguistics professor, translation is my passion. What can I help you with?",
                    "I studied at universities in Paris, Tokyo, and São Paulo. Send me anything to translate!",
                    "Languages are beautiful! I can handle everything from casual messages to technical documents.",
                    "Fun fact: I can often detect what language you're writing in just from context clues!",
                    "Whether it's business, poetry, or casual chat - I'll help you break language barriers!"
                ]
            },
            'code-helper': {
                name: 'Ryan O\'Connor',
                subtitle: 'Senior Developer',
                avatar: '👨‍💻',
                class: 'code-avatar',
                responses: [
                    "Hey! Ryan here, senior full-stack developer with 12+ years in the field. What's your coding challenge?",
                    "I work mainly in Python, JavaScript, and React these days. What project are you building?",
                    "Debugging is like solving puzzles - I love it! Share your code and I'll take a look.",
                    "From startups to big tech, I've seen it all. Every bug has a story, let's solve yours!",
                    "Currently leading a team at a tech company, but I always enjoy helping fellow developers.",
                    "Coffee, code, repeat! That's been my life. What programming problem can we tackle together?"
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
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
});