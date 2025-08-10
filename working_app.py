#!/usr/bin/env python3
"""
Working Telegram PII Detection App
Bypasses MongoDB dependency conflicts by using in-memory storage
"""

import os
import re
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Import our working PII detector
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pii_detector import PIIDetector

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# In-memory storage (replaces MongoDB for demo)
users_db = {}
messages_db = []
sessions_db = {}

# Initialize PII Detector
pii_detector = PIIDetector()

# Demo users
users_db['demo@example.com'] = {
    'email': 'demo@example.com',
    'name': 'Demo User',
    'password_hash': generate_password_hash('demo123'),
    'created_at': datetime.now().isoformat()
}

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
        
        # Create new user
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
        
        # Use our working PII detector
        pii_results = pii_detector.detect_all_pii(message)
        
        # Format response
        response = {
            'message': message,
            'pii_detected': len(pii_results) > 0,
            'pii_items': pii_results,
            'redacted_message': pii_detector.redact_pii(message, pii_results),
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
        pii_results = pii_detector.detect_all_pii(message)
        
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

@app.route('/test-pii')
def test_pii():
    """Test PII detection page"""
    return render_template('test_pii.html')

@app.route('/demo')
def demo():
    """Complete demo page"""
    return render_template('demo_complete.html')

if __name__ == '__main__':
    logger.info("Starting Telegram PII Detection App...")
    logger.info("Demo Login: demo@example.com / demo123")
    logger.info("Features: Real-time PII detection, Fixed avatars, Secure messaging")
    
    app.run(host='0.0.0.0', port=5000, debug=True)