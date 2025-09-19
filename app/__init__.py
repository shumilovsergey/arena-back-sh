"""
Flask application factory
"""

import time
import requests
from flask import Flask
from flask_cors import CORS
from .database import init_redis, wait_for_redis
from .constants import (
    SECRET_KEY, REDIS_URL, BOT_TOKEN, WEBHOOK_URL, TELEGRAM_API_BASE, FRONT_URL
)


def set_webhook(bot_token: str, webhook_url: str):
    """Set Telegram bot webhook on startup"""
    try:
        url = f"{TELEGRAM_API_BASE}/setWebhook"
        payload = {"url": webhook_url}
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Webhook set successfully: {webhook_url}")
            else:
                print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code} when setting webhook")
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['REDIS_URL'] = REDIS_URL
    app.config['BOT_TOKEN'] = BOT_TOKEN

    # CORS configuration for Telegram Mini Apps
    # Using permissive CORS for Telegram WebApp compatibility
    CORS(app)

    # Wait for Redis to be available
    print("Waiting for Redis to be available...")
    wait_for_redis(app.config['REDIS_URL'])

    # Initialize Redis connection
    init_redis(app)

    # Set webhook on startup
    # if BOT_TOKEN and WEBHOOK_URL:
    #     set_webhook(BOT_TOKEN, WEBHOOK_URL)

    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': time.time()}

    @app.route('/')
    def index():
        return {
            'message': 'Telegram App Template Backend',
            'status': 'running',
            'endpoints': [
                '/health - Health check',
                '/api/user - User management'
            ]
        }

    return app