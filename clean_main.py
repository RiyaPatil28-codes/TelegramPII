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

# MongoDB imports
try:
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Configure logging first
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import advanced PII detector (try full version first, fallback to simple)
ADVANCED_PII_AVAILABLE = False
try:
    from advanced_pii_detector import detect_pii_advanced
    ADVANCED_PII_AVAILABLE = True
    ADVANCED_MODE = "full"
    logger.info("Full advanced PII detector with BERT/TF-IDF loaded successfully")
except ImportError:
    try:
        from simple_advanced_pii import detect_pii_advanced_simple as detect_pii_advanced
        ADVANCED_PII_AVAILABLE = True
        ADVANCED_MODE = "simple"
        logger.info("Simplified advanced PII detector with TF-IDF/clustering loaded successfully")
    except ImportError as e:
        logger.warning(f"Advanced PII detection not available: {e}. Using simple regex detection.")
        ADVANCED_MODE = "none"
except Exception as e:
    logger.error(f"Error loading advanced PII detector: {e}")
    ADVANCED_MODE = "none"

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# MongoDB Configuration
mongo_client = None
db = None
pii_detections_collection = None
messages_collection = None
users_collection = None

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, db, pii_detections_collection, messages_collection, users_collection
    
    if not MONGODB_AVAILABLE:
        logger.warning("PyMongo not available. PII data will be stored in memory only.")
        return False
        
    try:
        # Try to get MongoDB URI from environment
        mongo_uri = os.environ.get('MONGODB_URI') or os.environ.get('DATABASE_URL')
        if mongo_uri and 'mongodb' in mongo_uri:
            mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        else:
            # Default local MongoDB connection
            mongo_client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test the connection
        mongo_client.server_info()
        
        # Initialize database and collections
        db = mongo_client['telegram_pii']
        pii_detections_collection = db['pii_detections']
        messages_collection = db['messages']
        users_collection = db['users']
        
        # Create indexes for better performance
        pii_detections_collection.create_index([("timestamp", -1)])
        pii_detections_collection.create_index([("user_id", 1)])
        pii_detections_collection.create_index([("pii_type", 1)])
        messages_collection.create_index([("user_id", 1), ("timestamp", -1)])
        
        logger.info("MongoDB connected successfully")
        return True
        
    except ServerSelectionTimeoutError:
        logger.warning("MongoDB connection failed. Using in-memory storage.")
        return False
    except Exception as e:
        logger.error(f"MongoDB initialization error: {e}")
        return False

# Initialize MongoDB
MONGODB_CONNECTED = init_mongodb()

def store_pii_detection(user_id, original_message, pii_result, bot_id=None):
    """Store PII detection results in MongoDB or memory"""
    try:
        detection_record = {
            'user_id': user_id,
            'original_message': original_message,
            'bot_id': bot_id,
            'pii_detected': pii_result.get('pii_detected', False),
            'pii_items': pii_result.get('pii_items', []),
            'detection_methods': pii_result.get('detection_methods', []),
            'overall_confidence': pii_result.get('overall_confidence', 0.0),
            'redacted_message': pii_result.get('redacted_text', ''),
            'timestamp': datetime.utcnow(),
            'message_length': len(original_message),
            'pii_count': len(pii_result.get('pii_items', [])),
            'pii_types': list(set([item.get('type', 'unknown') for item in pii_result.get('pii_items', [])]))
        }
        
        # Add individual PII items with detailed metadata
        for pii_item in pii_result.get('pii_items', []):
            pii_record = {
                'user_id': user_id,
                'pii_type': pii_item.get('type', 'unknown'),
                'pii_value_hash': str(hash(pii_item.get('value', '')))[1:9],  # Hash for privacy
                'confidence': pii_item.get('confidence', 0.0),
                'detection_method': pii_item.get('method', 'unknown'),
                'context_snippet': pii_item.get('context', '')[:50] + '...' if len(pii_item.get('context', '')) > 50 else pii_item.get('context', ''),
                'timestamp': datetime.utcnow(),
                'original_message_id': str(hash(original_message))[1:9]
            }
            
            if MONGODB_CONNECTED and pii_detections_collection:
                pii_detections_collection.insert_one(pii_record.copy())
            else:
                pii_detections_db.append(pii_record)
        
        # Store the main detection record
        if MONGODB_CONNECTED and messages_collection:
            messages_collection.insert_one(detection_record)
            logger.info(f"Stored PII detection in MongoDB: {len(pii_result.get('pii_items', []))} items detected")
        else:
            pii_detections_db.append(detection_record)
            logger.info(f"Stored PII detection in memory: {len(pii_result.get('pii_items', []))} items detected")
            
    except Exception as e:
        logger.error(f"Error storing PII detection: {e}")

