"""
Telegram utilities for validating init data and parsing responses
"""

import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any


class TelegramAuth:
    """Handle Telegram WebApp authentication"""

    @staticmethod
    def validate_init_data(init_data, bot_token):
        """
        Validate Telegram WebApp init data
        Returns (is_valid, user_data) tuple
        """
        if not init_data or not bot_token:
            return False, None

        try:
            # Alternative implementation based on working GitHub examples
            from urllib.parse import unquote

            # Parse the query string manually
            vals = {}
            for pair in init_data.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    vals[key] = unquote(value)

            print(f"DEBUG: Manual parsed data: {vals}")

            # Extract hash
            received_hash = vals.pop('hash', None)
            if not received_hash:
                print("DEBUG: No hash found in init data")
                return False, None

            print(f"DEBUG: Received hash: {received_hash}")

            # Create data check string (exclude hash only, keep signature)
            data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()))

            print(f"DEBUG: Data check string: {repr(data_check_string)}")

            # Generate secret key
            secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

            # Calculate hash
            calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

            print(f"DEBUG: Calculated hash: {calculated_hash}")
            print(f"DEBUG: Received hash:   {received_hash}")
            print(f"DEBUG: Hashes match: {hmac.compare_digest(received_hash, calculated_hash)}")

            # Verify hash
            is_valid = hmac.compare_digest(received_hash, calculated_hash)

            if not is_valid:
                print("DEBUG: Hash validation failed!")
                return False, None

            # Check auth date (optional - ensure request is recent)
            auth_date = vals.get('auth_date')
            if auth_date:
                auth_timestamp = int(auth_date)
                current_timestamp = datetime.utcnow().timestamp()

                # Check if auth is older than 24 hours
                if current_timestamp - auth_timestamp > 86400:
                    print("Warning: Auth data is older than 24 hours")

            # Parse user data
            user_data = None
            if 'user' in vals:
                try:
                    user_data = json.loads(vals['user'])
                except json.JSONDecodeError:
                    pass

            return True, user_data

        except Exception as e:
            print(f"Error validating init data: {e}")
            return False, None

    @staticmethod
    def extract_user_from_init_data(init_data):
        """
        Extract user data from init data string
        Returns user dict or None
        """
        if not init_data:
            return None

        try:
            parsed_data = urllib.parse.parse_qsl(init_data)
            data_dict = dict(parsed_data)

            if 'user' in data_dict:
                return json.loads(data_dict['user'])

        except Exception as e:
            print(f"Error extracting user from init data: {e}")

        return None

    @staticmethod
    def parse_telegram_response(response_data):
        """
        Parse response from Telegram Bot API
        Returns (success, data, error) tuple
        """
        try:
            if isinstance(response_data, str):
                response_data = json.loads(response_data)

            success = response_data.get('ok', False)
            result = response_data.get('result')
            error_code = response_data.get('error_code')
            description = response_data.get('description')

            if success:
                return True, result, None
            else:
                error_msg = f"Error {error_code}: {description}" if error_code else "Unknown error"
                return False, None, error_msg

        except Exception as e:
            return False, None, f"Failed to parse response: {e}"


class TelegramValidator:
    """Additional validation utilities"""

    @staticmethod
    def is_valid_telegram_id(telegram_id):
        """Check if telegram ID is valid format"""
        try:
            tid = int(telegram_id)
            return tid > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def sanitize_user_data(user_data):
        """Sanitize user data from Telegram"""
        if not isinstance(user_data, dict):
            return {}

        sanitized = {}
        allowed_fields = [
            'id', 'first_name', 'last_name', 'username',
            'language_code', 'is_bot', 'is_premium'
        ]

        for field in allowed_fields:
            if field in user_data:
                value = user_data[field]
                # Convert to string and limit length
                if isinstance(value, (str, int, bool)):
                    sanitized[field] = str(value)[:100] if field != 'id' else str(value)

        return sanitized

    @staticmethod
    def validate_user_update_data(data):
        """Validate data for user updates"""
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"

        # Check for required fields if updating basic info
        if 'first_name' in data and not data['first_name'].strip():
            return False, "First name cannot be empty"

        # Validate user_data field
        if 'user_data' in data:
            if not isinstance(data['user_data'], dict):
                return False, "user_data must be a dictionary"

            # Check user_data size (limit to prevent abuse)
            try:
                user_data_str = json.dumps(data['user_data'])
                if len(user_data_str) > 10000:  # 10KB limit
                    return False, "user_data is too large (max 10KB)"
            except Exception:
                return False, "user_data contains invalid JSON data"

        return True, "Valid"


