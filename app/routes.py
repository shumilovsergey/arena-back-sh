"""
API routes for user management
"""

from flask import Blueprint, request, jsonify, current_app
from .database import UserManager, check_redis_health
from .telegram_utils import validate_request_auth, TelegramValidator, validate_telegram_webhook
from .bot_logic import TelegramBot, BotMessageHandler
from .constants import BOT_TOKEN, TELEGRAM_API_BASE


api_bp = Blueprint('api', __name__)


@api_bp.route('/user/get_data', methods=['OPTIONS'])
@api_bp.route('/user/up_data', methods=['OPTIONS'])
def user_options():
    """Handle OPTIONS preflight for user endpoints"""
    print("DEBUG: OPTIONS request to /user endpoint")
    print(f"DEBUG: Origin: {request.headers.get('Origin')}")
    print(f"DEBUG: Access-Control-Request-Headers: {request.headers.get('Access-Control-Request-Headers')}")

    from flask import Response
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Telegram-Init-Data'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


@api_bp.route('/user/get_data', methods=['POST'])
def get_user_data():
    """Get or create user data"""
    try:
        # Debug: Log request headers
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: X-Telegram-Init-Data present: {'X-Telegram-Init-Data' in request.headers}")

        # Check bot token configuration
        if not current_app.config.get('BOT_TOKEN'):
            return jsonify({
                'error': 'Bot token not configured',
                'message': 'Please set BOT_TOKEN environment variable'
            }), 500

        # Validate authentication
        is_valid, user_data, error_msg = validate_request_auth(
            request, current_app.config['BOT_TOKEN']
        )

        # After authentication validation
        print(f"DEBUG: Auth validation result: is_valid={is_valid}, error_msg={error_msg}")

        if not is_valid:
            return jsonify({'error': error_msg}), 401

        telegram_id = user_data['id']

        # Check if user exists
        existing_user = UserManager.get_user(telegram_id)
        if existing_user:
            # When returning user data
            print(f"DEBUG: Returning existing user: {existing_user}")
            return jsonify({'user': existing_user})

        # Create new user
        sanitized_user_data = TelegramValidator.sanitize_user_data(user_data)
        new_user = UserManager.create_user(
            telegram_id=telegram_id,
            first_name=sanitized_user_data.get('first_name', ''),
            last_name=sanitized_user_data.get('last_name', ''),
            username=sanitized_user_data.get('username', ''),
            language_code=sanitized_user_data.get('language_code', '')
        )

        print(f"DEBUG: Created new user: {new_user}")
        return jsonify({'user': new_user}), 201

    except Exception as e:
        print(f"Error in get_user: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/user/up_data', methods=['POST'])
def update_user_data():
    """Update user data"""
    try:
        # Get request data
        update_data = request.get_json()
        if not update_data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate update data
        is_valid, validation_msg = TelegramValidator.validate_user_update_data(update_data)
        if not is_valid:
            return jsonify({'error': validation_msg}), 400

        # Check bot token configuration
        if not current_app.config.get('BOT_TOKEN'):
            return jsonify({
                'error': 'Bot token not configured',
                'message': 'Please set BOT_TOKEN environment variable'
            }), 500

        # Validate authentication
        is_valid, user_data, error_msg = validate_request_auth(
            request, current_app.config['BOT_TOKEN']
        )

        if not is_valid:
            return jsonify({'error': error_msg}), 401

        telegram_id = user_data['id']

        # Check if user exists
        if not UserManager.user_exists(telegram_id):
            return jsonify({'error': 'User not found'}), 404

        # Update user
        updated_user = UserManager.update_user(telegram_id, update_data)
        if not updated_user:
            return jsonify({'error': 'Failed to update user'}), 500

        return jsonify({'user': updated_user})

    except Exception as e:
        print(f"Error in update_user: {e}")
        return jsonify({'error': 'Internal server error'}), 500



@api_bp.route('/health', methods=['GET'])
def api_health():
    """API health check"""
    try:
        redis_healthy = check_redis_health()
        return jsonify({
            'status': 'healthy' if redis_healthy else 'unhealthy',
            'redis': 'connected' if redis_healthy else 'disconnected',
            'timestamp': request.headers.get('X-Request-Time')
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500




# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Bot webhook routes
@api_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram bot webhook"""
    try:
        bot_token = current_app.config.get('BOT_TOKEN')
        if not bot_token:
            return jsonify({'error': 'Bot token not configured'}), 500

        # Validate webhook request
        if not validate_telegram_webhook(request, bot_token):
            return jsonify({'error': 'Invalid webhook request'}), 400

        # Get update data
        update = request.get_json()
        if not update:
            return jsonify({'error': 'No update data'}), 400

        # Initialize bot and handler
        bot = TelegramBot(bot_token)
        handler = BotMessageHandler(bot)

        # Process the update
        success = handler.handle_update(update)

        if success:
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'error': 'Failed to process update'}), 500

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


