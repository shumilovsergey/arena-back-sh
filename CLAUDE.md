# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based Telegram Web App backend with Redis storage and Docker deployment. It's designed to work with a separate frontend and provides secure user authentication through Telegram WebApp validation.

## Quick Start Commands

```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your BOT_TOKEN, PROJECT_NAME, and URLs

# Start full backend with Redis
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f redis

# Stop all services
docker-compose down

# Clean everything including volumes
docker-compose down -v --remove-orphans

# Development mode (without Docker)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python run.py
```

## Environment Configuration

All configuration is done through environment variables. The app requires a properly configured `.env` file:

**Required Variables:**
- `PROJECT_NAME` - Alphanumeric name for Docker containers/networks
- `SECRET_KEY` - Flask secret key for sessions
- `BOT_TOKEN` - Telegram bot token from BotFather
- `FLASK_PORT` - Port for Flask app (default: 5000)
- `FRONTEND_URL` - URL where frontend is hosted
- `BACKEND_URL` - URL where this backend is accessible

**Optional Variables:**
- `FLASK_DEBUG` - Enable Flask debug mode (default: False)
- `SHUMILOV_WEBSITE` - Personal website URL
- `ENABLE_DEV_USER` - Enable development bypass (default: false)

The app will exit with clear error messages if required variables are missing or have placeholder values.

## Architecture

### Core Components

- **Flask App Factory** (`app/__init__.py`): Creates configured Flask app with Redis initialization
- **User Manager** (`app/database.py`): Redis-based user data management with JSON serialization
- **Routes** (`app/routes.py`): API endpoints for user data and Telegram bot webhook
- **Telegram Utils** (`app/telegram_utils.py`): Webhook validation and auth verification
- **Bot Logic** (`app/bot_logic.py`): Telegram bot message handling and commands
- **Constants** (`app/constants.py`): Environment variable validation and configuration

### Database Design

Redis stores user data with these key patterns:
- `user:{telegram_id}` - Hash containing user profile and app data
- `users:index` - Set of all user IDs for admin functions
- `last_bot_msg:{telegram_id}` - Last bot message ID for cleanup

User records include:
- Basic Telegram profile data (first_name, last_name, username, language_code)
- `user_data` field containing JSON-serialized application-specific data
- Created/updated timestamps

### Security Architecture

- **Telegram WebApp Auth**: Cryptographic validation of init data using bot token
- **User Data Isolation**: Each user can only access their own data
- **Input Validation**: All user inputs are validated and sanitized
- **Network Isolation**: Redis runs in private Docker network, only accessible by backend
- **No CORS Restrictions**: Relies on Telegram's cryptographic validation instead

## API Endpoints

### User Management (requires Telegram auth)
- `POST /api/user/get_data` - Get or create user data
- `POST /api/user/up_data` - Update user data
- `GET /api/health` - API health check

### Bot Webhook
- `POST /api/webhook` - Telegram bot webhook endpoint

### Health Checks
- `GET /health` - Main health check
- `GET /api/health` - API-specific health check with Redis status

## Docker Architecture

Two-network setup for security:
- **Private Network**: Flask ↔ Redis communication only
- **Public Network**: Flask port exposure to host

Containers:
- `{PROJECT_NAME}-flask` - Flask application
- `{PROJECT_NAME}-redis` - Redis database with persistent volume

Volume: `./redis_data` - Bind mount for Redis data persistence

## Development Workflow

1. **Environment Setup**: Copy `.env.example` to `.env` and configure all required variables
2. **Local Development**: Use `python run.py` or Docker Compose
3. **Testing**: Access health endpoints to verify Redis connectivity
4. **Production Deploy**: Ensure `BACKEND_URL` and `FRONTEND_URL` match deployed endpoints

## Common Development Tasks

```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# View Redis data
docker-compose exec redis redis-cli
> KEYS user:*
> HGETALL user:123456789

# Restart just the backend
docker-compose restart backend

# Check environment validation
python -c "from app.constants import *"
```

## Bot Integration

The webhook endpoint processes Telegram updates and supports:
- Message handling with automatic cleanup
- User creation/retrieval from database
- Command processing with protected commands
- Validation of webhook authenticity

Critical bot commands like `/start` are protected from cleanup to maintain user experience.

## Error Handling

The app validates all environment variables on startup and exits with clear error messages for:
- Missing required environment variables
- Invalid environment variable formats
- Placeholder values in production
- Invalid project names
- Redis connection failures