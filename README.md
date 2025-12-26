# A.B.E.L - Autonomous Backend Entity for Living

<div align="center">

![A.B.E.L](https://img.shields.io/badge/A.B.E.L-v1.0.0-00F0FF?style=for-the-badge&labelColor=050505)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=next.js&logoColor=white)

**Un assistant IA personnel avec mémoire, voix, et connexion au monde réel**

</div>

---

## Vision

A.B.E.L est une intelligence artificielle personnelle complète qui combine:

- **Mémoire contextuelle** via RAG (Retrieval-Augmented Generation) avec Qdrant
- **Interaction vocale** bidirectionnelle (Whisper + ElevenLabs)
- **Intégration productivité** (Gmail, Google Calendar)
- **Présence sociale** intelligente (Twitter, Instagram avec analyse de ton)
- **Découverte d'APIs** autonome via public-apis
- **Dashboard cyberpunk** temps réel

## Fonctionnalités

### Cerveau (Brain)
- Mémoire vectorielle avec Qdrant pour le RAG
- Conversations contextuelles avec GPT-4o
- Stockage et rappel intelligent des souvenirs

### Voix (Senses)
- Speech-to-Text avec OpenAI Whisper
- Text-to-Speech avec ElevenLabs
- Conversations vocales complètes

### Productivité (Google)
- Lecture et envoi d'emails via Gmail
- Gestion du calendrier Google
- Notifications en temps réel

### Social Media
- **Twitter/X**: Trends, posts, mentions
- **Instagram**: DMs avec analyse conversationnelle
- Système de directives utilisateur

### API Explorer
- Découverte automatique d'APIs publiques
- Appels dynamiques basés sur le langage naturel

## Architecture

```
A.B.E.L/
├── backend/                 # FastAPI Application
│   └── app/
│       ├── api/            # Routes API
│       ├── brain/          # RAG & Chat Services
│       ├── core/           # Config, DB, Redis
│       ├── models/         # SQLAlchemy Models
│       ├── modules/        # Productivity, Social, APIs
│       └── senses/         # Audio Processing
├── frontend/               # Next.js 14 Dashboard
│   ├── app/               # Pages
│   └── components/        # UI Components
└── docker/                # Docker configs
```

## Installation

### Prérequis

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Démarrage Rapide

```bash
# Cloner le repo
git clone https://github.com/Adam-Blf/A.B.E.L.git
cd A.B.E.L

# Configurer
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer
docker-compose up -d
```

### Accès

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Adminer | http://localhost:8080 |

## Services Docker

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI REST API |
| Postgres | 5432 | Base de données |
| Redis | 6379 | Cache & Celery |
| Qdrant | 6333 | Vector Database |
| Adminer | 8080 | DB Management |

## Configuration

Variables d'environnement clés:

- `OPENAI_API_KEY` - GPT-4 & Whisper
- `ELEVENLABS_API_KEY` - Text-to-Speech
- `GOOGLE_CLIENT_ID` - OAuth Google
- `TWITTER_BEARER_TOKEN` - Twitter API

## API Endpoints

- `POST /chat/` - Chat avec contexte RAG
- `POST /voice/listen` - Speech-to-Text
- `POST /voice/speak` - Text-to-Speech
- `POST /memory/store` - Stocker un souvenir
- `GET /health` - Status système

## Design

Theme cyberpunk:
- Background: `#050505`
- Primary: `#00F0FF`
- Accent: `#FF006E`

---

**Créé par Adam-Blf**
