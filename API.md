# API Documentation

## Overview

This backend provides REST API endpoints for Telegram Mini Apps with secure authentication and user data management. The API uses Docker Compose for deployment and includes Redis for persistent storage.

## Base URL

```
Production: https://arena-back.sh-development.ru/api
Development: http://localhost:9002/api
```

## Authentication

All API endpoints (except webhooks) require Telegram Web App authentication via the `X-Telegram-Init-Data` header.

### Authentication Header
```http
X-Telegram-Init-Data: query_id=AAHdF6IQAAAAAN0X...
```

This header contains the cryptographically signed init data from Telegram Web App. The backend validates this data using HMAC-SHA256 signature verification.

## CORS Configuration

The backend is configured with permissive CORS for Telegram WebApp compatibility:

- **Allowed Origins:** All origins (`*`) - required for Telegram WebApp environment
- **Allowed Methods:** All methods
- **Allowed Headers:** All headers
- **Credentials:** Supported

**Note:** While CORS is permissive, security is maintained through Telegram's cryptographic validation of init data.

## API Endpoints

### 1. Get User Data

**Endpoint:** `POST /api/user/get_data`

**Description:** Retrieve or create user profile data.

**Headers:**
```http
Content-Type: application/json
X-Telegram-Init-Data: <telegram_init_data>
```

**Request Body:** Empty JSON object `{}`

**Response (200 - Existing User):**
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

**Response (201 - New User Created):**
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

**Error Responses:**
```json
// 401 - Authentication failed
{
  "error": "Invalid authentication data"
}

// 500 - Server error
{
  "error": "Bot token not configured"
}
```

### 2. Update User Data

**Endpoint:** `POST /api/user/up_data`

**Description:** Update user profile and application-specific data.

**Headers:**
```http
Content-Type: application/json
X-Telegram-Init-Data: <telegram_init_data>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "user_data": {
    "level": 5,
    "score": 1250,
    "preferences": {
      "theme": "dark",
      "notifications": true
    }
  }
}
```

**Response (200):**
```json
{
  "user": {
    "telegram_id": "123456789",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "language_code": "en",
    "user_data": {
      "level": 5,
      "score": 1250,
      "preferences": {
        "theme": "dark",
        "notifications": true
      }
    },
    "created_at": "2025-01-15T10:30:00.000000",
    "updated_at": "2025-01-15T11:45:00.000000"
  }
}
```

**Error Responses:**
```json
// 400 - Validation error
{
  "error": "user_data is too large (max 10KB)"
}

// 401 - Authentication failed
{
  "error": "Invalid authentication data"
}

// 404 - User not found
{
  "error": "User not found"
}
```

### 3. API Health Check

**Endpoint:** `GET /api/health`

**Description:** Check API and database connectivity status.

**Headers:** None required

**Response (200):**
```json
{
  "status": "healthy",
  "redis": "connected",
  "timestamp": null
}
```

**Response (500 - Unhealthy):**
```json
{
  "status": "unhealthy",
  "redis": "disconnected",
  "error": "Redis connection failed"
}
```

## Data Structure

### User Object
```typescript
interface User {
  telegram_id: string;        // Telegram user ID
  first_name: string;         // User's first name
  last_name: string;          // User's last name (optional)
  username: string;           // Telegram username (optional)
  language_code: string;      // User's language preference
  user_data: object;          // Application-specific data (max 10KB)
  created_at: string;         // ISO timestamp
  updated_at: string;         // ISO timestamp
}
```

### User Data Field
The `user_data` field is a flexible JSON object where you can store application-specific information:

```json
{
  "user_data": {
    "game_progress": {
      "level": 15,
      "experience": 2500,
      "achievements": ["first_win", "level_10"]
    },
    "settings": {
      "theme": "dark",
      "sound_enabled": true,
      "language": "en"
    },
    "analytics": {
      "sessions_count": 45,
      "last_active": "2025-01-15T10:30:00Z"
    }
  }
}
```

**Limitations:**
- Maximum size: 10KB (JSON serialized)
- Must be valid JSON object
- No sensitive data (passwords, tokens, etc.)

## Error Handling

### HTTP Status Codes
- **200 OK:** Request successful
- **201 Created:** User created successfully
- **400 Bad Request:** Invalid request data
- **401 Unauthorized:** Authentication failed
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

### Error Response Format
```json
{
  "error": "Error description"
}
```

## Frontend Integration Examples

### JavaScript/TypeScript

```javascript
class TelegramAPI {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, data = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': window.Telegram.WebApp.initData
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API request failed');
    }

    return response.json();
  }

  async getUserData() {
    return this.request('/user/get_data');
  }

  async updateUserData(userData) {
    return this.request('/user/up_data', userData);
  }

  async checkHealth() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }
}

// Usage
const api = new TelegramAPI('https://arena-back.sh-development.ru/api');

// Get user data
try {
  const { user } = await api.getUserData();
  console.log('User:', user);
} catch (error) {
  console.error('Failed to get user:', error.message);
}

// Update user data
try {
  const { user } = await api.updateUserData({
    user_data: {
      level: 10,
      score: 1500
    }
  });
  console.log('Updated user:', user);
} catch (error) {
  console.error('Failed to update user:', error.message);
}
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

export function useUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const api = new TelegramAPI(process.env.REACT_APP_API_URL);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      setLoading(true);
      const { user } = await api.getUserData();
      setUser(user);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (userData) => {
    try {
      const { user } = await api.updateUserData(userData);
      setUser(user);
      return user;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return { user, loading, error, updateUser, reload: loadUser };
}
```