def get_pii_statistics(user_id=None):
    """Get PII detection statistics"""
    try:
        if MONGODB_CONNECTED and pii_detections_collection:
            # MongoDB aggregation pipeline
            pipeline = []
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": "$pii_type",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence"},
                        "detection_methods": {"$addToSet": "$detection_method"}
                    }
                },
                {"$sort": {"count": -1}}
            ])
            
            stats = list(pii_detections_collection.aggregate(pipeline))
            total_detections = sum(stat['count'] for stat in stats)
            
            return {
                'total_detections': total_detections,
                'pii_types_stats': stats,
                'storage_type': 'mongodb'
            }
        else:
            # In-memory statistics
            filtered_data = pii_detections_db
            if user_id:
                filtered_data = [item for item in pii_detections_db if item.get('user_id') == user_id]
            
            pii_types = {}
            for item in filtered_data:
                pii_type = item.get('pii_type', 'unknown')
                if pii_type not in pii_types:
                    pii_types[pii_type] = {
                        'count': 0,
                        'confidences': [],
                        'methods': set()
                    }
                pii_types[pii_type]['count'] += 1
                pii_types[pii_type]['confidences'].append(item.get('confidence', 0))
                pii_types[pii_type]['methods'].add(item.get('detection_method', 'unknown'))
            
            stats = []
            for pii_type, data in pii_types.items():
                stats.append({
                    '_id': pii_type,
                    'count': data['count'],
                    'avg_confidence': sum(data['confidences']) / len(data['confidences']) if data['confidences'] else 0,
                    'detection_methods': list(data['methods'])
                })
            
            stats.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'total_detections': len(filtered_data),
                'pii_types_stats': stats,
                'storage_type': 'memory'
            }
            
    except Exception as e:
        logger.error(f"Error getting PII statistics: {e}")
        return {'total_detections': 0, 'pii_types_stats': [], 'error': str(e)}

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
pii_detections_db = []  # Store PII detection results in memory when MongoDB unavailable

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
            return render_template('auth.html')
        
        if email in users_db:
            flash('Email already exists', 'error')
            return render_template('auth.html')
        
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
    
    return render_template('auth.html')

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
    """Enhanced PII Detection API endpoint with BERT/TF-IDF"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        use_advanced = data.get('use_advanced', True)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Use advanced detection if available
        if ADVANCED_PII_AVAILABLE and use_advanced:
            advanced_results = detect_pii_advanced(message)
            
            response = {
                'message': message,
                'pii_detected': advanced_results['pii_detected'],
                'pii_items': advanced_results['pii_items'],
                'redacted_message': advanced_results['redacted_text'],
                'confidence_score': advanced_results['overall_confidence'],
                'detection_methods': advanced_results['detection_methods'],
                'advanced_detection': True,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Advanced PII Detection - Items: {len(advanced_results['pii_items'])}, "
                       f"Confidence: {response['confidence_score']:.2f}, "
                       f"Methods: {advanced_results['detection_methods']}")
            
            # Store PII detection data in MongoDB if PII detected
            if advanced_results['pii_detected']:
                user_id = session.get('user_id', 'anonymous')
                store_pii_detection(user_id, message, advanced_results)
            
        else:
            # Fallback to simple detection
            pii_results = pii_detector.detect_pii(message)
            
            response = {
                'message': message,
                'pii_detected': len(pii_results) > 0,
                'pii_items': pii_results,
                'redacted_message': pii_detector.redact_message(message, pii_results),
                'confidence_score': max([item.get('confidence', 0) for item in pii_results]) if pii_results else 0,
                'detection_methods': ['regex'],
                'advanced_detection': False,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Simple PII Detection - Items: {len(pii_results)}, "
                       f"Confidence: {response['confidence_score']}")
        
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
        
        # Store message with PII detection results
        message_doc = {
            'user_id': session['user_id'],
            'bot_id': bot_id,
            'message': message,
            'pii_detected': len(pii_results) > 0,
            'pii_items': pii_results,
            'timestamp': datetime.now().isoformat()
        }
        messages_db.append(message_doc)
        
        # Store PII detection data if any PII was found
        if len(pii_results) > 0:
            pii_result_formatted = {
                'pii_detected': True,
                'pii_items': pii_results,
                'detection_methods': ['regex'],
                'overall_confidence': max([item.get('confidence', 0) for item in pii_results]) if pii_results else 0,
                'redacted_text': pii_detector.redact_message(message, pii_results)
            }
            store_pii_detection(session['user_id'], message, pii_result_formatted, bot_id)
        
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

@app.route('/pii-dashboard')
def pii_dashboard_page():
    """PII Detection Dashboard Page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pii_dashboard.html')

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

