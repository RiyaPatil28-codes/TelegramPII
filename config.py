import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/telegram_pii_db'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # PII Detection Settings
    PII_CONFIDENCE_THRESHOLD = 0.5
    ENABLE_PII_LOGGING = os.environ.get('ENABLE_PII_LOGGING', 'False').lower() == 'true'
    
    # Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
