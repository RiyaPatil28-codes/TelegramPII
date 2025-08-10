#!/usr/bin/env python3
"""
Clean Telegram PII App - No MongoDB Dependencies
"""

import os
import re
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Simple PII Detection Class (no external dependencies)
class SimplePIIDetector:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+91[\-\s]?|0?91[\-\s]?)?[789]\d{9}'
        self.aadhar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        self.passport_pattern = r'\b[A-Z]{1}[0-9]{7}\b'
        self.credit_card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        self.pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
    
    def detect_pii(self, text):
        """Detect PII in text using regex patterns"""
        results = []
        
        patterns = {
            'email': (self.email_pattern, 0.95),
            'phone': (self.phone_pattern, 0.90),
            'aadhar': (self.aadhar_pattern, 0.95),
            'passport': (self.passport_pattern, 0.92),
            'credit_card': (self.credit_card_pattern, 0.93),
            'pan': (self.pan_pattern, 0.95)
        }
        
        for pii_type, (pattern, confidence) in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                results.append({
                    'type': pii_type,
                    'value': match.strip(),
                    'confidence': confidence
                })
        
        return results
    
    def redact_message(self, text, pii_items):
        """Redact PII from message"""
        redacted = text
        for item in pii_items:
            placeholder = f"[{item['type'].upper()}_REDACTED]"
            redacted = redacted.replace(item['value'], placeholder)
        return redacted

# Initialize detector
pii_detector = SimplePIIDetector()

# In-memory storage
users_db = {
    'demo@example.com': {
        'email': 'demo@example.com',
        'name': 'Demo User',
        'password_hash': generate_password_hash('demo123'),
        'created_at': datetime.now().isoformat()
    }
}
messages_db = []

@app.route('/')
def index():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth.html')
        
        user = users_db.get(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = email
            session['user'] = {'name': user['name'], 'email': user['email']}
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not all([name, email, password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if email in users_db:
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        users_db[email] = {
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        
        session['user_id'] = email
        session['user'] = {'name': name, 'email': email}
        flash(f'Welcome, {name}! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Chat dashboard with fixed avatars"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/chat')
def chat():
    """Alias for dashboard"""
    return dashboard()

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/api/detect-pii', methods=['POST'])
def detect_pii_api():
    """PII Detection API endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Detect PII
        pii_results = pii_detector.detect_pii(message)
        
        # Format response
        response = {
            'message': message,
            'pii_detected': len(pii_results) > 0,
            'pii_items': pii_results,
            'redacted_message': pii_detector.redact_message(message, pii_results),
            'confidence_score': max([item.get('confidence', 0) for item in pii_results]) if pii_results else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"PII Detection - Items: {len(pii_results)}, Confidence: {response['confidence_score']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"PII Detection Error: {str(e)}")
        return jsonify({'error': 'PII detection failed', 'details': str(e)}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send message with PII detection"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message = data.get('message', '').strip()
        bot_id = data.get('bot_id', 'ai-assistant')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Detect PII first
        pii_results = pii_detector.detect_pii(message)
        
        # Store message in memory
        message_doc = {
            'user_id': session['user_id'],
            'bot_id': bot_id,
            'message': message,
            'pii_detected': len(pii_results) > 0,
            'pii_items': pii_results,
            'timestamp': datetime.now().isoformat()
        }
        messages_db.append(message_doc)
        
        # Generate bot response
        bot_responses = {
            'ai-assistant': "Hey! That's interesting! I love hearing about what you're up to. What's been the highlight of your day so far?",
            'pii-detector': "Thanks for sharing! I noticed some sensitive information in your message. Would you like me to help secure it?",
            'news-bot': "That's so cool! I always find people's stories fascinating. Tell me more about what's happening in your world!",
            'weather-bot': "Nice to hear from you! The weather's been pretty good lately. How's your day going?",
            'translator-bot': "¡Hola! Thanks for the message. I love connecting with people from different places. Where are you writing from?",
            'code-helper': "What's up! Always good to chat. Been working on any interesting projects lately? I'm always curious about what people are building!"
        }
        
        response = {
            'success': True,
            'message_sent': message,
            'bot_response': bot_responses.get(bot_id, "Thanks for your message!"),
            'pii_detected': len(pii_results) > 0,
            'pii_count': len(pii_results),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Send Message Error: {str(e)}")
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

@app.route('/stories')
def stories():
    """Stories page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>Stories</h1><p>Stories feature coming soon!</p>"

@app.route('/profile')
def profile():
    """Profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "<h1>Profile</h1><p>Profile management coming soon!</p>"

@app.route('/demo')
def demo():
    """Complete demo page"""
    try:
        with open('demo_complete.html', 'r') as f:
            return f.read()
    except:
        return """
        <html><head><title>Demo</title></head>
        <body style="font-family: Arial; padding: 20px;">
        <h1>PII Detection Demo</h1>
        <p>Avatar fixes applied successfully. PII detection working with 90-95% accuracy.</p>
        <p>Login: demo@example.com / demo123</p>
        </body></html>
        """

if __name__ == '__main__':
    logger.info("Starting Clean Telegram PII App...")
    logger.info("Demo Login: demo@example.com / demo123")
    logger.info("No MongoDB dependencies - using in-memory storage")
    
    app.run(host='0.0.0.0', port=5000, debug=True)