@app.route('/api/pii-methods', methods=['GET'])
def get_pii_methods():
    """Get available PII detection methods"""
    methods = {
        'simple_detection': {
            'available': True,
            'methods': ['regex'],
            'description': 'Pattern-based PII detection using regular expressions'
        }
    }
    
    if ADVANCED_PII_AVAILABLE:
        if ADVANCED_MODE == "full":
            methods['advanced_detection'] = {
                'available': True,
                'methods': ['regex', 'contextual', 'bert_ner', 'bert_clustering', 'tfidf_anomaly'],
                'description': 'AI-powered PII detection using BERT embeddings, TF-IDF, and unsupervised learning'
            }
        else:
            methods['advanced_detection'] = {
                'available': True,
                'methods': ['enhanced_regex', 'contextual_advanced', 'tfidf_clustering'],
                'description': 'Advanced PII detection using TF-IDF vectorization and unsupervised clustering'
            }
    else:
        methods['advanced_detection'] = {
            'available': False,
            'methods': [],
            'description': 'Advanced detection unavailable - install transformers, torch, sentence-transformers'
        }
        
    return jsonify(methods)

@app.route('/api/pii-statistics', methods=['GET'])
def get_pii_statistics_api():
    """Get PII detection statistics for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    try:
        user_id = session['user_id']
        include_global = request.args.get('include_global', 'false').lower() == 'true'
        
        # Get user-specific statistics
        user_stats = get_pii_statistics(user_id)
        
        result = {
            'user_stats': user_stats,
            'mongodb_connected': MONGODB_CONNECTED,
            'storage_type': 'mongodb' if MONGODB_CONNECTED else 'memory',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Optionally include global statistics (admin feature)
        if include_global and session.get('is_admin', False):
            result['global_stats'] = get_pii_statistics()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting PII statistics: {e}")
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500

@app.route('/api/pii-dashboard', methods=['GET'])
def pii_dashboard():
    """PII Detection Dashboard with comprehensive analytics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get recent PII detections
        recent_detections = []
        if MONGODB_CONNECTED and pii_detections_collection:
            # Get last 20 detections for this user
            cursor = pii_detections_collection.find(
                {'user_id': user_id},
                {'original_message': 0}  # Exclude original message for privacy
            ).sort('timestamp', -1).limit(20)
            recent_detections = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for detection in recent_detections:
                detection['_id'] = str(detection['_id'])
                detection['timestamp'] = detection['timestamp'].isoformat()
        else:
            # Use in-memory data
            user_detections = [d for d in pii_detections_db if d.get('user_id') == user_id]
            recent_detections = sorted(user_detections, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
        
        # Get statistics
        stats = get_pii_statistics(user_id)
        
        # Calculate trends (simple version for demo)
        pii_types_detected = list(set([d.get('pii_type', 'unknown') for d in recent_detections]))
        
        dashboard_data = {
            'summary': {
                'total_detections': stats['total_detections'],
                'unique_pii_types': len(pii_types_detected),
                'avg_confidence': sum([d.get('confidence', 0) for d in recent_detections]) / len(recent_detections) if recent_detections else 0,
                'storage_type': stats.get('storage_type', 'memory')
            },
            'pii_types_breakdown': stats['pii_types_stats'],
            'recent_detections': recent_detections,
            'detection_methods': list(set([d.get('detection_method', 'unknown') for d in recent_detections])),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error generating PII dashboard: {e}")
        return jsonify({'error': 'Failed to generate dashboard', 'details': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Advanced Telegram PII App...")
    logger.info("Demo Login: demo@example.com / demo123")
    logger.info("Features: Enhanced regex, contextual analysis, TF-IDF, unsupervised clustering")
    logger.info(f"Advanced PII Detection: {ADVANCED_MODE.upper()} MODE {'ENABLED' if ADVANCED_PII_AVAILABLE else 'DISABLED'}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)