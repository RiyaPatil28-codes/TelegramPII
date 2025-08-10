from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, storage, mongo
from pii_detector import pii_detector
import logging
from datetime import datetime
import base64
import random
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Bot response generator function
def generate_bot_response(bot_id, user_message):
    """Generate authentic human-like responses based on bot personality"""
    
    # Authentic friend personalities with varied responses
    responses = {
        'sarah': [
            "That's really interesting! What made you think about that?",
            "I love hearing your perspective on things like this.",
            "You know, that reminds me of something I was thinking about yesterday...",
            "That's such a thoughtful way to look at it!",
            "I've been wondering about similar things lately too.",
            "Your insights always make me see things differently.",
            "I really appreciate you sharing that with me.",
            "That's fascinating - tell me more about what you're thinking!"
        ],
        'alex': [
            "Wow, that sounds amazing! I can totally relate to that feeling.",
            "That's awesome! I had a similar experience when I was hiking last weekend.",
            "You're absolutely right about that. I love your energy!",
            "That's so cool! Have you ever tried exploring that further?",
            "I'm really excited to hear more about this!",
            "That sounds like quite an adventure! I'm a bit jealous honestly.",
            "Your enthusiasm is contagious! That sounds incredible.",
            "I wish I could experience that too - it sounds amazing!"
        ],
        'maya': [
            "Oh wow, that's such a beautiful story! Thank you for sharing.",
            "I love hearing about your experiences - they're always so genuine.",
            "That sounds like it was really meaningful for you.",
            "Your stories always make me feel more connected to the world.",
            "I'm so curious about the details - what happened next?",
            "That's the kind of story that stays with you, isn't it?",
            "I really appreciate you opening up about that.",
            "Stories like yours remind me why human connections matter so much."
        ],
        'david': [
            "That's a really thoughtful observation. I've been pondering similar things.",
            "You know what's fascinating about that? It reminds me of how stars form...",
            "That's the kind of deep thinking I really enjoy discussing.",
            "I love conversations that make me look at things from new angles.",
            "Your perspective is refreshing - most people don't think that deeply.",
            "That's exactly the type of genuine conversation I value.",
            "You always bring such depth to our talks.",
            "It's rare to find someone who thinks about things like that."
        ],
        'elena': [
            "That sounds delicious! Food has such a way of bringing people together.",
            "Oh, that reminds me of a dish I tried in Barcelona last year!",
            "I love how different cultures express themselves through food.",
            "That's such a wonderful way to experience new things!",
            "Food memories are some of my favorites - they're so vivid.",
            "I'm getting hungry just thinking about that!",
            "Have you ever tried making something similar at home?",
            "Cultural exchanges like that are what make life so rich!"
        ],
        'ryan': [
            "Dude, that's exactly what I've been thinking about lately!",
            "That sounds pretty epic! I can relate to that completely.",
            "You know what's cool about that? It reminds me of this game I played...",
            "That's awesome - I love when people are passionate about stuff.",
            "Honestly, that sounds way more interesting than what I did today!",
            "I really value friends who think about things like that.",
            "That's the kind of conversation that makes my day better.",
            "You always have such interesting thoughts - I appreciate that about you!"
        ]
    }
    
    # Get random authentic response based on bot personality
    bot_responses = responses.get(bot_id, responses['sarah'])
    return random.choice(bot_responses)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = storage.find_user_by_email(email)
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html')
        
        # Create new user
        user_data = {
            'username': fullname,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'profile': {
                'name': fullname,
                'avatar': 'user-default.png'
            }
        }
        if storage.save_user(email, user_data):
            # Get the inserted user to get the ObjectId
            user = storage.find_user_by_email(email)
            session['user_id'] = str(user['_id'])
            session['username'] = fullname
            session['user'] = {'name': fullname, 'email': email}
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = storage.find_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['user'] = {'name': user['username'], 'email': user['email']}
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

def get_cache_bust():
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d-%H%M%S')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user data from session
    user_data = session.get('user', {'name': session.get('username', 'User')})
    return render_template('dashboard.html', user=user_data, cache_bust=get_cache_bust())

