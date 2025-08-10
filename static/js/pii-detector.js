class PIIDetectorFrontend {
    constructor() {
        this.piiPatterns = {
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
            phone: /(\+91[\-\s]?)?[0]?(91)?[789]\d{9}/g,
            aadhar: /\b\d{4}\s?\d{4}\s?\d{4}\b/g,
            passport: /\b[A-Z]{1}[0-9]{7}\b/g,
            creditCard: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            pan: /\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b/g
        };
        
        this.piiKeywords = [
            'name', 'phone', 'email', 'address', 'aadhar', 'passport', 'ssn',
            'credit card', 'debit card', 'pan', 'bank account', 'license',
            'birth date', 'dob', 'age', 'location', 'zip code', 'pincode'
        ];
    }

    // Quick client-side PII detection for immediate feedback
    quickDetectPII(text) {
        const detected = [];
        
        for (const [type, pattern] of Object.entries(this.piiPatterns)) {
            const matches = text.match(pattern);
            if (matches) {
                matches.forEach(match => {
                    detected.push({
                        type: type,
                        value: match,
                        confidence: 0.8
                    });
                });
            }
        }
        
        // Basic name detection (capitalized words)
        const namePattern = /\b[A-Z][a-z]+ [A-Z][a-z]+/g;
        const nameMatches = text.match(namePattern);
        if (nameMatches) {
            nameMatches.forEach(match => {
                // Exclude common non-names
                const commonWords = ['Hello There', 'Thank You', 'Good Morning', 'Best Regards'];
                if (!commonWords.includes(match)) {
                    detected.push({
                        type: 'name',
                        value: match,
                        confidence: 0.6
                    });
                }
            });
        }
        
        return detected;
    }

    // Show PII confirmation dialog
    showPIIConfirmation(message, detectedPII, callback) {
        const modal = document.createElement('div');
        modal.className = 'pii-modal-overlay';
        modal.innerHTML = `
            <div class="pii-modal">
                <div class="pii-modal-header">
                    <h3>🔒 PII Detected</h3>
                    <p>We found potentially sensitive information in your message:</p>
                </div>
                <div class="pii-detected-list">
                    ${detectedPII.map(pii => `
                        <div class="pii-item">
                            <span class="pii-type">${this.formatPIIType(pii.type)}</span>
                            <span class="pii-value">${pii.value}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="pii-message-preview">
                    <h4>Your message:</h4>
                    <div class="message-preview">${message}</div>
                </div>
                <div class="pii-modal-actions">
                    <button class="btn-pii-send-redacted">
                        <i class="fas fa-shield-alt"></i>
                        Send with Redaction
                    </button>
                    <button class="btn-pii-send-original">
                        <i class="fas fa-paper-plane"></i>
                        Send Original Message
                    </button>
                    <button class="btn-pii-cancel">
                        <i class="fas fa-times"></i>
                        Cancel
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle button clicks
        modal.querySelector('.btn-pii-send-redacted').onclick = () => {
            document.body.removeChild(modal);
            callback('redacted');
        };

        modal.querySelector('.btn-pii-send-original').onclick = () => {
            document.body.removeChild(modal);
            callback('original');
        };

        modal.querySelector('.btn-pii-cancel').onclick = () => {
            document.body.removeChild(modal);
            callback('cancel');
        };

        // Close on overlay click
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                callback('cancel');
            }
        };
    }

    formatPIIType(type) {
        const typeMap = {
            email: 'Email Address',
            phone: 'Phone Number',
            aadhar: 'Aadhar Number',
            passport: 'Passport Number',
            creditCard: 'Credit Card',
            pan: 'PAN Number',
            name: 'Personal Name'
        };
        return typeMap[type] || type.toUpperCase();
    }

    // Send message to backend for comprehensive PII analysis
    async sendMessageWithPIIAnalysis(message, sendRedacted = false) {
        try {
            const response = await fetch('/api/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    bot_id: window.chatManager ? window.chatManager.currentBot : 'ai-assistant',
                    send_redacted: sendRedacted
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }
}

// Global PII detector instance
window.piiDetector = new PIIDetectorFrontend();