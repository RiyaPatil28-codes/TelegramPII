class PIIDetectorFrontend {
    constructor() {
        this.piiPatterns = {
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
            // Comprehensive international phone patterns
            phone_us: /(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
            phone_uk: /(?:\+?44[-.\s]?)?(?:0[-.\s]?)?(?:[1-9]\d{8,9}|[1-9]\d{3}[-.\s]?\d{6})\b/g,
            phone_india: /(?:\+?91[-.\s]?)?[0]?[6-9]\d{9}\b/g,
            phone_china: /(?:\+?86[-.\s]?)?1[3-9]\d{9}\b/g,
            phone_germany: /(?:\+?49[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{10,11}\b/g,
            phone_france: /(?:\+?33[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_japan: /(?:\+?81[-.\s]?)?(?:0[-.\s]?)?[7-9]0[-.\s]?\d{4}[-.\s]?\d{4}\b/g,
            phone_australia: /(?:\+?61[-.\s]?)?(?:0[-.\s]?)?[2-478]\d{8}\b/g,
            phone_canada: /(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
            phone_brazil: /(?:\+?55[-.\s]?)?(?:\(?[1-9]{2}\)?[-.\s]?)?[9]?[0-9]{4}[-.\s]?\d{4}\b/g,
            phone_russia: /(?:\+?7[-.\s]?)?[489]\d{2}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b/g,
            phone_mexico: /(?:\+?52[-.\s]?)?(?:1[-.\s]?)?[2-9]\d{2}[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
            phone_italy: /(?:\+?39[-.\s]?)?(?:0[-.\s]?)?[0-9]{6,11}\b/g,
            phone_spain: /(?:\+?34[-.\s]?)?[6-9]\d{8}\b/g,
            phone_south_korea: /(?:\+?82[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,8}\b/g,
            phone_netherlands: /(?:\+?31[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_sweden: /(?:\+?46[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,8}\b/g,
            phone_norway: /(?:\+?47[-.\s]?)?[2-9]\d{7}\b/g,
            phone_denmark: /(?:\+?45[-.\s]?)?[2-9]\d{7}\b/g,
            phone_switzerland: /(?:\+?41[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_belgium: /(?:\+?32[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,8}\b/g,
            phone_austria: /(?:\+?43[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{6,12}\b/g,
            phone_poland: /(?:\+?48[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_singapore: /(?:\+?65[-.\s]?)?[6-9]\d{7}\b/g,
            phone_malaysia: /(?:\+?60[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,9}\b/g,
            phone_thailand: /(?:\+?66[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_indonesia: /(?:\+?62[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,11}\b/g,
            phone_philippines: /(?:\+?63[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{9}\b/g,
            phone_vietnam: /(?:\+?84[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8,9}\b/g,
            phone_south_africa: /(?:\+?27[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_nigeria: /(?:\+?234[-.\s]?)?(?:0[-.\s]?)?[7-9]\d{9}\b/g,
            phone_egypt: /(?:\+?20[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8,9}\b/g,
            phone_turkey: /(?:\+?90[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{9}\b/g,
            phone_israel: /(?:\+?972[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,8}\b/g,
            phone_uae: /(?:\+?971[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{7,8}\b/g,
            phone_saudi_arabia: /(?:\+?966[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_argentina: /(?:\+?54[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{6,10}\b/g,
            phone_chile: /(?:\+?56[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_colombia: /(?:\+?57[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{9}\b/g,
            phone_peru: /(?:\+?51[-.\s]?)?(?:0[-.\s]?)?[1-9]\d{8}\b/g,
            phone_new_zealand: /(?:\+?64[-.\s]?)?(?:0[-.\s]?)?[2-9]\d{7,9}\b/g,
            // Generic international format
            phone_international: /\+[1-9]\d{1,14}\b/g,
            aadhar: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            passport: /\b[A-Z]{1}[0-9]{7}\b/g,
            creditCard: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            pan: /\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b/g,
            ssn: /\b\d{3}-?\d{2}-?\d{4}\b/g,
            birthDate: /\b(?:0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](?:19|20)\d{2}\b/g,
            idNumber: /\b(?:ID|id|Id)[\s\-\#\:]*[A-Z0-9]{6,15}\b/g
        };
        
        this.piiKeywords = [
            'name', 'phone', 'email', 'address', 'aadhar', 'passport', 'ssn',
            'credit card', 'debit card', 'pan', 'bank account', 'license',
            'birth date', 'dob', 'age', 'location', 'zip code', 'pincode',
            'live in', 'from', 'city', 'state', 'country', 'id number',
            'my name is', 'i am', 'born on', 'birthday'
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
        
        // Enhanced name detection with context
        const namePatterns = [
            /\b(?:my name is|i am|i'm|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/gi,
            /\b([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:here|speaking|calling)/gi,
            /\b(?:mr|mrs|ms|dr|prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/gi
        ];
        
        namePatterns.forEach(pattern => {
            const nameMatches = [...text.matchAll(pattern)];
            nameMatches.forEach(match => {
                const name = match[1] || match[0];
                const commonWords = ['Hello There', 'Thank You', 'Good Morning', 'Best Regards', 'New York', 'Los Angeles'];
                if (!commonWords.includes(name)) {
                    detected.push({
                        type: 'person_name',
                        value: name,
                        confidence: 0.8
                    });
                }
            });
        });
        
        // Place name detection
        const placePatterns = [
            /\b(?:live in|from|at|in|near|visiting|traveled to|going to|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/gi,
            /\b(Mumbai|Delhi|Bangalore|Chennai|Kolkata|New York|Los Angeles|London|California|Texas)\b/gi
        ];
        
        placePatterns.forEach(pattern => {
            const placeMatches = [...text.matchAll(pattern)];
            placeMatches.forEach(match => {
                const place = match[1] || match[0];
                detected.push({
                    type: 'place_name',
                    value: place,
                    confidence: 0.85
                });
            });
        });
        
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
            'name': '[NAME_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'birthDate': '[BIRTHDATE_REDACTED]',
            'idNumber': '[ID_REDACTED]',
            'place_name': '[LOCATION_REDACTED]',
            'person_name': '[NAME_REDACTED]',
            'birth_date': '[BIRTHDATE_REDACTED]',
            'id_number': '[ID_REDACTED]',
            'driver_license': '[LICENSE_REDACTED]'
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