"""
Application constants loaded from environment variables
NO DEFAULT VALUES - All values must be explicitly configured
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_required_env(var_name: str) -> str:
    """Get required environment variable or exit with error"""
    value = os.getenv(var_name)
    if not value or value.startswith('CHANGE-ME'):
        print(f"❌ ERROR: Required environment variable '{var_name}' is not set or has placeholder value!")
        print(f"   Please configure '{var_name}' in your .env file")
        print(f"   Copy .env.example to .env and update all CHANGE-ME values")
        sys.exit(1)
    return value

def get_required_env_int(var_name: str) -> int:
    """Get required environment variable as integer or exit with error"""
    value = get_required_env(var_name)
    try:
        return int(value)
    except ValueError:
        print(f"❌ ERROR: Environment variable '{var_name}' must be a valid integer!")
        print(f"   Current value: '{value}'")
        sys.exit(1)

def validate_project_name(project_name: str) -> str:
    """Validate project name format"""
    if not project_name.replace('-', '').replace('_', '').isalnum():
        print(f"❌ ERROR: PROJECT_NAME '{project_name}' contains invalid characters!")
        print("   Use only lowercase letters, numbers, hyphens, and underscores")
        print("   Examples: myapp, telegram-shop, crypto_bot")
        sys.exit(1)
    return project_name.lower()

# Core Configuration (REQUIRED)
PROJECT_NAME = validate_project_name(get_required_env('PROJECT_NAME'))
SECRET_KEY = get_required_env('SECRET_KEY')
BOT_TOKEN = get_required_env('BOT_TOKEN')

# Flask Configuration
FLASK_HOST = '0.0.0.0'  # Hardcoded - no need to configure
FLASK_PORT = get_required_env_int('FLASK_PORT')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# URL Configuration (REQUIRED)
FRONT_URL = get_required_env('FRONTEND_URL')
BACKEND_URL = get_required_env('BACKEND_URL')

# Auto-generated Docker Configuration
FLASK_CONTAINER_NAME = f"{PROJECT_NAME}-flask"
REDIS_CONTAINER_NAME = f"{PROJECT_NAME}-redis"
PRIVATE_NETWORK_NAME = f"{PROJECT_NAME}-private-network"
PUBLIC_NETWORK_NAME = f"{PROJECT_NAME}-public-network"
REDIS_VOLUME_NAME = f"{PROJECT_NAME}-redis-data"

# Auto-generated URLs and Ports
WEBHOOK_URL = f"{BACKEND_URL}/api/webhook"
REDIS_PORT = 6379  # Hardcoded - isolated in container, no conflicts possible
REDIS_URL = f"redis://{REDIS_CONTAINER_NAME}:{REDIS_PORT}/0"

# Optional Configuration
SHUMILOV_WEBSITE = os.getenv('SHUMILOV_WEBSITE', 'https://sh-development.ru')

# Development User Bypass Configuration (OPTIONAL)
ENABLE_DEV_USER = os.getenv('ENABLE_DEV_USER', 'false').lower() == 'true'
DEV_USER_ID = int(os.getenv('DEV_USER_ID', '999999999'))
DEV_USER_FIRST_NAME = os.getenv('DEV_USER_FIRST_NAME', 'Dev User')
DEV_USER_LAST_NAME = os.getenv('DEV_USER_LAST_NAME', 'Template')
DEV_USER_USERNAME = os.getenv('DEV_USER_USERNAME', 'dev_user')
DEV_USER_LANGUAGE = os.getenv('DEV_USER_LANGUAGE', 'en')
DEV_AUTH_HEADER = os.getenv('DEV_AUTH_HEADER', 'dev-user-bypass')

# CORS Configuration Removed - Telegram cryptographic validation provides security

# Telegram API Base URL
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("✅ All environment variables validated successfully!")
print(f"   Project: {PROJECT_NAME}")
print(f"   Flask container: {FLASK_CONTAINER_NAME} (exposed port: {FLASK_PORT})")
print(f"   Redis container: {REDIS_CONTAINER_NAME} (internal port: {REDIS_PORT})")
print(f"   Private network: {PRIVATE_NETWORK_NAME}")
print(f"   Public network: {PUBLIC_NETWORK_NAME}")
print(f"   Volume: {REDIS_VOLUME_NAME}")
print(f"   Frontend URL: {FRONT_URL}")
print(f"   Backend URL: {BACKEND_URL}")
print(f"   Webhook URL: {WEBHOOK_URL}")
print("🔓 CORS disabled - All origins allowed (Telegram validation provides security)")

if ENABLE_DEV_USER:
    print("🚧 DEV USER BYPASS ENABLED - Local development mode")
    print(f"   Dev user ID: {DEV_USER_ID}")
    print(f"   Dev auth header: X-Dev-Auth: {DEV_AUTH_HEADER}")
    print("   ⚠️  WARNING: Only use for development/testing!")
else:
    print("🔒 Production mode - Telegram authentication required")