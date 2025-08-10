from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import logging

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    stories = db.relationship('Story', backref='author', lazy='dynamic')
    
    def __init__(self, username=None, email=None, password=None, profile_picture=None):
        self.username = username
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)
        self.profile_picture = profile_picture
    
    def save(self):
        """Save user to PostgreSQL"""
        try:
            db.session.add(self)
            db.session.commit()
            logging.debug(f"User saved with ID: {self.id}")
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving user: {e}")
            return False
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return User.query.get(user_id)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

class Message:
    def __init__(self, sender_id, recipient_id, content, message_type='text', has_pii=False, redacted_content=None):
        self.sender_id = ObjectId(sender_id) if isinstance(sender_id, str) else sender_id
        self.recipient_id = ObjectId(recipient_id) if isinstance(recipient_id, str) else recipient_id
        self.content = content
        self.redacted_content = redacted_content
        self.message_type = message_type
        self.has_pii = has_pii
        self.timestamp = datetime.utcnow()
        self.is_read = False
        self.pii_detected = []
    
    def save(self):
        """Save message to MongoDB"""
        try:
            message_data = {
                'sender_id': self.sender_id,
                'recipient_id': self.recipient_id,
                'content': self.content,
                'redacted_content': self.redacted_content,
                'message_type': self.message_type,
                'has_pii': self.has_pii,
                'pii_detected': self.pii_detected,
                'timestamp': self.timestamp,
                'is_read': self.is_read
            }
            result = mongo.db.messages.insert_one(message_data)
            self._id = result.inserted_id
            logging.debug(f"Message saved with ID: {self._id}")
            return True
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            return False
    
    @staticmethod
    def get_conversation(user1_id, user2_id, limit=50):
        """Get conversation between two users"""
        if isinstance(user1_id, str):
            user1_id = ObjectId(user1_id)
        if isinstance(user2_id, str):
            user2_id = ObjectId(user2_id)
        
        messages = mongo.db.messages.find({
            '$or': [
                {'sender_id': user1_id, 'recipient_id': user2_id},
                {'sender_id': user2_id, 'recipient_id': user1_id}
            ]
        }).sort('timestamp', 1).limit(limit)
        
        return list(messages)

class Story:
    def __init__(self, user_id, content, media_url=None, expires_at=None):
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.content = content
        self.media_url = media_url
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at or datetime.utcnow().replace(hour=23, minute=59, second=59)
        self.views = []
    
    def save(self):
        """Save story to MongoDB"""
        try:
            story_data = {
                'user_id': self.user_id,
                'content': self.content,
                'media_url': self.media_url,
                'created_at': self.created_at,
                'expires_at': self.expires_at,
                'views': self.views
            }
            result = mongo.db.stories.insert_one(story_data)
            self._id = result.inserted_id
            logging.debug(f"Story saved with ID: {self._id}")
            return True
        except Exception as e:
            logging.error(f"Error saving story: {e}")
            return False
    
    @staticmethod
    def get_active_stories(user_id):
        """Get active stories for a user's contacts"""
        current_time = datetime.utcnow()
        stories = mongo.db.stories.find({
            'expires_at': {'$gt': current_time}
        }).sort('created_at', -1)
        
        return list(stories)
