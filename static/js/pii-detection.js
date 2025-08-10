// PII Detection utilities and helpers
class PIIDetector {
    constructor() {
        this.detectionCache = new Map();
        this.isAnalyzing = false;
    }
    
    // Analyze text for PII
    async analyzeText(text) {
        if (this.detectionCache.has(text)) {
            return this.detectionCache.get(text);
        }
        
        if (this.isAnalyzing) {
            return null;
        }
        
        this.isAnalyzing = true;
        
        try {
            const response = await fetch('/api/analyze_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: text })
            });
            
            const result = await response.json();
            
            // Cache the result
            this.detectionCache.set(text, result);
            
            // Limit cache size
            if (this.detectionCache.size > 100) {
                const firstKey = this.detectionCache.keys().next().value;
                this.detectionCache.delete(firstKey);
            }
            
            return result;
        } catch (error) {
            console.error('Error analyzing text for PII:', error);
            return null;
        } finally {
            this.isAnalyzing = false;
        }
    }
    
    // Real-time PII detection as user types
    setupRealTimeDetection(inputElement, warningElement) {
        let debounceTimer;
        
        inputElement.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(async () => {
                const text = inputElement.value.trim();
                
                if (text.length < 3) {
                    this.hideWarning(warningElement);
                    return;
                }
                
                const result = await this.analyzeText(text);
                
                if (result && result.has_pii) {
                    this.showWarning(warningElement, result);
                } else {
                    this.hideWarning(warningElement);
                }
            }, 500); // 500ms debounce
        });
    }
    
    showWarning(warningElement, analysisResult) {
        if (!warningElement) return;
        
        warningElement.classList.remove('d-none');
        
        // Update PII details
        const detailsElement = warningElement.querySelector('.pii-details, #pii-details');
        if (detailsElement) {
            const piiList = analysisResult.pii_detected.map(pii => 
                `<span class="pii-item">
                    ${pii.type}: ${pii.value} (${Math.round(pii.confidence * 100)}%)
                </span>`
            ).join('');
            
            detailsElement.innerHTML = `
                <strong>Detected PII:</strong><br>
                ${piiList}
            `;
        }
        
        // Update redacted preview if available
        const redactedPreview = document.getElementById('redacted-message-preview');
        if (redactedPreview && analysisResult.redacted_message) {
            redactedPreview.textContent = analysisResult.redacted_message;
        }
    }
    
    hideWarning(warningElement) {
        if (warningElement) {
            warningElement.classList.add('d-none');
        }
    }
    
    // Format PII type for display
    formatPIIType(type) {
        const typeMap = {
            'email': 'Email Address',
            'phone': 'Phone Number',
            'aadhar': 'Aadhar Number',
            'passport': 'Passport Number',
            'credit_card': 'Credit Card',
            'pan': 'PAN Number',
            'person': 'Personal Name',
            'org': 'Organization',
            'gpe': 'Location',
            'date': 'Date',
            'money': 'Financial Information',
            'cardinal': 'Number'
        };
        
        return typeMap[type.toLowerCase()] || type.toUpperCase();
    }
    
    // Get PII type icon
    getPIIIcon(type) {
        const iconMap = {
            'email': 'fas fa-envelope',
            'phone': 'fas fa-phone',
            'aadhar': 'fas fa-id-card',
            'passport': 'fas fa-passport',
            'credit_card': 'fas fa-credit-card',
            'pan': 'fas fa-id-badge',
            'person': 'fas fa-user',
            'org': 'fas fa-building',
            'gpe': 'fas fa-map-marker-alt',
            'date': 'fas fa-calendar',
            'money': 'fas fa-dollar-sign',
            'cardinal': 'fas fa-hashtag'
        };
        
        return iconMap[type.toLowerCase()] || 'fas fa-exclamation-triangle';
    }
    
    // Create PII badge element
    createPIIBadge(piiItem) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-warning text-dark me-2 mb-2';
        badge.innerHTML = `
            <i class="${this.getPIIIcon(piiItem.type)} me-1"></i>
            ${this.formatPIIType(piiItem.type)}: ${piiItem.value}
            <small>(${Math.round(piiItem.confidence * 100)}%)</small>
        `;
        return badge;
    }
    
    // Highlight PII in text
    highlightPII(text, piiItems) {
        let highlightedText = text;
        
        // Sort by length (longest first) to avoid overlapping replacements
        const sortedPII = piiItems.sort((a, b) => b.value.length - a.value.length);
        
        sortedPII.forEach(pii => {
            const regex = new RegExp(this.escapeRegex(pii.value), 'gi');
            highlightedText = highlightedText.replace(regex, 
                `<mark class="pii-highlight" data-type="${pii.type}">$&</mark>`);
        });
        
        return highlightedText;
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    // Generate privacy score based on PII detected
    calculatePrivacyScore(piiItems) {
        if (piiItems.length === 0) return 100;
        
        let score = 100;
        
        piiItems.forEach(pii => {
            // Deduct points based on PII type and confidence
            let deduction = 0;
            
            switch (pii.type.toLowerCase()) {
                case 'aadhar':
                case 'passport':
                case 'credit_card':
                case 'pan':
                    deduction = 25; // High sensitivity
                    break;
                case 'email':
                case 'phone':
                    deduction = 15; // Medium sensitivity
                    break;
                case 'person':
                case 'org':
                    deduction = 10; // Lower sensitivity
                    break;
                default:
                    deduction = 5;
            }
            
            score -= deduction * pii.confidence;
        });
        
        return Math.max(0, Math.round(score));
    }
    
    // Get privacy score color
    getPrivacyScoreColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }
    
    // Show privacy score
    displayPrivacyScore(score, container) {
        if (!container) return;
        
        const color = this.getPrivacyScoreColor(score);
        const icon = score >= 80 ? 'shield-alt' : score >= 60 ? 'exclamation-triangle' : 'times-circle';
        
        container.innerHTML = `
            <div class="privacy-score text-${color}">
                <i class="fas fa-${icon} me-2"></i>
                Privacy Score: ${score}/100
            </div>
        `;
    }
}

