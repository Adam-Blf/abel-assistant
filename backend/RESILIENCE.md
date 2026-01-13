# A.B.E.L. Backend Resilience Guide

## Overview

The A.B.E.L. backend is now **crash-proof** and designed to never fail during startup, even when critical services are unavailable. This document explains the resilience features and how to use them.

## Key Features

### 1. Graceful Degradation

The application can start and run even when:
- Environment variables are missing
- Supabase is unavailable
- Gemini API key is not configured
- External tools (weather, news, search) fail to initialize

### 2. Mock Mode

When `ALLOW_MOCK_MODE=true` (default), services that fail to initialize will operate in **mock mode**:

- **Supabase Mock Mode**: Returns 503 errors for auth endpoints
- **Gemini Mock Mode**: Returns mock responses instead of AI-generated content
- **Tools Mock Mode**: Application continues without failed tools

### 3. Service Status Monitoring

Check service availability via the `/health/ready` endpoint:

```json
{
  "status": "ready",
  "services": {
    "supabase": "available",
    "gemini": "mock_mode"
  },
  "message": "Some services running in mock mode"
}
```

## Environment Variables

### Required (with defaults)

```bash
# Security - defaults to development key
SECRET_KEY=dev-secret-key-CHANGE-IN-PRODUCTION-min32chars

# Resilience
ALLOW_MOCK_MODE=true  # Set to false in production to fail fast
```

### Optional Services

```bash
# Supabase (auth features disabled if missing)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Gemini (AI features return mock responses if missing)
GEMINI_API_KEY=AIza...

# External APIs (tools disabled if missing)
OPENWEATHER_API_KEY=xxx
NEWS_API_KEY=xxx
```

## Usage Scenarios

### Development Mode (Default)

Start the server without any configuration:

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The server will:
- Use default development SECRET_KEY
- Run Supabase in mock mode
- Run Gemini in mock mode
- Initialize available tools

### Production Mode

Set `ALLOW_MOCK_MODE=false` in production to fail fast when services are unavailable:

```bash
APP_ENV=production
ALLOW_MOCK_MODE=false
SECRET_KEY=<strong-random-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-anon-key>
GEMINI_API_KEY=<your-api-key>
```

If critical services fail, the application will log errors but continue to handle requests that don't require those services.

### Railway Deployment

Railway will automatically use environment variables from the dashboard. The application will:

1. Start successfully even if some env vars are missing
2. Log warnings about missing services
3. Provide degraded functionality
4. Allow you to add env vars later without redeployment crashes

## Service Behavior

### Supabase Mock Mode

When Supabase is unavailable:
- Auth endpoints return 503 Service Unavailable
- Error message: "Authentication service is temporarily unavailable"
- Health check shows: `"supabase": "mock_mode"`

### Gemini Mock Mode

When Gemini API is unavailable:
- Chat returns: `[MOCK RESPONSE] I received your message...`
- Vision returns: `[MOCK RESPONSE] Image analysis not available...`
- Health check shows: `"gemini": "mock_mode"`

### Tools Initialization

Tools are initialized individually:
- If one tool fails, others continue
- Failed tools are logged but don't stop startup
- Health check shows available tools

## Monitoring

### Health Checks

```bash
# Basic health check (always returns 200)
curl http://localhost:8000/health

# Readiness check (shows service status)
curl http://localhost:8000/health/ready
```

### Logs

The application logs service status during startup:

```
INFO: Starting ABEL API server
INFO: Environment: development
INFO: Mock mode allowed: True
WARNING: Entering Supabase MOCK MODE - auth features will be unavailable
INFO: Gemini client initialized successfully
INFO: Tools initialized: ['weather', 'news', 'search']
INFO: Service status: {'supabase': 'mock_mode', 'gemini': 'available'}
```

## Best Practices

### Development

1. Start with no configuration to verify the app boots
2. Add environment variables as needed
3. Use mock mode to develop without external dependencies
4. Check logs to see which services are available

### Staging

1. Set `ALLOW_MOCK_MODE=true`
2. Configure all critical services
3. Monitor `/health/ready` for service status
4. Test degraded mode scenarios

### Production

1. Set `ALLOW_MOCK_MODE=false` for fail-fast behavior
2. Configure all environment variables
3. Monitor health endpoints
4. Set up alerts for service degradation

## Troubleshooting

### Issue: App won't start

Check logs for critical errors:
```bash
poetry run uvicorn app.main:app --log-level debug
```

### Issue: Auth not working

1. Check `/health/ready` endpoint
2. Verify Supabase environment variables
3. Check logs for "Supabase MOCK MODE"

### Issue: AI responses are mocked

1. Check `/health/ready` endpoint
2. Verify `GEMINI_API_KEY` is set
3. Check logs for "Gemini MOCK MODE"

### Issue: Production deployment crashed

1. Ensure `SECRET_KEY` is at least 32 characters
2. Set `ALLOW_MOCK_MODE=false` to fail fast
3. Check Railway logs for initialization errors

## Migration Notes

### From v0.9.x to v1.0.0

The application now:
- Never crashes on startup due to missing env vars
- Provides default SECRET_KEY for development
- Supports mock mode for all services
- Logs all initialization failures

No code changes required, but you can now safely deploy without all environment variables configured.

## Security Notes

1. **Default SECRET_KEY**: Only use in development. Change in production.
2. **Mock Mode in Production**: Set `ALLOW_MOCK_MODE=false` to prevent degraded operation.
3. **Service Unavailability**: Monitor `/health/ready` to detect degraded services.

## API Changes

### Health Endpoints

The `/health/ready` endpoint now returns detailed service status:

**Before:**
```json
{
  "status": "ready",
  "dependencies": {
    "database": "ok",
    "gemini": "ok"
  }
}
```

**After:**
```json
{
  "status": "ready",
  "services": {
    "supabase": "available",
    "gemini": "mock_mode"
  },
  "message": "Some services running in mock mode"
}
```

## Support

For issues or questions:
- Check logs first
- Use `/health/ready` to diagnose
- Review environment variables
- Open an issue on GitHub
