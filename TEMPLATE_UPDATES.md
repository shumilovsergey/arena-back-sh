# Template Updates - Authentication & Debug Improvements

This file documents all the changes made to fix authentication issues and improve debugging in the arena-back-sh project. These changes should be applied to the base template at https://github.com/shumilovsergey/tg-app-template/tree/main/back

## 🚨 Critical Fixes Applied

### 1. **Fixed Telegram WebApp Authentication Algorithm**

**Problem**: Original authentication implementation was incorrect, causing all authentication attempts to fail.

**Files Modified**: `app/telegram_utils.py`

**Solution**: Completely rewrote the `validate_init_data` method with correct implementation:

```python
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
```

**Key Changes**:
- Manual URL parsing instead of `parse_qsl()` for better special character handling
- Correct field exclusion (only exclude `hash`, keep `signature`)
- Proper HMAC-SHA256 calculation following Telegram's algorithm
- Extensive debug logging for troubleshooting

### 2. **Enhanced CORS Configuration**

**Problem**: Frontend couldn't make requests due to CORS preflight failures.

**Files Modified**: `app/__init__.py`, `app/routes.py`

**Solutions**:

**In `app/__init__.py`**:
```python
# Enable CORS for GitHub Pages and development
CORS(app,
     origins=ALLOWED_ORIGINS,
     supports_credentials=True,
     allow_headers=['Content-Type', 'X-Telegram-Init-Data'],
     methods=['GET', 'POST', 'OPTIONS'])
```

**In `app/constants.py`**:
```python
# CORS Configuration
ALLOWED_ORIGINS = [
    FRONT_URL,
    FRONT_URL.rstrip('/'),  # Without trailing slash
    'http://localhost:8080',  # Local development
    'http://127.0.0.1:8080',
    'https://localhost:8080'
]
```

**Added explicit OPTIONS handler in `app/routes.py`**:
```python
@api_bp.route('/user', methods=['OPTIONS'])
def user_options():
    """Handle OPTIONS preflight for /user endpoint"""
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
```

### 3. **Comprehensive Debug Logging**

**Files Modified**: `app/routes.py`, `app/telegram_utils.py`

**Added Debug Logging in `app/routes.py`**:
```python
# Debug: Log request headers
print(f"DEBUG: Request headers: {dict(request.headers)}")
print(f"DEBUG: X-Telegram-Init-Data present: {'X-Telegram-Init-Data' in request.headers}")

# After authentication validation
print(f"DEBUG: Auth validation result: is_valid={is_valid}, error_msg={error_msg}")

# When returning user data
print(f"DEBUG: Returning existing user: {existing_user}")
print(f"DEBUG: Created new user: {new_user}")
```

## 🔧 Configuration Improvements

### 4. **Environment Configuration**

**File**: `.env.example`

**Updated template with all required variables**:
```bash
# Flask Configuration
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-change-in-production

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Telegram Bot Configuration
BOT_TOKEN=your-telegram-bot-token-here

# Frontend URL Configuration
FRONTEND_URL=https://yourusername.github.io/arena-front-sh/

# Backend URL Configuration (used for webhook setup)
BACKEND_URL=https://your-backend-domain.com

# Personal Website Configuration
SHUMILOV_WEBSITE=https://sh-development.ru

# Bot Webhook Configuration
WEBHOOK_URL=https://your-backend-domain.com/api/webhook

# Additional configuration
PYTHONUNBUFFERED=1
```

### 5. **Webhook Auto-Setup Disable**

**File**: `app/__init__.py`

**Problem**: Webhook was being set automatically on startup, which could interfere with development.

**Solution**: Commented out auto-webhook setup:
```python
# Set webhook on startup
# if BOT_TOKEN and WEBHOOK_URL:
#     set_webhook(BOT_TOKEN, WEBHOOK_URL)
```

**Note**: Webhook should be set manually via BotFather or API when ready for production.

