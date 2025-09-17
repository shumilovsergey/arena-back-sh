"""
Application constants loaded from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Frontend URL Configuration
FRONT_URL = os.getenv('FRONTEND_URL', 'https://yourusername.github.io')

# Backend URL Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'https://your-backend-domain.com')

# Personal Website Configuration
SHUMILOV_WEBSITE = os.getenv('SHUMILOV_WEBSITE', 'https://sh-development.ru')

# Webhook Configuration
WEBHOOK_URL = os.getenv('WEBHOOK_URL', f'{BACKEND_URL}/api/webhook')

# CORS Configuration
ALLOWED_ORIGINS = [
    FRONT_URL,
    FRONT_URL.rstrip('/'),  # Without trailing slash
    'http://localhost:8080',  # Local development
    'http://127.0.0.1:8080',
    'https://localhost:8080'
]

# Telegram API Base URL
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

# Validation
def validate_constants():
    """Validate required constants are set"""
    required_vars = {
        'BOT_TOKEN': BOT_TOKEN,
        'SECRET_KEY': SECRET_KEY,
    }

    default_vars = {
        'FRONT_URL': FRONT_URL,
        'BACKEND_URL': BACKEND_URL
    }

    # Check for missing required variables
    missing = [name for name, value in required_vars.items() if not value]

    # Check for default placeholder values
    default_placeholders = [
        name for name, value in default_vars.items()
        if 'yourusername.github.io' in value or 'your-backend-domain.com' in value or 'sh-development.ru' in value
    ]

    if missing:
        print(f"Error: Missing required variables: {', '.join(missing)}")
        print("Please check your .env file configuration")

    if default_placeholders:
        print(f"Warning: Using default placeholder values for: {', '.join(default_placeholders)}")
        print("Please update these in your .env file for production")

    return len(missing) == 0

# Validate on import
validate_constants()