## Docker Development

### Environment Variables

Create `.env` file with required variables:

```bash
# Required
PROJECT_NAME=arena
SECRET_KEY=your-secure-secret-key-change-in-production
BOT_TOKEN=your-telegram-bot-token-here
FRONTEND_URL=https://shumilovsergey.github.io/arena-front-sh
BACKEND_URL=https://arena-back.sh-development.ru
FLASK_PORT=9002

# Optional
FLASK_DEBUG=false
SHUMILOV_WEBSITE=https://sh-development.ru
PYTHONUNBUFFERED=1
```

### Development Commands

```bash
# Start development environment
docker-compose up --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean restart
docker-compose down -v --remove-orphans
docker-compose up --build
```

### Health Monitoring

Check if the backend is running:

```bash
# Basic health check
curl http://localhost:9002/health

# API health check
curl http://localhost:9002/api/health

# Check Docker containers
docker-compose ps
```

## Security Considerations

1. **Authentication:** All requests validated using Telegram's cryptographic signature
2. **CORS:** Restricted to Telegram domains and your frontend URL
3. **Data Isolation:** Users can only access their own data
4. **Input Validation:** All user inputs sanitized and size-limited
5. **Network Security:** Redis isolated in private Docker network

## Support and Debugging

### Common Issues

1. **CORS Errors:** Backend now uses permissive CORS for Telegram WebApp compatibility
2. **Authentication Failures:** Verify `X-Telegram-Init-Data` header is properly set from Telegram WebApp
3. **Connection Issues:** Check Docker containers are running and healthy with `docker-compose ps`
4. **Data Validation:** Ensure `user_data` is valid JSON under 10KB
5. **Port Issues:** Make sure port 9002 is available and not blocked by firewall

### Debug Mode

Enable debug mode in development:

```bash
FLASK_DEBUG=true
```

This will provide detailed error messages and request logging.

## Arena LoL Project Setup

### Current Configuration

This backend is configured for the Arena LoL Telegram Mini App:

- **Frontend URL:** `https://shumilovsergey.github.io/arena-front-sh`
- **Backend URL:** `https://arena-back.sh-development.ru`
- **Local Development Port:** `9002`

### Frontend Integration for Arena LoL

The frontend should use these exact endpoints:

```javascript
// Production API base URL
const API_BASE_URL = 'https://arena-back.sh-development.ru/api';

// For local development
const API_BASE_URL = 'http://localhost:9002/api';

// Example usage in Arena frontend
class ArenaAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async getUserProfile() {
    const response = await fetch(`${this.baseURL}/user/get_data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': window.Telegram.WebApp.initData
      },
      body: JSON.stringify({})
    });

    const data = await response.json();
    return data.user;
  }

  async saveGameProgress(gameData) {
    const response = await fetch(`${this.baseURL}/user/up_data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': window.Telegram.WebApp.initData
      },
      body: JSON.stringify({
        user_data: {
          ...gameData,
          last_updated: new Date().toISOString()
        }
      })
    });

    const data = await response.json();
    return data.user;
  }
}
```

### Arena-Specific Data Structure

For the Arena LoL game, you can store game-specific data in the `user_data` field:

```json
{
  "user_data": {
    "arena": {
      "level": 15,
      "experience": 2500,
      "coins": 1200,
      "champions": {
        "owned": ["ashe", "garen", "lux"],
        "active": "ashe"
      },
      "matches": {
        "total": 45,
        "wins": 28,
        "losses": 17
      },
      "achievements": ["first_win", "level_10", "champion_master"],
      "settings": {
        "sound_enabled": true,
        "graphics_quality": "high",
        "auto_battle": false
      }
    },
    "session": {
      "current_match_id": null,
      "last_active": "2025-01-15T10:30:00Z",
      "session_count": 156
    }
  }
}
```

### CORS Fix Applied

The backend has been updated with permissive CORS settings to resolve the frontend connection issues:

- **Before:** Restrictive CORS with specific origins and headers
- **After:** Permissive CORS (`CORS(app)`) matching the working Telegram Drive backend
- **Security:** Maintained through Telegram's cryptographic validation

### Testing the Integration

1. **Backend Status:** Check if backend is running
   ```bash
   curl https://arena-back.sh-development.ru/health
   ```

2. **API Connectivity:** Test API health
   ```bash
   curl https://arena-back.sh-development.ru/api/health
   ```

3. **Frontend Testing:** Open your frontend at `https://shumilovsergey.github.io/arena-front-sh` in Telegram WebApp and check browser dev tools for any remaining errors.