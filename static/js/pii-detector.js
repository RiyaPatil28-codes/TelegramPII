class PIIDetectorFrontend {
    constructor() {
        this.piiPatterns = {
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
            phone: /(\+91[\-\s]?)?[0]?(91)?[789]\d{9}/g,
            aadhar: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            passport: /\b[A-Z]{1}[0-9]{7}\b/g,
            creditCard: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            pan: /\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b/g
        };
        
        this.piiKeywords = [
            'name', 'phone', 'email', 'address', 'aadhar', 'passport', 'ssn',
            'credit card', 'debit card', 'pan', 'bank account', 'license',
            'birth date', 'dob', 'age', 'location', 'zip code', 'pincode'
        ];
        
        this.currentPIIDetected = []; // Track current PII state
    }

    // Clear PII detection state
    clearPIIState() {
        this.currentPIIDetected = [];
        const existingModals = document.querySelectorAll('.pii-modal-overlay');
        existingModals.forEach(modal => modal.remove());
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

    // Generate redacted preview
    generateRedactedPreview(message, detectedPII) {
        let redactedMessage = message;
        const replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'aadhar': '[AADHAR_REDACTED]',
            'passport': '[PASSPORT_REDACTED]',
            'creditCard': '[CARD_REDACTED]',
            'pan': '[PAN_REDACTED]',
            'name': '[NAME_REDACTED]'
        };

        detectedPII.forEach(pii => {
            const replacement = `<span class="redacted-text">${replacements[pii.type] || '[REDACTED]'}</span>`;
            redactedMessage = redactedMessage.replace(new RegExp(pii.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacement);
        });

        return redactedMessage;
    }

    // Show PII confirmation dialog with enhanced UI
    showPIIConfirmation(message, detectedPII, callback) {
        const redactedPreview = this.generateRedactedPreview(message, detectedPII);
        let selectedRedaction = 'placeholder'; // Default redaction method
        
        const modal = document.createElement('div');
        modal.className = 'pii-modal-overlay';
        modal.innerHTML = `
            <div class="pii-modal">
                <div class="pii-modal-header">
                    <h3>PII Detected</h3>
                    <p>We found potentially sensitive information in your message. Choose how to proceed:</p>
                </div>
                <div class="pii-detected-list">
                    <h4 class="pii-section-title">Detected Sensitive Information:</h4>
                    ${detectedPII.map(pii => `
                        <div class="pii-item">
                            <span class="pii-type">${this.formatPIIType(pii.type)}</span>
                            <span class="pii-value">${pii.value}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="pii-redaction-options">
                    <h4>Redaction Options:</h4>
                    <label class="redaction-choice selected" data-method="placeholder">
                        <input type="radio" name="redaction" value="placeholder" checked>
                        <div class="redaction-label">
                            <div class="redaction-title">Replace with Placeholders</div>
                            <div class="redaction-description">Replace sensitive data with [EMAIL_REDACTED], [PHONE_REDACTED], etc.</div>
                        </div>
                    </label>
                    <label class="redaction-choice" data-method="mask">
                        <input type="radio" name="redaction" value="mask">
                        <div class="redaction-label">
                            <div class="redaction-title">Mask with Symbols</div>
                            <div class="redaction-description">Replace with *** or #### while keeping format (john@***.com)</div>
                        </div>
                    </label>
                    <label class="redaction-choice" data-method="remove">
                        <input type="radio" name="redaction" value="remove">
                        <div class="redaction-label">
                            <div class="redaction-title">Remove Completely</div>
                            <div class="redaction-description">Remove sensitive information entirely from the message</div>
                        </div>
                    </label>
                </div>
                <div class="pii-message-preview">
                    <div class="pii-preview-tabs">
                        <button class="pii-tab active" data-tab="original">Original</button>
                        <button class="pii-tab" data-tab="redacted">Redacted Preview</button>
                    </div>
                    <div class="message-preview" id="originalPreview">${message}</div>
                    <div class="message-preview redacted" id="redactedPreview" style="display: none;">${redactedPreview}</div>
                </div>
                <div class="pii-modal-actions">
                    <button class="btn-pii-send-redacted">
                        <i class="fas fa-shield-alt"></i>
                        Send with Redaction
                    </button>
                    <button class="btn-pii-send-original">
                        <i class="fas fa-paper-plane"></i>
                        Send Original
                    </button>
                    <button class="btn-pii-cancel">
                        <i class="fas fa-times"></i>
                        Cancel
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle tab switching
        const tabs = modal.querySelectorAll('.pii-tab');
        const originalPreview = modal.querySelector('#originalPreview');
        const redactedPreviewElement = modal.querySelector('#redactedPreview');
        
        tabs.forEach(tab => {
            tab.onclick = () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                if (tab.dataset.tab === 'original') {
                    originalPreview.style.display = 'block';
                    redactedPreviewElement.style.display = 'none';
                } else {
                    originalPreview.style.display = 'none';
                    redactedPreviewElement.style.display = 'block';
                }
            };
        });

        // Handle redaction option changes
        const redactionChoices = modal.querySelectorAll('.redaction-choice');
        redactionChoices.forEach(choice => {
            choice.onclick = () => {
                redactionChoices.forEach(c => c.classList.remove('selected'));
                choice.classList.add('selected');
                choice.querySelector('input').checked = true;
                selectedRedaction = choice.dataset.method;
                
                // Update preview based on selection
                this.updateRedactedPreview(message, detectedPII, selectedRedaction, redactedPreviewElement);
            };
        });

        // Handle button clicks
        modal.querySelector('.btn-pii-send-redacted').onclick = () => {
            document.body.removeChild(modal);
            callback('redacted', selectedRedaction);
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

    // Update redacted preview based on selected method
    updateRedactedPreview(message, detectedPII, method, previewElement) {
        let redactedMessage = message;
        
        const replacements = {
            'placeholder': {
                'email': '[EMAIL_REDACTED]',
                'phone': '[PHONE_REDACTED]',
                'aadhar': '[AADHAR_REDACTED]',
                'passport': '[PASSPORT_REDACTED]',
                'creditCard': '[CARD_REDACTED]',
                'pan': '[PAN_REDACTED]',
                'name': '[NAME_REDACTED]'
            },
            'mask': {
                'email': (value) => value.replace(/(.{2})(.*)(@.{2})(.*)/, '$1***$3***'),
                'phone': (value) => value.replace(/(\d{3})(\d*)(\d{3})/, '$1****$3'),
                'aadhar': (value) => value.replace(/(\d{4})(.*)(\d{4})/, '$1-****-$3'),
                'passport': (value) => value.replace(/([A-Z]{1})(.*)/, '$1*******'),
                'creditCard': (value) => value.replace(/(\d{4})(.*)(\d{4})/, '$1-****-****-$3'),
                'pan': (value) => value.replace(/([A-Z]{3})(.*)([A-Z]{1})/, '$1**$4**$3'),
                'name': (value) => value.replace(/(\w+)\s+(\w+)/, '$1 ***')
            },
            'remove': ''
        };

        detectedPII.forEach(pii => {
            let replacement;
            if (method === 'mask' && typeof replacements[method][pii.type] === 'function') {
                replacement = `<span class="redacted-text">${replacements[method][pii.type](pii.value)}</span>`;
            } else if (method === 'placeholder') {
                replacement = `<span class="redacted-text">${replacements[method][pii.type] || '[REDACTED]'}</span>`;
            } else if (method === 'remove') {
                replacement = '';
            }
            
            redactedMessage = redactedMessage.replace(new RegExp(pii.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacement);
        });

        previewElement.innerHTML = redactedMessage;
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