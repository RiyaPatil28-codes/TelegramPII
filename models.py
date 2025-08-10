from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
import logging

class User:
    def __init__(self, username=None, email=None, password=None, profile_picture=None, _id=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.profile_picture = profile_picture
        self.created_at = datetime.utcnow()
        self._id = _id
    
    def save(self):
        """Save user to MongoDB"""
        try:
            user_data = {
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'profile_picture': self.profile_picture,
                'created_at': self.created_at,
                'contacts': [],
                'blocked_users': []
            }
            result = mongo.db.users.insert_one(user_data)
            self._id = result.inserted_id
            logging.debug(f"User saved with ID: {self._id}")
            return True
        except Exception as e:
            logging.error(f"Error saving user: {e}")
            return False
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            user = User()
            user._id = user_data['_id']
            user.username = user_data['username']
            user.email = user_data['email']
            user.password_hash = user_data['password_hash']
            user.profile_picture = user_data.get('profile_picture')
            user.created_at = user_data.get('created_at')
            return user
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = mongo.db.users.find_one({'_id': user_id})
        if user_data:
            user = User()
            user._id = user_data['_id']
            user.username = user_data['username']
            user.email = user_data['email']
            user.password_hash = user_data['password_hash']
            user.profile_picture = user_data.get('profile_picture')
            user.created_at = user_data.get('created_at')
            return user
        return None
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self._id)
    
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
