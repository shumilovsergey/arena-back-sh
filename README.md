# Backend

Flask + Redis + Docker

## Setup

```bash
cp .env.example .env
# Set BOT_TOKEN and WEBHOOK_URL
docker-compose up -d --build
```

## Environment

```
BOT_TOKEN=your-telegram-bot-token
WEBHOOK_URL=https://your-domain.com/api/webhook
FRONTEND_URL=https://your-frontend.com
```

## API

- `GET /api/user` - Get/create user
- `POST /api/user` - Update user
- `POST /api/webhook` - Bot webhook