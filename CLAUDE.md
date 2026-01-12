# A.B.E.L. - Claude Code Context

## Project Overview

A.B.E.L. (Advanced Biometric Enhanced Liaison) est un assistant IA mobile full-stack open source.

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / Poetry
- **Mobile**: React Native / Expo SDK 52+ / TypeScript
- **AI**: Google Gemini 1.5 Flash (chat), Gemini 1.5 Pro (vision)
- **Database**: Supabase (PostgreSQL + pgvector pour RAG)
- **Auth**: Supabase Auth + JWT + Biometrics
- **Styling**: NativeWind (Tailwind CSS)

## Project Structure

```
abel-assistant/
├── backend/           # Python FastAPI API
│   ├── app/
│   │   ├── main.py
│   │   ├── config/    # Settings, security config
│   │   ├── core/      # Security middleware, auth
│   │   ├── api/v1/    # REST endpoints
│   │   ├── services/  # Gemini, Supabase, Memory, Tools
│   │   ├── schemas/   # Pydantic models
│   │   └── utils/     # Helpers, PII redactor
│   └── tests/
├── mobile/            # React Native Expo app
│   ├── app/           # Expo Router screens
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── store/     # Zustand
│       └── theme/     # NativeWind cyberpunk theme
└── scripts/           # Automation scripts
```

## Critical Security Requirements

1. **NEVER** commit secrets or .env files
2. All inputs must be validated with Pydantic
3. Rate limiting on all endpoints
4. Session timeout: 15 minutes
5. HTTPS only in production
6. PII redaction in logs

## Environment Variables

### Backend (.env)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anon key
- `SUPABASE_SERVICE_KEY` - Supabase service key (secret)
- `GEMINI_API_KEY` - Google Gemini API key (secret)
- `SECRET_KEY` - JWT secret (min 32 chars)

### Mobile (.env)
- `EXPO_PUBLIC_API_URL` - Backend API URL
- `EXPO_PUBLIC_SUPABASE_URL` - Supabase project URL
- `EXPO_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

## Commands

### Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
poetry run pytest
```

### Mobile
```bash
cd mobile
npm install
npx expo start
```

### Sync (Auto-commit)
```bash
./scripts/ops_sync.sh "commit message"
```

## Coding Standards

- Python: PEP 8, type hints, docstrings
- TypeScript: strict mode, no `any`
- All API responses use Pydantic schemas
- Components are functional with hooks
- State management via Zustand

## API Endpoints

- `POST /api/v1/chat` - Send message to Gemini
- `POST /api/v1/voice/stt` - Speech to text
- `POST /api/v1/voice/tts` - Text to speech
- `POST /api/v1/vision/analyze` - Image analysis
- `GET /api/v1/memory` - Retrieve memories (RAG)
- `POST /api/v1/tools/{tool_name}` - Execute external tool
