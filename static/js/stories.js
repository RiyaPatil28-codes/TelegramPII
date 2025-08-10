// Stories functionality for Telegram PII application
class StoriesManager {
    constructor() {
        this.currentStoryIndex = 0;
        this.stories = [];
        this.storyViewerModal = null;
        this.createStoryModal = null;
        this.storyProgressInterval = null;
        this.storyDuration = 10000; // 10 seconds per story
        
        this.initializeModals();
        this.initializeEventListeners();
        this.loadStories();
    }
    
    initializeModals() {
        // Initialize Bootstrap modals
        const createModalElement = document.getElementById('createStoryModal');
        const viewerModalElement = document.getElementById('storyViewerModal');
        
        if (createModalElement) {
            this.createStoryModal = new bootstrap.Modal(createModalElement);
        }
        
        if (viewerModalElement) {
            this.storyViewerModal = new bootstrap.Modal(viewerModalElement);
        }
    }
    
    initializeEventListeners() {
        // Story content textarea event listeners
        const storyContent = document.getElementById('story-content');
        if (storyContent) {
            storyContent.addEventListener('input', this.handleStoryContentChange.bind(this));
            storyContent.addEventListener('paste', this.handleStoryContentChange.bind(this));
        }
        
        // Story media upload
        const storyMedia = document.getElementById('story-media');
        if (storyMedia) {
            storyMedia.addEventListener('change', this.handleMediaUpload.bind(this));
        }
        
        // Preview and publish buttons
        const previewBtn = document.getElementById('preview-story-btn');
        const publishBtn = document.getElementById('publish-story-btn');
        
        if (previewBtn) {
            previewBtn.addEventListener('click', this.previewStory.bind(this));
        }
        
        if (publishBtn) {
            publishBtn.addEventListener('click', this.publishStory.bind(this));
        }
        
        // Story card click handlers
        this.setupStoryCardListeners();
        
        // Modal event listeners
        if (this.createStoryModal) {
            document.getElementById('createStoryModal').addEventListener('hidden.bs.modal', this.resetCreateStoryForm.bind(this));
        }
        
        // Keyboard navigation for story viewer
        document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
    }
    
