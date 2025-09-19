# Backend API Setup Guide

Complete guide for setting up and deploying the backend for your Telegram Web App.

## Quick Start

### 1. Environment Setup

1. **Copy the template backend folder** to your project
2. **Configure environment variables**:

```bash
cd back
cp .env.example .env
```

3. **Edit `.env` file** with your values:

```bash
# Required - Replace ALL "CHANGE-ME" values
PROJECT_NAME=my-telegram-app
FLASK_PORT=5001  # ⚠️ CHANGE: Choose your port (5001, 8080, 9002, etc.)
SECRET_KEY=your-secure-secret-key-here
BOT_TOKEN=123456:ABC-your-bot-token-from-botfather
FRONTEND_URL=https://yourusername.github.io/your-repo
BACKEND_URL=https://your-backend-domain.com

# Optional
FLASK_DEBUG=false
SHUMILOV_WEBSITE=https://your-website.com
PYTHONUNBUFFERED=1
```

### 2. Local Development

```bash
# Start with Docker (recommended)
docker-compose up --build

# Or run without Docker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### 3. Health Check

```bash
# Test backend is running (replace YOUR_PORT with your actual FLASK_PORT)
curl http://localhost:YOUR_PORT/health

# Test API
curl http://localhost:YOUR_PORT/api/health
```

## Environment Variables

### Required Variables (6 total)

| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_NAME` | Your project identifier | `telegram-shop` |
| `FLASK_PORT` | Port for Flask app | `5001`, `8080`, `9002` (choose any available port) |
| `SECRET_KEY` | Flask secret key | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABC-DEF...` |
| `FRONTEND_URL` | Your frontend deployment URL | `https://yourusername.github.io/repo` |
| `BACKEND_URL` | Your backend deployment URL | `https://api.yourdomain.com` |

### Auto-Generated Variables

These are automatically generated from PROJECT_NAME:
- Container names: `${PROJECT_NAME}-flask`, `${PROJECT_NAME}-redis`
- Networks: `${PROJECT_NAME}-private-network`, `${PROJECT_NAME}-public-network`
- Redis data: `./redis_data/` directory

### Example Configurations

#### Local Development
```bash
PROJECT_NAME=myapp-dev
FLASK_PORT=5001  # ⚠️ CHANGE: Choose available port (5001, 8080, 9002, etc.)
SECRET_KEY=dev-secret-key-change-in-production
BOT_TOKEN=123456:ABC-your-bot-token
FRONTEND_URL=http://localhost:8000
BACKEND_URL=http://localhost:5001  # ⚠️ MUST match FLASK_PORT above
```

#### Production Deployment
```bash
PROJECT_NAME=myapp-prod
FLASK_PORT=5001  # ⚠️ CHANGE: Your chosen port or platform default
SECRET_KEY=super-secure-production-key
BOT_TOKEN=123456:ABC-your-bot-token
FRONTEND_URL=https://yourusername.github.io/myapp
BACKEND_URL=https://myapp-backend.herokuapp.com
```

## API Endpoints

### User Management

#### Get User Data
```http
POST /api/user/get_data
Content-Type: application/json
X-Telegram-Init-Data: <telegram_webapp_init_data>

{}
```

Response:
```json
{
  "user": {
    "telegram_id": "123456789",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "language_code": "en",
    "user_data": {},
    "created_at": "2025-01-15T10:30:00.000000",
    "updated_at": "2025-01-15T10:30:00.000000"
  }
}
```

#### Update User Data
```http
POST /api/user/up_data
Content-Type: application/json
X-Telegram-Init-Data: <telegram_webapp_init_data>

{
  "user_data": {
    "level": 10,
    "score": 1500,
    "preferences": {
      "theme": "dark"
    }
  }
}
```

### Health Checks

#### Basic Health
```http
GET /health
```

#### API Health
```http
GET /api/health
```

### Bot Webhook

#### Telegram Webhook
```http
POST /api/webhook
Content-Type: application/json

{
  "update_id": 123,
  "message": {
    "message_id": 456,
    "from": {...},
    "chat": {...},
    "text": "/start"
  }
}
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone your project
git clone <your-repo-url>
cd <your-project>/back

# Setup environment
cp .env.example .env
# Edit .env with your values

# Start development
docker-compose up --build
```

### 2. Code Changes

```bash
# After making code changes
docker-compose down
docker-compose up --build

# Or for faster rebuilds
docker-compose restart backend
```

### 3. View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f redis

# View latest logs
docker-compose logs --tail=50 backend
```

### 4. Database Management

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# View all users
docker-compose exec redis redis-cli SMEMBERS users:index

# View specific user
docker-compose exec redis redis-cli HGETALL user:123456789

# Clear all data
docker-compose exec redis redis-cli FLUSHALL
```

## Deployment Options

### Option 1: Heroku

1. **Install Heroku CLI**
2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set PROJECT_NAME=your-app
   heroku config:set FLASK_PORT=5001  # ⚠️ Use your chosen port
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set BOT_TOKEN=your-bot-token
   heroku config:set FRONTEND_URL=https://yourusername.github.io/repo
   heroku config:set BACKEND_URL=https://your-app.herokuapp.com
   ```

4. **Add Redis addon**:
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 2: Railway

1. **Connect GitHub repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Railway auto-deploys** on git push

### Option 3: Fly.io

1. **Install Fly CLI**
2. **Initialize**:
   ```bash
   fly launch
   ```
3. **Set secrets**:
   ```bash
   fly secrets set SECRET_KEY=your-secret-key
   fly secrets set BOT_TOKEN=your-bot-token
   # ... other secrets
   ```
4. **Deploy**:
   ```bash
   fly deploy
   ```

### Option 4: Digital Ocean App Platform

1. **Connect GitHub repository**
2. **Configure environment variables**
3. **Deploy automatically**

### Option 5: VPS (Ubuntu)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <your-repo>
cd <your-project>/back
cp .env.example .env
# Edit .env with production values
docker-compose up -d --build

# Setup reverse proxy (nginx)
sudo apt install nginx
# Configure nginx to proxy to your Flask port
```