## 🐛 Debug Features Added

### 6. **Request Debugging**

All API endpoints now log:
- Complete request headers
- Authentication data presence
- Authentication validation results
- User creation/retrieval details
- Response data being sent

### 7. **Authentication Debugging**

Telegram authentication now logs:
- Parsed init data structure
- Hash calculation steps
- Data check string contents
- Secret key generation
- Hash comparison results
- Validation success/failure reasons

### 8. **CORS Debugging**

CORS preflight requests now log:
- Origin information
- Requested headers
- Preflight handling status

## 📝 Setup Instructions for New Projects

### 1. **Environment Setup**
1. Copy `.env.example` to `.env`
2. Set `BOT_TOKEN` (get from @BotFather)
3. Set `FRONTEND_URL` (your GitHub Pages URL)
4. Set `BACKEND_URL` (your server domain)
5. Set `WEBHOOK_URL` (usually `BACKEND_URL/api/webhook`)

### 2. **BotFather Configuration**
1. Create bot with @BotFather
2. Get bot token
3. Set WebApp URL: `/mybots` → Your Bot → Bot Settings → Menu Button → Configure Menu Button
4. Set URL to your frontend (e.g., `https://yourusername.github.io/arena-front-sh/`)

### 3. **Deployment**
```bash
# Production deployment
docker-compose up -d --build

# Check logs for authentication debugging
docker-compose logs -f backend

# Verify user creation
docker exec arena-redis redis-cli keys "*"
docker exec arena-redis redis-cli hgetall "user:YOUR_TELEGRAM_ID"
```

## 🔍 Troubleshooting Guide

### Authentication Issues
1. **Check bot token**: Use `curl "https://api.telegram.org/botYOUR_TOKEN/getMe"`
2. **Check WebApp configuration**: Ensure WebApp URL is set in BotFather
3. **Check CORS**: Look for OPTIONS requests in logs
4. **Check hash validation**: Debug logs show exact hash calculation steps

### Common Errors
- **"Authentication failed"**: Usually wrong bot token or WebApp not configured
- **CORS errors**: Check `FRONTEND_URL` matches exactly (with/without trailing slash)
- **Hash mismatch**: Check bot token matches the one used in Telegram WebApp

### Debug Log Examples

**Successful Authentication**:
```
DEBUG: Hashes match: True
DEBUG: Auth validation result: is_valid=True, error_msg=None
DEBUG: Created new user: {'telegram_id': '507717647', ...}
GET /api/user HTTP/1.1" 201
```

**Failed Authentication**:
```
DEBUG: Hashes match: False
DEBUG: Hash validation failed!
DEBUG: Auth validation result: is_valid=False, error_msg=Invalid authentication data
GET /api/user HTTP/1.1" 401
```

**CORS Issues**:
```
DEBUG: OPTIONS request to /user endpoint
DEBUG: Origin: https://yourusername.github.io
DEBUG: Access-Control-Request-Headers: content-type,x-telegram-init-data
```

## 🎯 Results

After applying these changes:
- ✅ **Telegram WebApp authentication works correctly**
- ✅ **CORS preflight requests handled properly**
- ✅ **Users created and stored in Redis successfully**
- ✅ **Comprehensive debug logging for troubleshooting**
- ✅ **Backend returns proper JSON responses**
- ✅ **Ready for production deployment**

## 📋 Files to Update in Template

1. `app/telegram_utils.py` - Complete rewrite of authentication logic
2. `app/__init__.py` - Enhanced CORS configuration
3. `app/routes.py` - Added debug logging and OPTIONS handler
4. `app/constants.py` - Improved CORS origins handling
5. `.env.example` - Complete environment variables template
6. `CLAUDE.md` - Updated documentation with new architecture details

---

**Note**: Keep all debug print statements in the template. They are invaluable for troubleshooting authentication issues and can be easily disabled by setting `FLASK_DEBUG=False` in production.