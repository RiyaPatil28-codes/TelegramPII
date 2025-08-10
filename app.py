import os
import logging
from flask import Flask
# Simplified approach without MongoDB for now
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Simplified storage for now - can be replaced with real DB later
class SimpleStorage:
    def __init__(self):
        self.users = {}
        self.messages = []
    
    def find_user_by_email(self, email):
        return self.users.get(email)
    
    def save_user(self, email, user_data):
        self.users[email] = user_data
        return True

# Simple in-memory storage (for demo purposes)
storage = SimpleStorage()

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
