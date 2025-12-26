# A.B.E.L - Instructions pour Claude Code

## Contexte du Projet

A.B.E.L (Autonomous Backend Entity for Living) est un assistant IA personnel complet integrant 1400+ APIs et 120+ fonctionnalites.

## Architecture

```
backend/
├── app/
│   ├── api/                 # Routes FastAPI
│   ├── brain/               # Services IA (RAG, Chat)
│   │   ├── chat_service.py  # GPT-4o integration
│   │   └── memory_service.py # Qdrant RAG
│   ├── core/                # Configuration
│   │   ├── config.py        # Settings Pydantic
│   │   ├── database.py      # SQLAlchemy async
│   │   ├── redis.py         # Redis client
│   │   └── celery_app.py    # Task queue
│   ├── models/              # SQLAlchemy models
│   ├── modules/             # Business modules
│   │   ├── productivity/    # Gmail, Calendar
│   │   └── social/          # Twitter, Instagram
│   ├── senses/              # Audio (STT/TTS)
│   └── services/            # Domain services
│       ├── entertainment/   # Deezer, TMDB, Anime, Games
│       ├── finance/         # Crypto, Stocks, Currency
│       ├── google/          # Drive, Docs, Sheets, etc.
│       └── utilities/       # Weather, News, Translation
```

## Conventions de Code

### Python/FastAPI
- Python 3.11+
- Async/await pour toutes les operations I/O
- Type hints obligatoires
- Pydantic pour la validation
- SQLAlchemy 2.0 style async

### Style
```python
# Imports groupes: stdlib, third-party, local
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from app.core.logging import logger

# Classes avec docstrings
class ServiceName:
    """
    Description du service.
    - Fonctionnalite 1
    - Fonctionnalite 2
    """

    # Constantes en MAJUSCULES
    API_URL = "https://api.example.com"

    # Methodes async avec type hints
    async def method_name(
        self,
        param: str,
        optional_param: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Docstring courte."""
        try:
            # Implementation
            async with httpx.AsyncClient() as client:
                response = await client.get(...)
                return response.json()
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
```

## Commandes de Developpement

```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up -d
docker-compose logs -f backend

# Tests
poetry run pytest
poetry run pytest --cov=app

# Linting
poetry run ruff check .
poetry run black .
```

## Services Principaux

### Brain (IA)
- `chat_service.py` - Chat GPT-4o avec contexte RAG
- `memory_service.py` - Stockage vectoriel Qdrant

### Google Services
- `drive_service.py` - Fichiers, dossiers, partage
- `docs_service.py` - Documents
- `sheets_service.py` - Tableurs
- `photos_service.py` - Photos
- `tasks_service.py` - Taches
- `contacts_service.py` - Contacts
- `youtube_service.py` - Videos

### Entertainment
- `music_service.py` - Deezer, iTunes, Lyrics
- `movie_service.py` - TMDB, TVMaze
- `anime_service.py` - Jikan, AniList, Kitsu
- `games_service.py` - RAWG, CheapShark

### Finance
- `crypto_service.py` - CoinGecko, Binance
- `stock_service.py` - Alpha Vantage, Finnhub
- `currency_service.py` - Frankfurter

### Utilities
- `weather_service.py` - OpenWeatherMap, Open-Meteo
- `news_service.py` - NewsAPI, HackerNews, Reddit
- `translation_service.py` - MyMemory, Lingva
- `tools_service.py` - QR, URL, Passwords

## Variables d'Environnement Cles

```
OPENAI_API_KEY          # GPT-4o, Whisper
ELEVENLABS_API_KEY      # Text-to-Speech
GOOGLE_CLIENT_ID        # OAuth Google
GOOGLE_CLIENT_SECRET    # OAuth Google
TMDB_API_KEY           # Films
NEWS_API_KEY           # Actualites
OPENWEATHERMAP_API_KEY # Meteo
```

## Endpoints API

```
POST /api/chat          # Chat avec RAG
POST /api/voice/listen  # Speech-to-Text
POST /api/voice/speak   # Text-to-Speech
GET  /api/health        # Health check

# Entertainment
GET  /api/entertainment/music/search
GET  /api/entertainment/movies/popular
GET  /api/entertainment/anime/top

# Finance
GET  /api/finance/crypto/{coin_id}
GET  /api/finance/stocks/{symbol}
GET  /api/finance/currency/convert

# Utilities
GET  /api/utilities/weather
GET  /api/utilities/news/tech
POST /api/utilities/translate
```

## Priorites de Developpement

1. **Stabilite** - Gestion des erreurs, logging
2. **Performance** - Caching Redis, async
3. **Securite** - Validation, rate limiting
4. **UX** - Reponses rapides, feedback clair

## Notes Importantes

- Toujours utiliser `httpx.AsyncClient` avec context manager
- Logger les erreurs avec `logger.error()`
- Retourner des valeurs par defaut en cas d'erreur ([], {}, None)
- Timeouts de 10s pour les appels API externes
- Utiliser les APIs gratuites en priorite
