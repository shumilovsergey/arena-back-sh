# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `arena-back-sh`, a Flask-based Telegram bot backend with Redis storage. The application provides user management APIs, webhook endpoints for Telegram bot integration, and Docker-based deployment.

## Quick Start Commands

```bash
# Production deployment with Docker
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f redis

# Stop services
docker-compose down

# Clean everything (including volumes)
docker-compose down -v --remove-orphans

# Local development (without Docker)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Project Structure

```
├── app/
│   ├── __init__.py         # Flask app factory with webhook setup
│   ├── routes.py           # API endpoints (/api/user, /api/webhook, /api/health)
│   ├── database.py         # Redis connection and UserManager class
│   ├── telegram_utils.py   # Telegram auth validation and utilities
│   ├── bot_logic.py        # TelegramBot and BotMessageHandler classes
│   └── constants.py        # Environment configuration loading
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Python 3.11-slim container
├── docker-compose.yml     # Multi-container setup (backend + redis)
├── .env.example          # Environment variables template
└── README.md             # Basic setup instructions
```

## Architecture

### Flask Application Structure
- **App Factory Pattern**: `app/__init__.py` creates configured Flask app
- **Blueprint-based Routing**: API routes defined in `routes.py` under `/api` prefix
- **Environment Configuration**: All settings loaded via `constants.py` from `.env` file
- **Health Checks**: Built-in health endpoints at `/health` and `/api/health`

### Database Layer
- **Redis Integration**: `UserManager` class handles all user CRUD operations
- **Connection Management**: `wait_for_redis()` ensures Redis availability before startup
- **Data Isolation**: Each user can only access their own data via Telegram ID
- **JSON Storage**: User data stored as JSON with sanitization and validation

### Telegram Integration
- **WebApp Authentication**: `validate_request_auth()` validates Telegram WebApp init data
- **Webhook Processing**: `validate_telegram_webhook()` secures bot webhook requests
- **Bot Logic**: `TelegramBot` and `BotMessageHandler` classes for command processing
- **Auto Webhook Setup**: Webhook URL automatically configured on app startup

### Docker Infrastructure
- **Multi-container Setup**: Backend (port 9002) + Redis with isolated networking
- **Health Monitoring**: Built-in health checks for both services
- **Persistent Storage**: Redis data stored in `redis-data` Docker volume
- **Security**: Non-root user, isolated Redis network (`arena-privat`)

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required
BOT_TOKEN=your-telegram-bot-token-here
SECRET_KEY=your-secure-secret-key

# URLs
FRONTEND_URL=https://yourusername.github.io
BACKEND_URL=https://your-backend-domain.com
WEBHOOK_URL=https://your-backend-domain.com/api/webhook

# Optional (has defaults)
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
REDIS_URL=redis://redis:6379/0
```

## API Endpoints

### User Management (requires Telegram WebApp auth)
- `GET /api/user` - Get or create user data
- `POST /api/user` - Update user data (validates input)
- `GET /api/health` - API health check with Redis status

### Bot Integration
- `POST /api/webhook` - Telegram bot webhook endpoint
- `GET /health` - Application health check

All WebApp endpoints require `X-Telegram-Init-Data` header with valid Telegram WebApp authentication.

## Key Classes and Components

### UserManager (`app/database.py`)
- `create_user()` - Create new user with Telegram data
- `get_user()` - Retrieve user by Telegram ID
- `update_user()` - Update user data with validation
- `user_exists()` - Check if user exists

### TelegramValidator (`app/telegram_utils.py`)
- `validate_init_data()` - Cryptographic validation of WebApp data
- `sanitize_user_data()` - Clean and validate user input
- `validate_user_update_data()` - Validate update requests

### BotMessageHandler (`app/bot_logic.py`)
- `handle_update()` - Process incoming Telegram updates
- Command processing for bot interactions

## Development Workflow

1. **Environment Setup**: Copy `.env.example` to `.env`, set `BOT_TOKEN`
2. **Local Development**: Use `python run.py` or Docker Compose
3. **Testing**: Access API at `http://localhost:5000` (Docker: `http://localhost:9002`)
4. **Logs**: Use `docker-compose logs -f backend` for debugging
5. **Redis Access**: Redis runs in isolated network, only accessible via backend

## Security Features

- **Cryptographic Auth**: Telegram WebApp data validated with HMAC-SHA256
- **Input Sanitization**: All user inputs cleaned and validated
- **Network Isolation**: Redis accessible only to backend container
- **Non-root Execution**: Docker containers run as non-root user
- **CORS Protection**: Configured for specific frontend origins only

## Important Notes

- **No Testing Framework**: Project currently has no test files or testing setup
- **Manual Deployment**: No CI/CD pipelines configured
- **Port Mapping**: Docker exposes backend on port 9002 (not 5000)
- **Webhook Auto-Setup**: Bot webhook configured automatically on startup
- **Redis Persistence**: Data survives container restarts via Docker volume