@app.route('/debug')
def debug():
    return render_template('debug.html', cache_bust=get_cache_bust())

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bot_id = request.args.get('bot_id', 'sarah')
    
    # Get user data
    user_data = session.get('user', {'name': session.get('username', 'User')})
    
    # Bot personalities - authentic human-like friends
    bots = {
        'sarah': {
            'name': 'Sarah Chen',
            'title': 'Friend',
            'avatar': 'sarah-chen.png',
            'personality': 'movie_lover_deep_conversations',
            'description': 'Loves movies and deep conversations about life'
        },
        'alex': {
            'name': 'Alex Rodriguez', 
            'title': 'Friend',
            'avatar': 'alex-rodriguez.png',
            'personality': 'outdoor_adventurer',
            'description': 'Outdoor enthusiast who loves hiking and photography'
        },
        'maya': {
            'name': 'Maya Patel',
            'title': 'Friend', 
            'avatar': 'maya-patel.png',
            'personality': 'curious_storyteller',
            'description': 'Curious person who loves hearing peoples stories'
        },
        'david': {
            'name': 'David Kim',
            'title': 'Friend',
            'avatar': 'david-kim.png', 
            'personality': 'astronomy_enthusiast',
            'description': 'Astronomy lover who prefers real conversations'
        },
        'elena': {
            'name': 'Elena Kowalski',
            'title': 'Friend',
            'avatar': 'elena-kowalski.png',
            'personality': 'multicultural_foodie', 
            'description': 'World traveler and multicultural food enthusiast'
        },
        'ryan': {
            'name': 'Ryan O\'Connor',
            'title': 'Friend',
            'avatar': 'ryan-oconnor.png',
            'personality': 'gamer_music_lover',
            'description': 'Gamer and music enthusiast who values human connections'
        }
    }
    
    selected_bot = bots.get(bot_id, bots['sarah'])
    
    # Load previous messages from MongoDB
    messages = storage.get_user_messages(session['user_id'], bot_id)
    
    return render_template('chat.html', 
                         bot=selected_bot, 
                         user=user_data,
                         messages=messages,
                         cache_bust=get_cache_bust())

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
    bot_id = data.get('bot_id', 'sarah')
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Missing message content'}), 400
    
    # Analyze message for PII
    analysis = pii_detector.analyze_message(content)
    
    # Create message document for MongoDB
    message_data = {
        'sender_id': session['user_id'],
        'bot_id': bot_id,
        'content': content,
        'has_pii': analysis['has_pii'],
        'pii_detected': analysis['pii_detected'],
        'redacted_content': analysis.get('redacted_message', ''),
        'timestamp': datetime.utcnow(),
        'type': 'user'
    }
    
    # Save user message to MongoDB
    if storage.save_message(message_data):
        # Generate bot response based on personality
        bot_response = generate_bot_response(bot_id, content)
        
        # Save bot response
        bot_message_data = {
            'sender_id': bot_id,
            'bot_id': bot_id,
            'content': bot_response,
            'has_pii': False,
            'pii_detected': [],
            'timestamp': datetime.utcnow(),
            'type': 'bot'
        }
        storage.save_message(bot_message_data)
        
        return jsonify({
            'success': True,
            'user_message': message_data,
            'bot_response': bot_response,
            'has_pii': analysis['has_pii'],
            'pii_count': len(analysis['pii_detected'])
        })
    else:
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/get_messages/<bot_id>')
def get_messages(bot_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    messages = storage.get_user_messages(session['user_id'], bot_id)
    
    # Convert messages for JSON response
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'sender_id': str(msg.get('sender_id', '')),
            'bot_id': msg.get('bot_id', ''),
            'content': msg['content'],
            'has_pii': msg.get('has_pii', False),
            'pii_detected': msg.get('pii_detected', []),
            'timestamp': msg['timestamp'].isoformat() if msg.get('timestamp') else '',
            'type': msg.get('type', 'user'),
            'is_own_message': msg.get('type') == 'user'
        })
    
    return jsonify({'messages': formatted_messages})

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])}, {'password_hash': 0})
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        return render_template('profile.html', user=user)
    except Exception as e:
        logging.error(f"Error loading profile: {e}")
        session.clear()
        return redirect(url_for('login'))

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

@app.route('/api/send-message', methods=['POST'])
def api_send_message():
    """API endpoint for sending messages with PII analysis"""
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '').strip()
    bot_id = data.get('bot_id', 'ai-assistant')
    send_redacted = data.get('send_redacted', False)
    
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    try:
        # Comprehensive PII analysis using all detection methods
        pii_analysis = pii_detector.analyze_message(message)
        
        # Determine final message to store
        final_message = message
        if send_redacted and pii_analysis['has_pii']:
            final_message = pii_analysis['redacted_message']
        
        # Generate bot response
        bot_response = generate_bot_response(bot_id, message)
        
        # Store messages in MongoDB
        user_id = session.get('user_id')
        timestamp = datetime.utcnow()
        
        # Store user message
        user_message_doc = {
            'user_id': ObjectId(user_id),
            'bot_id': bot_id,
            'message': final_message,
            'original_message': message if send_redacted else final_message,
            'message_type': 'user',
            'pii_analysis': pii_analysis,
            'redacted': send_redacted,
            'timestamp': timestamp
        }
        mongo.db.messages.insert_one(user_message_doc)
        
        # Store bot response
        bot_message_doc = {
            'user_id': ObjectId(user_id),
            'bot_id': bot_id,
            'message': bot_response,
            'message_type': 'bot',
            'timestamp': timestamp
        }
        mongo.db.messages.insert_one(bot_message_doc)
        
        return jsonify({
            'success': True,
            'bot_response': bot_response,
            'pii_analysis': pii_analysis,
            'message_stored': final_message
        })
        
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