## Configuration Details

### CORS Configuration

The backend uses permissive CORS for Telegram WebApp compatibility:

```python
# In app/__init__.py
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Permissive CORS for Telegram WebApp
    # ...
```

This allows requests from any origin, which is necessary for Telegram WebApp environment.

### Redis Configuration

Redis is configured with:
- **Persistence**: AOF (Append Only File) enabled
- **Data Safety**: Bind mount to `./redis_data/`
- **Network Isolation**: Private Docker network only
- **Health Checks**: Automatic container health monitoring

### Security Features

1. **Telegram Authentication**: Cryptographic validation of WebApp init data
2. **User Data Isolation**: Each user can only access their own data
3. **Input Validation**: All user inputs validated and sanitized
4. **Network Security**: Redis isolated in private Docker network
5. **Data Validation**: User data limited to 10KB maximum

## Troubleshooting

### Common Issues

#### Environment Variables Not Set
```bash
# Error: Required environment variable 'PROJECT_NAME' is not set
# Solution: Edit .env file and replace all CHANGE-ME values
```

#### Port Already in Use
```bash
# Error: Port XXXX is already in use
# Solution: Change FLASK_PORT in .env to a different available port (e.g., 5001, 8080, 9002)
```

#### Redis Connection Failed
```bash
# Check Redis container status
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

#### CORS Errors from Frontend
```bash
# Verify CORS is enabled
# Check that FRONTEND_URL matches actual frontend domain
# Ensure backend is accessible from frontend
```

### Debug Mode

Enable debug mode for development:

```bash
# In .env file
FLASK_DEBUG=true
```

This provides:
- Detailed error messages
- Request/response logging
- Automatic code reloading (when not using Docker)

### Health Monitoring

Set up monitoring for production:

```bash
# Basic health check
curl -f https://your-backend.com/health || echo "Backend down"

# API health check
curl -f https://your-backend.com/api/health || echo "API down"

# Redis connectivity
curl -s https://your-backend.com/api/health | jq '.redis' || echo "Redis down"
```

## Testing

### Unit Tests

```bash
# Run tests (if implemented)
cd back
python -m pytest tests/

# Test with coverage
python -m pytest tests/ --cov=app
```

### API Testing

```bash
# Test with curl (replace YOUR_PORT with your FLASK_PORT)
curl -X POST http://localhost:YOUR_PORT/api/user/get_data \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Init-Data: query_id=..." \
  -d '{}'

# Test with httpie
http POST localhost:YOUR_PORT/api/user/get_data \
  Content-Type:application/json \
  X-Telegram-Init-Data:query_id=... \
  < test_data.json
```

### Load Testing

```bash
# Install hey
go install github.com/rakyll/hey@latest

# Test API endpoint (replace YOUR_PORT with your FLASK_PORT)
hey -n 1000 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://localhost:YOUR_PORT/api/user/get_data
```

## Monitoring and Logging

### Docker Logs

```bash
# Follow all logs
docker-compose logs -f

# Filter specific patterns
docker-compose logs backend | grep ERROR

# Save logs to file
docker-compose logs backend > backend.log
```

### Application Metrics

Consider adding monitoring with:
- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **Datadog**: Application monitoring
- **New Relic**: Performance monitoring

### Log Aggregation

For production, consider:
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Fluentd**: Log collection and forwarding
- **CloudWatch**: AWS logging
- **Google Cloud Logging**: GCP logging

## Security Checklist

Before deploying to production:

- [ ] Change all default values in .env
- [ ] Use strong SECRET_KEY (32+ random characters)
- [ ] Enable HTTPS for production (required by Telegram)
- [ ] Verify bot token is kept secure
- [ ] Test user data isolation
- [ ] Monitor for suspicious API usage
- [ ] Set up log monitoring
- [ ] Configure firewall rules
- [ ] Use environment-specific configurations
- [ ] Regularly update dependencies

## Performance Optimization

### Redis Optimization

```bash
# In docker-compose.yml
command: redis-server --appendonly yes --appendfsync everysec --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Flask Optimization

Consider adding:
- **Gunicorn**: Production WSGI server
- **Redis caching**: Cache frequently accessed data
- **Database indexing**: Optimize Redis key patterns
- **Request compression**: Gzip responses

### Monitoring

```bash
# Monitor container resources
docker stats

# Monitor Redis performance
docker-compose exec redis redis-cli INFO stats
```

## Support

### Working Examples

- **Backend**: https://github.com/shumilovsergey/arena-back-sh
- **Frontend**: https://github.com/shumilovsergey/arena-front-sh

### Documentation References

- Check existing `API.md` for detailed API specification
- Check `backend_note.md` for specific fixes applied
- See `front_api.md` for frontend integration guide

### Next Steps

1. Set up your backend using this guide
2. Configure your frontend using `front_api.md`
3. Test the integration locally
4. Deploy both frontend and backend
5. Configure your Telegram bot webhook