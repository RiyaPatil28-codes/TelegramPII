import os
import logging
from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# MongoDB Configuration
app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")
mongo = PyMongo(app)

# MongoDB storage class
class MongoStorage:
    def __init__(self, mongo_instance):
        self.mongo = mongo_instance
    
    def find_user_by_email(self, email):
        return self.mongo.db.users.find_one({"email": email})
    
    def save_user(self, email, user_data):
        try:
            result = self.mongo.db.users.insert_one(user_data)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error saving user: {e}")
            return False
    
    def save_message(self, message_data):
        try:
            result = self.mongo.db.messages.insert_one(message_data)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            return False
    
    def get_user_messages(self, user_id, bot_id=None, limit=50):
        try:
            query = {"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]}
            if bot_id:
                query["bot_id"] = bot_id
            return list(self.mongo.db.messages.find(query).sort("timestamp", -1).limit(limit))
        except Exception as e:
            logging.error(f"Error retrieving messages: {e}")
            return []

# MongoDB storage instance
storage = MongoStorage(mongo)

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