# Helper functions for common operations
def get_user_id_from_request(request):
    """Extract user ID from request headers"""
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        return None

    user_data = TelegramAuth.extract_user_from_init_data(init_data)
    if user_data and 'id' in user_data:
        return user_data['id']

    return None


def validate_request_auth(request, bot_token):
    """Validate request authentication"""
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        return False, None, "No authentication data provided"

    is_valid, user_data = TelegramAuth.validate_init_data(init_data, bot_token)
    if not is_valid:
        return False, None, "Invalid authentication data"

    if not user_data or 'id' not in user_data:
        return False, None, "Invalid user data"

    return True, user_data, None


# Bot webhook message parsing utilities

@dataclass
class Message:
    """User-friendly message structure for Telegram updates"""
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    text: Optional[str] = None
    photo: Optional[str] = None
    video: Optional[str] = None
    voice: Optional[str] = None
    document: Optional[str] = None
    callback_data: Optional[str] = None

    def get_full_name(self) -> str:
        """Get user's full name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts) if parts else self.username or 'Unknown'

    def has_media(self) -> bool:
        """Check if message contains any media"""
        return any([self.photo, self.video, self.voice, self.document])


def flatten_json(nested_json: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested json object
    """
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # Take the first item if it's a list of dicts (like photos array)
            items.extend(flatten_json(v[0], new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get(flat_update: Dict[str, Any], key: str) -> Any:
    """
    Get value from flattened update data
    """
    return flat_update.get(key)


def parse_telegram_update(update: Dict[str, Any]) -> Message:
    """
    Parse Telegram update into user-friendly Message format
    """
    flat_update = flatten_json(update)

    # Extract message data (could be from message or callback_query)
    message_data = {}

    # Try to get from direct message
    if 'message' in update:
        msg = update['message']
        message_data.update({
            'chat_id': get(flat_update, 'message_chat_id'),
            'message_id': get(flat_update, 'message_message_id'),
            'user_id': get(flat_update, 'message_from_id'),
            'username': get(flat_update, 'message_from_username'),
            'first_name': get(flat_update, 'message_from_first_name'),
            'last_name': get(flat_update, 'message_from_last_name'),
            'text': get(flat_update, 'message_text'),
        })

        # Handle media
        if 'photo' in msg:
            message_data['photo'] = get(flat_update, 'message_photo_file_id')
        if 'video' in msg:
            message_data['video'] = get(flat_update, 'message_video_file_id')
        if 'voice' in msg:
            message_data['voice'] = get(flat_update, 'message_voice_file_id')
        if 'document' in msg:
            message_data['document'] = get(flat_update, 'message_document_file_id')

    # Try to get from callback query
    elif 'callback_query' in update:
        message_data.update({
            'chat_id': get(flat_update, 'callback_query_message_chat_id'),
            'message_id': get(flat_update, 'callback_query_message_message_id'),
            'user_id': get(flat_update, 'callback_query_from_id'),
            'username': get(flat_update, 'callback_query_from_username'),
            'first_name': get(flat_update, 'callback_query_from_first_name'),
            'last_name': get(flat_update, 'callback_query_from_last_name'),
            'callback_data': get(flat_update, 'callback_query_data'),
        })

    # Try to get from edited message
    elif 'edited_message' in update:
        message_data.update({
            'chat_id': get(flat_update, 'edited_message_chat_id'),
            'message_id': get(flat_update, 'edited_message_message_id'),
            'user_id': get(flat_update, 'edited_message_from_id'),
            'username': get(flat_update, 'edited_message_from_username'),
            'first_name': get(flat_update, 'edited_message_from_first_name'),
            'last_name': get(flat_update, 'edited_message_from_last_name'),
            'text': get(flat_update, 'edited_message_text'),
        })

    return Message(**message_data)


def validate_telegram_webhook(request, bot_token: str) -> bool:
    """
    Validate incoming webhook request from Telegram
    Optional: Implement webhook secret validation if needed
    """
    # For basic validation, check if request contains valid update structure
    try:
        data = request.get_json()
        if not data:
            return False

        # Check if it has basic Telegram update structure
        valid_keys = ['update_id', 'message', 'callback_query', 'edited_message', 'channel_post']
        if not any(key in data for key in valid_keys):
            return False

        return True
    except Exception:
        return False