    setupStoryCardListeners() {
        const storyCards = document.querySelectorAll('.story-card');
        storyCards.forEach((card, index) => {
            card.addEventListener('click', () => {
                this.openStoryViewer(index);
            });
        });
        
        // Reply button handlers
        const replyButtons = document.querySelectorAll('.story-reply-btn');
        replyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleStoryReply(btn);
            });
        });
    }
    
    handleStoryContentChange(event) {
        const content = event.target.value;
        const maxLength = 500;
        const remaining = maxLength - content.length;
        
        // Update character counter
        this.updateCharacterCounter(remaining);
        
        // Real-time PII detection
        if (content.trim().length > 2) {
            this.debounceStoryPIICheck(content);
        } else {
            this.hideStoryPIIWarning();
        }
        
        // Enable/disable publish button
        const publishBtn = document.getElementById('publish-story-btn');
        if (publishBtn) {
            publishBtn.disabled = !content.trim() || remaining < 0;
        }
    }
    
    debounceStoryPIICheck(content) {
        clearTimeout(this.piiCheckTimeout);
        this.piiCheckTimeout = setTimeout(() => {
            this.checkStoryPII(content);
        }, 800);
    }
    
    async checkStoryPII(content) {
        try {
            const response = await fetch('/api/analyze_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: content })
            });
            
            const data = await response.json();
            
            if (data.has_pii) {
                this.showStoryPIIWarning(data);
            } else {
                this.hideStoryPIIWarning();
            }
        } catch (error) {
            console.error('Error checking story PII:', error);
        }
    }
    
    showStoryPIIWarning(analysisData) {
        const warning = document.getElementById('story-pii-warning');
        const details = document.getElementById('story-pii-details');
        
        if (!warning || !details) return;
        
        // Create PII badges
        const piiList = analysisData.pii_detected.map(pii => {
            const icon = this.getPIIIcon(pii.type);
            return `<span class="badge bg-warning text-dark me-2 mb-1">
                <i class="${icon} me-1"></i>
                ${pii.type.toUpperCase()}: ${pii.value}
                <small>(${Math.round(pii.confidence * 100)}%)</small>
            </span>`;
        }).join('');
        
        details.innerHTML = `
            <div class="mt-2">
                <strong>Detected PII:</strong><br>
                ${piiList}
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    Stories are visible to all your contacts. Consider removing personal information.
                </small>
            </div>
        `;
        
        warning.classList.remove('d-none');
        
        // Disable publish button when PII is detected
        const publishBtn = document.getElementById('publish-story-btn');
        if (publishBtn) {
            publishBtn.disabled = true;
            publishBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Cannot Publish (Contains PII)';
        }
    }
    
    hideStoryPIIWarning() {
        const warning = document.getElementById('story-pii-warning');
        if (warning) {
            warning.classList.add('d-none');
        }
        
        // Re-enable publish button
        const publishBtn = document.getElementById('publish-story-btn');
        const storyContent = document.getElementById('story-content');
        if (publishBtn && storyContent) {
            publishBtn.disabled = !storyContent.value.trim();
            publishBtn.innerHTML = '<i class="fas fa-share"></i> Publish Story';
        }
    }
    
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
    
    updateCharacterCounter(remaining) {
        let counterElement = document.getElementById('character-counter');
        
        if (!counterElement) {
            // Create character counter if it doesn't exist
            const formText = document.querySelector('#story-content + .form-text');
            if (formText) {
                counterElement = document.createElement('div');
                counterElement.id = 'character-counter';
                counterElement.className = 'character-counter mt-1';
                formText.parentNode.insertBefore(counterElement, formText.nextSibling);
            }
        }
        
        if (counterElement) {
            const color = remaining < 0 ? 'text-danger' : remaining < 50 ? 'text-warning' : 'text-muted';
            counterElement.innerHTML = `<small class="${color}">${remaining} characters remaining</small>`;
        }
    }
    
    handleMediaUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/webm'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid image or video file.');
            event.target.value = '';
            return;
        }
        
        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showError('File size must be less than 10MB.');
            event.target.value = '';
            return;
        }
        
        // Show preview
        this.showMediaPreview(file);
    }
    
    showMediaPreview(file) {
        const preview = document.getElementById('media-preview') || this.createMediaPreview();
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const isVideo = file.type.startsWith('video/');
            preview.innerHTML = `
                <div class="media-preview-container">
                    <h6>Media Preview:</h6>
                    ${isVideo ? 
                        `<video controls class="img-fluid rounded" style="max-height: 200px;">
                            <source src="${e.target.result}" type="${file.type}">
                        </video>` :
                        `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px;" alt="Preview">`
                    }
                    <button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            `;
            preview.classList.remove('d-none');
        };
        
        reader.readAsDataURL(file);
    }
    
    createMediaPreview() {
        const preview = document.createElement('div');
        preview.id = 'media-preview';
        preview.className = 'd-none mb-3';
        
        const storyForm = document.getElementById('create-story-form');
        if (storyForm) {
            storyForm.appendChild(preview);
        }
        
        return preview;
    }
    
    previewStory() {
        const content = document.getElementById('story-content').value.trim();
        const preview = document.getElementById('story-preview');
        const previewContent = document.getElementById('preview-content');
        
        if (!content) {
            this.showError('Please enter story content to preview.');
            return;
        }
        
        if (preview && previewContent) {
            // Create story preview
            previewContent.innerHTML = `
                <div class="story-preview-card">
                    <div class="story-preview-header">
                        <div class="d-flex align-items-center">
                            <div class="story-avatar me-2">
                                <i class="fas fa-user-circle"></i>
                            </div>
                            <div>
                                <h6 class="mb-0">Your Story</h6>
                                <small class="text-muted">Now</small>
                            </div>
                        </div>
                    </div>
                    <div class="story-preview-content">
                        <p class="mb-0">${this.escapeHtml(content)}</p>
                    </div>
                </div>
            `;
            
            preview.classList.remove('d-none');
            
            // Scroll to preview
            preview.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    async publishStory() {
        const content = document.getElementById('story-content').value.trim();
        
        if (!content) {
            this.showError('Please enter story content.');
            return;
        }
        
        // Check for PII one more time before publishing
        try {
            const analysisResponse = await fetch('/api/analyze_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: content })
            });
            
            const analysisData = await analysisResponse.json();
            
            if (analysisData.has_pii) {
                this.showError('Cannot publish story: Contains personally identifiable information. Please remove sensitive data before publishing.');
                return;
            }
            
            // Disable publish button and show loading
            const publishBtn = document.getElementById('publish-story-btn');
            const originalText = publishBtn.innerHTML;
            publishBtn.disabled = true;
            publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publishing...';
            
            // Publish story
            const response = await fetch('/api/create_story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: content })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Story published successfully! It will be visible for 24 hours.');
                
                // Close modal and refresh page
                if (this.createStoryModal) {
                    this.createStoryModal.hide();
                }
                
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                this.showError(data.error || 'Failed to publish story.');
            }
            
        } catch (error) {
            console.error('Error publishing story:', error);
            this.showError('An error occurred while publishing the story.');
        } finally {
            // Re-enable publish button
            const publishBtn = document.getElementById('publish-story-btn');
            if (publishBtn) {
                publishBtn.disabled = false;
                publishBtn.innerHTML = '<i class="fas fa-share"></i> Publish Story';
            }
        }
    }
    
    openStoryViewer(storyIndex) {
        if (!this.storyViewerModal) return;
        
        this.currentStoryIndex = storyIndex;
        this.loadStoryInViewer(storyIndex);
        this.storyViewerModal.show();
        this.startStoryProgress();
    }
    
    loadStoryInViewer(index) {
        const storyCards = document.querySelectorAll('.story-card');
        if (index >= storyCards.length) return;
        
        const storyCard = storyCards[index];
        const storyContent = storyCard.querySelector('.story-text p')?.textContent || '';
        const storyMedia = storyCard.querySelector('.story-media img')?.src || '';
        const username = storyCard.querySelector('.story-username')?.textContent || '';
        const timestamp = storyCard.querySelector('.story-time')?.textContent || '';
        
        const viewerContent = document.querySelector('.story-viewer-content');
        if (viewerContent) {
            viewerContent.innerHTML = `
                <div class="story-viewer-header mb-3">
                    <div class="d-flex align-items-center text-white">
                        <div class="story-avatar me-2">
                            <i class="fas fa-user-circle fa-2x"></i>
                        </div>
                        <div>
                            <h5 class="mb-0">${this.escapeHtml(username)}</h5>
                            <small>${this.escapeHtml(timestamp)}</small>
                        </div>
                    </div>
                </div>
                
                ${storyMedia ? `
                    <div class="story-media mb-3">
                        <img src="${storyMedia}" class="img-fluid rounded" alt="Story media">
                    </div>
                ` : ''}
                
                ${storyContent ? `
                    <div class="story-text">
                        <p class="text-white fs-5">${this.escapeHtml(storyContent)}</p>
                    </div>
                ` : ''}
            `;
        }
    }
    
    startStoryProgress() {
        const progressBar = document.querySelector('.story-progress .progress-bar');
        if (!progressBar) return;
        
        progressBar.style.width = '0%';
        progressBar.style.transition = `width ${this.storyDuration}ms linear`;
        
        // Start progress animation
        setTimeout(() => {
            progressBar.style.width = '100%';
        }, 100);
        
        // Auto-advance to next story
        this.storyProgressInterval = setTimeout(() => {
            this.nextStory();
        }, this.storyDuration);
    }
    
    nextStory() {
        const storyCards = document.querySelectorAll('.story-card');
        
        if (this.currentStoryIndex < storyCards.length - 1) {
            this.currentStoryIndex++;
            this.loadStoryInViewer(this.currentStoryIndex);
            this.startStoryProgress();
        } else {
            // End of stories, close viewer
            if (this.storyViewerModal) {
                this.storyViewerModal.hide();
            }
        }
    }
    
    previousStory() {
        if (this.currentStoryIndex > 0) {
            this.currentStoryIndex--;
            this.loadStoryInViewer(this.currentStoryIndex);
            this.startStoryProgress();
        }
    }
    
    handleKeyboardNavigation(event) {
        if (!this.storyViewerModal || !document.body.classList.contains('modal-open')) return;
        
        switch (event.key) {
            case 'ArrowRight':
            case ' ':
                event.preventDefault();
                this.nextStory();
                break;
            case 'ArrowLeft':
                event.preventDefault();
                this.previousStory();
                break;
            case 'Escape':
                if (this.storyViewerModal) {
                    this.storyViewerModal.hide();
                }
                break;
        }
    }
    
    handleStoryReply(button) {
        const storyCard = button.closest('.story-card');
        const username = storyCard.querySelector('.story-username')?.textContent || '';
        
        // Simple reply implementation - could be enhanced
        const replyMessage = prompt(`Reply to ${username}'s story:`);
        if (replyMessage && replyMessage.trim()) {
            this.showSuccess(`Reply sent to ${username}!`);
            // In a real implementation, this would send an API request
        }
    }
    
    resetCreateStoryForm() {
        const form = document.getElementById('create-story-form');
        if (form) {
            form.reset();
        }
        
        // Reset character counter
        const counter = document.getElementById('character-counter');
        if (counter) {
            counter.innerHTML = '<small class="text-muted">500 characters remaining</small>';
        }
        
        // Hide preview and warnings
        const preview = document.getElementById('story-preview');
        const warning = document.getElementById('story-pii-warning');
        const mediaPreview = document.getElementById('media-preview');
        
        if (preview) preview.classList.add('d-none');
        if (warning) warning.classList.add('d-none');
        if (mediaPreview) mediaPreview.remove();
        
        // Reset publish button
        const publishBtn = document.getElementById('publish-story-btn');
        if (publishBtn) {
            publishBtn.disabled = true;
            publishBtn.innerHTML = '<i class="fas fa-share"></i> Publish Story';
        }
    }
    
    loadStories() {
        // Stories are already loaded server-side, but we can fetch updates here if needed
        console.log('Stories loaded from server-side rendering');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.stories-container') || document.querySelector('main');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
    
    showSuccess(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.stories-container') || document.querySelector('main');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            
            // Auto-dismiss after 3 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 3000);
        }
    }
}

// Initialize stories manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.storiesManager = new StoriesManager();
});

// Add story viewer modal event listeners
document.addEventListener('DOMContentLoaded', function() {
    const storyViewerModal = document.getElementById('storyViewerModal');
    
    if (storyViewerModal) {
        storyViewerModal.addEventListener('hidden.bs.modal', function() {
            // Clear progress interval when modal is closed
            if (window.storiesManager && window.storiesManager.storyProgressInterval) {
                clearTimeout(window.storiesManager.storyProgressInterval);
            }
        });
        
        // Add click handlers for story navigation
        storyViewerModal.addEventListener('click', function(e) {
            const modalBody = e.target.closest('.story-viewer-body');
            if (!modalBody) return;
            
            const rect = modalBody.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const modalWidth = rect.width;
            
            // Click on left side = previous story, right side = next story
            if (clickX < modalWidth / 2) {
                if (window.storiesManager) {
                    window.storiesManager.previousStory();
                }
            } else {
                if (window.storiesManager) {
                    window.storiesManager.nextStory();
                }
            }
        });
    }
});
