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

# MongoDB configuration
mongo_uri = "mongodb+srv://riya28:2022PE0226r@cluster0.op9ayen.mongodb.net/telegram_pii?retryWrites=true&w=majority&appName=Cluster0"
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

# Test MongoDB connection
try:
    with app.app_context():
        info = mongo.db.command('ismaster')
        logging.info(f"MongoDB connection established successfully. Server version: {info.get('version', 'Unknown')}")
except Exception as e:
    logging.error(f"Failed to establish MongoDB connection: {e}")
    # Continue anyway to let the app start

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
