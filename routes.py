from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, mongo
from models import User, Message, Story
from pii_detector import pii_detector
import logging
from bson import ObjectId
from datetime import datetime
import base64

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('auth.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, password=password)
        if user.save():
            session['user_id'] = str(user._id)
            session['username'] = username
            flash('Registration successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.find_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = str(user._id)
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's contacts (for simplicity, get all users except current user)
    current_user_id = ObjectId(session['user_id'])
    contacts = list(mongo.db.users.find({'_id': {'$ne': current_user_id}}, {'password_hash': 0}))
    
    return render_template('chat.html', contacts=contacts)

@app.route('/api/analyze_message', methods=['POST'])
def analyze_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    message_text = data.get('message', '')
    
    if not message_text.strip():
        return jsonify({'error': 'Empty message'}), 400
    
    # Analyze message for PII
    analysis = pii_detector.analyze_message(message_text)
    
    return jsonify({
        'has_pii': analysis['has_pii'],
        'pii_detected': analysis['pii_detected'],
        'redacted_message': analysis['redacted_message'],
        'confidence_score': analysis['confidence_score']
    })

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    use_redacted = data.get('use_redacted', False)
    redacted_content = data.get('redacted_content')
    
    if not recipient_id or not content:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Analyze message for PII
    analysis = pii_detector.analyze_message(content)
    
    # Create message object
    message = Message(
        sender_id=session['user_id'],
        recipient_id=recipient_id,
        content=redacted_content if use_redacted and redacted_content else content,
        has_pii=analysis['has_pii'],
        redacted_content=redacted_content if analysis['has_pii'] else None
    )
    message.pii_detected = analysis['pii_detected']
    
    if message.save():
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'has_pii': analysis['has_pii'],
            'pii_count': len(analysis['pii_detected'])
        })
    else:
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/get_messages/<recipient_id>')
def get_messages(recipient_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    messages = Message.get_conversation(session['user_id'], recipient_id)
    
    # Convert ObjectId to string and format for JSON
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'sender_id': str(msg['sender_id']),
            'recipient_id': str(msg['recipient_id']),
            'content': msg['content'],
            'has_pii': msg.get('has_pii', False),
            'pii_detected': msg.get('pii_detected', []),
            'timestamp': msg['timestamp'].isoformat(),
            'is_own_message': str(msg['sender_id']) == session['user_id']
        })
    
    return jsonify({'messages': formatted_messages})

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.find_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    try:
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'username': username}}
        )
        session['username'] = username
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        logging.error(f"Error updating profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/stories')
def stories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get active stories
    active_stories = Story.get_active_stories(session['user_id'])
    
    # Format stories for display
    formatted_stories = []
    for story in active_stories:
        user = User.find_by_id(story['user_id'])
        if user:
            formatted_stories.append({
                'id': str(story['_id']),
                'username': user.username,
                'content': story['content'],
                'media_url': story.get('media_url'),
                'created_at': story['created_at'],
                'is_own_story': str(story['user_id']) == session['user_id']
            })
    
    return render_template('stories.html', stories=formatted_stories)

@app.route('/api/create_story', methods=['POST'])
def create_story():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    content = data.get('content', '')
    
    if not content.strip():
        return jsonify({'error': 'Story content is required'}), 400
    
    # Analyze story content for PII
    analysis = pii_detector.analyze_message(content)
    
    if analysis['has_pii']:
        return jsonify({
            'error': 'Story contains PII',
            'has_pii': True,
            'pii_detected': analysis['pii_detected'],
            'redacted_content': analysis['redacted_message']
        }), 400
    
    story = Story(user_id=session['user_id'], content=content)
    if story.save():
        return jsonify({'success': True, 'message': 'Story created successfully'})
    else:
        return jsonify({'error': 'Failed to create story'}), 500

@app.route('/api/contacts')
def get_contacts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_user_id = ObjectId(session['user_id'])
    contacts = list(mongo.db.users.find(
        {'_id': {'$ne': current_user_id}}, 
        {'username': 1, 'email': 1, 'profile_picture': 1}
    ))
    
    # Format contacts for JSON response
    formatted_contacts = []
    for contact in contacts:
        formatted_contacts.append({
            'id': str(contact['_id']),
            'username': contact['username'],
            'email': contact['email'],
            'profile_picture': contact.get('profile_picture')
        })
    
    return jsonify({'contacts': formatted_contacts})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
