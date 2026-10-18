import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    # Session Cookie Security Flags
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set Secure to True in production (HTTPS), False for local development
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_DEBUG', 'False').lower() != 'true'
    
    MOCK_AUTH = os.environ.get('MOCK_AUTH', 'False').lower() == 'true'
    OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')