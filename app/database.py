"""
Redis database connection and utilities
"""

import redis
import json
import time
from datetime import datetime
from urllib.parse import urlparse


# Global Redis connection
redis_client = None


def wait_for_redis(redis_url, max_retries=30, retry_delay=2):
    """Wait for Redis to be available"""
    for attempt in range(max_retries):
        try:
            # Parse Redis URL
            parsed_url = urlparse(redis_url)
            host = parsed_url.hostname or 'localhost'
            port = parsed_url.port or 6379
            db = int(parsed_url.path.lstrip('/')) if parsed_url.path else 0

            # Test connection
            test_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            test_client.ping()
            print(f"Redis is available at {host}:{port}")
            return True

        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Redis not ready ({e})")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise Exception(f"Redis not available after {max_retries} attempts")

    return False


def init_redis(app):
    """Initialize Redis connection"""
    global redis_client

    redis_url = app.config['REDIS_URL']
    parsed_url = urlparse(redis_url)

    host = parsed_url.hostname or 'localhost'
    port = parsed_url.port or 6379
    db = int(parsed_url.path.lstrip('/')) if parsed_url.path else 0

    redis_client = redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10
    )

    try:
        redis_client.ping()
        print(f"Redis connected successfully at {host}:{port}")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        raise


def get_redis():
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        raise Exception("Redis not initialized")
    return redis_client


class UserManager:
    """Manage user data in Redis"""

    @staticmethod
    def _get_user_key(telegram_id):
        """Generate Redis key for user"""
        return f"user:{telegram_id}"

    @staticmethod
    def get_user(telegram_id):
        """Get user data from Redis"""
        redis_conn = get_redis()
        user_key = UserManager._get_user_key(telegram_id)

        user_data = redis_conn.hgetall(user_key)
        if not user_data:
            return None

        # Convert stored JSON strings back to objects
        if 'user_data' in user_data:
            user_data['user_data'] = json.loads(user_data['user_data'])

        return user_data

    @staticmethod
    def create_user(telegram_id, first_name, last_name=None, username=None, language_code=None):
        """Create new user in Redis"""
        redis_conn = get_redis()
        user_key = UserManager._get_user_key(telegram_id)

        # Check if user already exists
        if redis_conn.exists(user_key):
            return UserManager.get_user(telegram_id)

        now = datetime.utcnow().isoformat()
        user_data = {
            'telegram_id': str(telegram_id),
            'first_name': first_name or '',
            'last_name': last_name or '',
            'username': username or '',
            'language_code': language_code or '',
            'user_data': json.dumps({}),  # Store as JSON string
            'created_at': now,
            'updated_at': now
        }

        # Store user data
        redis_conn.hset(user_key, mapping=user_data)

        # Add to user index for admin purposes
        redis_conn.sadd('users:index', telegram_id)

        print(f"Created new user: {telegram_id}")
        return UserManager.get_user(telegram_id)

    @staticmethod
    def update_user(telegram_id, updates):
        """Update user data in Redis"""
        redis_conn = get_redis()
        user_key = UserManager._get_user_key(telegram_id)

        # Check if user exists
        if not redis_conn.exists(user_key):
            return None

        # Prepare updates
        update_data = {}
        for key, value in updates.items():
            if key == 'user_data':
                # Store user_data as JSON string
                update_data[key] = json.dumps(value)
            else:
                update_data[key] = str(value)

        update_data['updated_at'] = datetime.utcnow().isoformat()

        # Update user data
        redis_conn.hset(user_key, mapping=update_data)

        print(f"Updated user: {telegram_id}")
        return UserManager.get_user(telegram_id)

    @staticmethod
    def delete_user(telegram_id):
        """Delete user from Redis"""
        redis_conn = get_redis()
        user_key = UserManager._get_user_key(telegram_id)

        # Remove from user index
        redis_conn.srem('users:index', telegram_id)

        # Delete user data
        deleted = redis_conn.delete(user_key)

        print(f"Deleted user: {telegram_id}")
        return deleted > 0

    @staticmethod
    def get_all_users():
        """Get all user IDs (admin function)"""
        redis_conn = get_redis()
        return redis_conn.smembers('users:index')

    @staticmethod
    def user_exists(telegram_id):
        """Check if user exists"""
        redis_conn = get_redis()
        user_key = UserManager._get_user_key(telegram_id)
        return redis_conn.exists(user_key)

    @staticmethod
    def set_last_bot_message_id(telegram_id, message_id: int):
        """Store the ID of the last message bot sent to user"""
        redis_conn = get_redis()
        key = f"last_bot_msg:{telegram_id}"
        redis_conn.set(key, str(message_id))
        # Set expiry for message ID (7 days)
        redis_conn.expire(key, 604800)
        return True

    @staticmethod
    def get_last_bot_message_id(telegram_id):
        """Get the ID of the last message bot sent to user"""
        redis_conn = get_redis()
        key = f"last_bot_msg:{telegram_id}"
        message_id = redis_conn.get(key)
        return int(message_id) if message_id else None

    @staticmethod
    def clear_last_bot_message_id(telegram_id):
        """Clear the stored last bot message ID"""
        redis_conn = get_redis()
        key = f"last_bot_msg:{telegram_id}"
        return redis_conn.delete(key) > 0



# Database health check
def check_redis_health():
    """Check Redis connection health"""
    try:
        redis_conn = get_redis()
        redis_conn.ping()
        return True
    except Exception:
        return False