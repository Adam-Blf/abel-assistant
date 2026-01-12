# A.B.E.L. - Claude Code Context

## Project Overview

A.B.E.L. (Advanced Biometric Enhanced Liaison) est un assistant IA mobile full-stack open source, inspiré de Jarvis. Il apprend de l'utilisateur et fournit une assistance personnalisée via chat, voix et vision.

**Version**: 1.0.0
**License**: MIT
**Repo**: https://github.com/Adam-Blf/abel-assistant

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / Poetry
- **Mobile**: React Native / Expo SDK 52+ / TypeScript
- **AI**: Google Gemini 1.5 Flash (chat/voice), Gemini 1.5 Pro (vision)
- **Database**: Supabase (PostgreSQL + pgvector pour RAG)
- **Auth**: Supabase Auth + JWT + Biometrics (Face ID/Touch ID)
- **Styling**: NativeWind (Tailwind CSS) - Thème Cyberpunk
- **Deployment**: Railway (backend), EAS Build (mobile)

## Project Structure

```
abel-assistant/
├── backend/                    # Python FastAPI API
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config/            # Settings, security config
│   │   ├── core/              # Security middleware, auth, exceptions
│   │   ├── api/v1/endpoints/  # REST endpoints
│   │   │   ├── auth.py        # Login, register, logout
│   │   │   ├── chat.py        # Chat with Gemini
│   │   │   ├── voice.py       # STT/TTS
│   │   │   ├── vision.py      # Image analysis
│   │   │   ├── memory.py      # RAG memory
│   │   │   ├── tools.py       # External APIs
│   │   │   └── health.py      # Health checks
│   │   ├── services/          # Business logic
│   │   │   ├── gemini/        # Gemini client, chat, voice, vision
│   │   │   ├── supabase/      # DB client, auth
│   │   │   ├── memory/        # Embeddings, vector store, RAG
│   │   │   └── tools/         # Weather, news, web search
│   │   ├── schemas/           # Pydantic models
│   │   └── utils/             # Helpers, PII redactor
│   └── tests/
├── mobile/                     # React Native Expo app
│   ├── app/                   # Expo Router screens
│   │   ├── (auth)/            # Login, register
│   │   ├── (tabs)/            # Chat, voice, vision, memory, settings
│   │   └── _layout.tsx        # Root layout
│   └── src/
│       ├── components/        # UI components (chat, vision)
│       ├── hooks/             # Custom hooks (voice, camera, biometric)
│       ├── services/          # API client, storage
│       ├── contexts/          # Auth context
│       ├── store/             # Zustand slices
│       └── theme/             # Colors, cyberpunk theme
├── scripts/                   # Automation
│   └── ops_sync.sh
└── docs/
```

## Features

### 1. Chat (Gemini 1.5 Flash)
- Conversation contextuelle avec mémoire
- RAG pour réponses personnalisées
- WebSocket pour temps réel

### 2. Voice (STT/TTS)
- Transcription audio via Gemini multimodal
- Synthèse vocale native (expo-speech)
- Commandes vocales avec contexte

### 3. Vision (Gemini Pro Vision)
- Analyse d'images
- OCR (extraction de texte)
- Détection d'objets
- Comparaison d'images

### 4. Memory (RAG)
- Embeddings via Gemini
- Vector store PostgreSQL (pgvector)
- Recherche sémantique
- Apprentissage des préférences utilisateur

### 5. External Tools
- **Weather**: Open-Meteo API (gratuit)
- **News**: RSS feeds (Le Monde, HackerNews, BBC)
- **Search**: DuckDuckGo (gratuit)
- Intégration Gemini function calling

### 6. Security
- Authentification biométrique (Face ID/Touch ID)
- Session timeout 15 min
- HTTPS strict
- Rate limiting (slowapi)
- PII redaction dans logs
- expo-secure-store pour tokens

## Critical Security Requirements

1. **NEVER** commit secrets or .env files
2. All inputs validated with Pydantic
3. Rate limiting on all endpoints
4. Session timeout: 15 minutes
5. HTTPS only in production
6. PII redaction in logs
7. Biometric auth for sensitive actions

## Environment Variables

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...  # SECRET

# Gemini
GEMINI_API_KEY=AIza...  # SECRET

# Security
SECRET_KEY=<32+ random chars>  # SECRET

# Server
APP_ENV=production
DEBUG=false
```

### Mobile (.env)
```bash
EXPO_PUBLIC_API_URL=https://your-api.railway.app
EXPO_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## Commands

### Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload  # Dev
poetry run pytest                          # Tests
bandit -r app -ll                          # Security audit
```

### Mobile
```bash
cd mobile
npm install
npx expo start                             # Dev (Expo Go)
eas build --profile development            # Dev build
eas build --profile production             # Prod build
```

### Deployment
```bash
# Backend (Railway)
git push origin master  # Auto-deploy

# Mobile (EAS)
eas build --platform all --profile production
eas submit --platform all
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user

### Chat
- `POST /api/v1/chat` - Send message
- `GET /api/v1/chat/history` - Get history
- `WS /api/v1/chat/ws` - WebSocket

### Voice
- `POST /api/v1/voice/transcribe` - Audio to text
- `POST /api/v1/voice/command` - Process voice command
- `POST /api/v1/voice/speak` - Generate speech text

### Vision
- `POST /api/v1/vision/analyze` - Analyze image
- `POST /api/v1/vision/ocr` - Extract text
- `POST /api/v1/vision/objects` - Detect objects
- `POST /api/v1/vision/compare` - Compare images

### Memory
- `POST /api/v1/memory` - Store memory
- `GET /api/v1/memory/search` - Search memories
- `GET /api/v1/memory` - List memories
- `DELETE /api/v1/memory/{id}` - Delete memory

### Tools
- `GET /api/v1/tools/available` - List tools
- `POST /api/v1/tools/execute` - Execute tool
- `GET /api/v1/tools/weather` - Get weather
- `GET /api/v1/tools/news` - Get news
- `GET /api/v1/tools/search` - Web search
- `GET /api/v1/tools/answer` - Quick answer

### Health
- `GET /health` - Health check
- `GET /health/ready` - Readiness check

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Auth | 5/min |
| Chat | 30/min |
| Voice | 10/min |
| Vision | 5/min |
| Tools | 20-30/min |
| Default | 100/min |

## Coding Standards

- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: strict mode, no `any`
- **API**: Pydantic schemas for all responses
- **Components**: Functional with hooks
- **State**: Zustand slices
- **Commits**: Conventional commits

## Database Schema

### Tables (Supabase)
- `users` - User profiles
- `conversations` - Chat sessions
- `messages` - Chat messages
- `memories` - RAG memory store with embeddings
- `auth.users` - Supabase Auth

### Vector Store
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users,
  content TEXT NOT NULL,
  embedding vector(768),
  category TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);
```

## Supabase Project

- **Project ID**: itgloukhclznuuqjfzuk
- **Region**: eu-central-1

## Railway Deployment

Backend is configured for Railway deployment:
- `Procfile`: gunicorn command
- `railway.json`: build settings
- `nixpacks.toml`: Python 3.11
