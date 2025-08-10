// Chat functionality
class ChatManager {
    constructor() {
        this.currentChatId = null;
        this.currentChatName = null;
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.messagesContainer = document.getElementById('messages-container');
        this.welcomeScreen = document.getElementById('welcome-screen');
        this.chatWindow = document.getElementById('chat-window');
        
        this.initializeEventListeners();
        this.loadContacts();
    }
    
    initializeEventListeners() {
        // Message input event listeners
        this.messageInput.addEventListener('input', () => {
            const message = this.messageInput.value.trim();
            this.sendButton.disabled = !message;
            
            // Auto-resize textarea
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        this.sendButton.addEventListener('click', () => {
            this.handleSendMessage();
        });
        
        // Auto-scroll to bottom when new messages are added
        if (this.messagesContainer) {
            const observer = new MutationObserver(() => {
                this.scrollToBottom();
            });
            observer.observe(this.messagesContainer, { childList: true });
        }
    }
    
    loadContacts() {
        fetch('/api/contacts')
            .then(response => response.json())
            .then(data => {
                if (data.contacts) {
                    this.renderContacts(data.contacts);
                }
            })
            .catch(error => {
                console.error('Error loading contacts:', error);
            });
    }
    
    renderContacts(contacts) {
        // Contacts are already rendered server-side, but we can update them here if needed
        console.log('Contacts loaded:', contacts.length);
    }
    
    async handleSendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.currentChatId) return;
        
        try {
            // First, analyze the message for PII
            const analysisResponse = await fetch('/api/analyze_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const analysisData = await analysisResponse.json();
            
            if (analysisData.has_pii) {
                // Show PII warning and let user decide
                this.showPIIWarning(message, analysisData);
            } else {
                // Send message normally
                await this.sendMessage(message, false, null);
            }
            
        } catch (error) {
            console.error('Error handling message:', error);
            this.showError('Failed to send message. Please try again.');
        }
    }
    
    showPIIWarning(originalMessage, analysisData) {
        const modal = new bootstrap.Modal(document.getElementById('piiModal'));
        
        // Update modal content
        document.getElementById('original-message-preview').textContent = originalMessage;
        document.getElementById('redacted-message-preview').textContent = analysisData.redacted_message;
        
        // Show detected PII
        const piiList = document.getElementById('detected-pii-list');
        piiList.innerHTML = analysisData.pii_detected.map(pii => 
            `<span class="badge bg-warning me-2 mb-2">
                <i class="fas fa-exclamation-triangle"></i> 
                ${pii.type.toUpperCase()}: ${pii.value} 
                (${Math.round(pii.confidence * 100)}% confidence)
            </span>`
        ).join('');
        
        // Handle modal button clicks
        document.getElementById('modal-send-redacted').onclick = () => {
            modal.hide();
            this.sendMessage(analysisData.redacted_message, true, analysisData.redacted_message);
        };
        
        document.getElementById('modal-send-original').onclick = () => {
            modal.hide();
            this.sendMessage(originalMessage, false, null);
        };
        
        modal.show();
    }
    
    async sendMessage(content, useRedacted, redactedContent) {
        try {
            const response = await fetch('/api/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipient_id: this.currentChatId,
                    content: content,
                    use_redacted: useRedacted,
                    redacted_content: redactedContent
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Clear input and refresh messages
                this.messageInput.value = '';
                this.sendButton.disabled = true;
                this.messageInput.style.height = 'auto';
                
                // Add message to UI immediately for better UX
                this.addMessageToUI({
                    content: content,
                    is_own_message: true,
                    timestamp: new Date().toISOString(),
                    has_pii: data.has_pii
                });
                
                if (data.has_pii && data.pii_count > 0) {
                    this.showNotification(`Message sent with ${data.pii_count} PII item(s) ${useRedacted ? 'redacted' : 'unredacted'}`, 'info');
                }
            } else {
                this.showError(data.error || 'Failed to send message');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message. Please try again.');
        }
    }
    
    addMessageToUI(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_own_message ? 'own' : ''}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        const content = document.createElement('p');
        content.className = 'message-content';
        content.textContent = message.content;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatMessageTime(message.timestamp);
        
        bubble.appendChild(content);
        bubble.appendChild(time);
        
        // Add PII indicator if message has PII
        if (message.has_pii) {
            const piiIndicator = document.createElement('div');
            piiIndicator.className = 'pii-indicator';
            piiIndicator.innerHTML = '<i class="fas fa-shield-alt" title="This message was processed for PII"></i>';
            bubble.appendChild(piiIndicator);
        }
        
        messageDiv.appendChild(bubble);
        this.messagesContainer.appendChild(messageDiv);
        
        // Add fade-in animation
        messageDiv.classList.add('fade-in');
    }
    
    formatMessageTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    async loadMessages(contactId) {
        try {
            const response = await fetch(`/api/get_messages/${contactId}`);
            const data = await response.json();
            
            if (data.messages) {
                this.renderMessages(data.messages);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            this.showError('Failed to load messages');
        }
    }
    
    renderMessages(messages) {
        this.messagesContainer.innerHTML = '';
        
        if (messages.length === 0) {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'text-center text-muted mt-5';
            emptyDiv.innerHTML = `
                <i class="fas fa-comments fa-3x mb-3" style="opacity: 0.3;"></i>
                <p>No messages yet. Start the conversation!</p>
            `;
            this.messagesContainer.appendChild(emptyDiv);
            return;
        }
        
        messages.forEach(message => {
            this.addMessageToUI(message);
        });
        
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of chat area
        const chatArea = document.querySelector('.chat-area');
        chatArea.insertBefore(alert, chatArea.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of page
        const main = document.querySelector('main');
        main.insertBefore(alert, main.firstChild);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
}

// Global function to open chat (called from HTML)
function openChat(contactId, contactName) {
    // Update active contact
    document.querySelectorAll('.contact-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-contact-id="${contactId}"]`).classList.add('active');
    
    // Show chat window
    document.getElementById('welcome-screen').classList.add('d-none');
    document.getElementById('chat-window').classList.remove('d-none');
    
    // Update chat header
    document.getElementById('chat-contact-name').textContent = contactName;
    
    // Set current chat in manager
    if (window.chatManager) {
        window.chatManager.currentChatId = contactId;
        window.chatManager.currentChatName = contactName;
        window.chatManager.loadMessages(contactId);
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatManager = new ChatManager();
});