// Utility functions for PII detection UI
function showPIITooltip(element, piiType, confidence) {
    const tooltip = new bootstrap.Tooltip(element, {
        title: `${piiType.toUpperCase()} detected with ${Math.round(confidence * 100)}% confidence`,
        placement: 'top',
        trigger: 'hover'
    });
    
    element.addEventListener('mouseenter', () => tooltip.show());
    element.addEventListener('mouseleave', () => tooltip.hide());
}

function createPIISummary(piiItems) {
    const summary = document.createElement('div');
    summary.className = 'pii-summary';
    
    if (piiItems.length === 0) {
        summary.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-shield-alt me-2"></i>
                No PII detected in this message.
            </div>
        `;
        return summary;
    }
    
    const groupedPII = {};
    piiItems.forEach(pii => {
        if (!groupedPII[pii.type]) {
            groupedPII[pii.type] = [];
        }
        groupedPII[pii.type].push(pii);
    });
    
    let summaryHTML = `
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>${piiItems.length} PII item(s) detected:</strong>
        </div>
    `;
    
    Object.keys(groupedPII).forEach(type => {
        const items = groupedPII[type];
        summaryHTML += `
            <div class="pii-type-group mb-2">
                <strong>${window.piiDetector.formatPIIType(type)}:</strong>
                ${items.map(item => `<code>${item.value}</code>`).join(', ')}
            </div>
        `;
    });
    
    summary.innerHTML = summaryHTML;
    return summary;
}

// Initialize PII detector
document.addEventListener('DOMContentLoaded', function() {
    window.piiDetector = new PIIDetector();
    
    // Setup real-time detection for message input if it exists
    const messageInput = document.getElementById('message-input');
    const piiWarning = document.getElementById('pii-warning');
    
    if (messageInput && piiWarning) {
        window.piiDetector.setupRealTimeDetection(messageInput, piiWarning);
    }
    
    // Setup for story content if it exists
    const storyContent = document.getElementById('story-content');
    const storyWarning = document.getElementById('story-pii-warning');
    
    if (storyContent && storyWarning) {
        window.piiDetector.setupRealTimeDetection(storyContent, storyWarning);
    }
});
