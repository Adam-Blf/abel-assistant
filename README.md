# A.B.E.L - Autonomous Backend Entity for Living

<div align="center">

![A.B.E.L Logo](https://img.shields.io/badge/A.B.E.L-v2.0-00F0FF?style=for-the-badge&logo=robot&logoColor=white)

**L'Assistant IA Personnel Ultime**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

</div>

---

## Vue d'ensemble

A.B.E.L est un assistant IA personnel complet qui integre **1400+ APIs publiques** et **120+ fonctionnalites** pour devenir votre compagnon numerique ultime. Construit avec une architecture moderne et evolutive.

### Capacites Principales

- **Intelligence Conversationnelle** - GPT-4o avec memoire contextuelle RAG
- **Interaction Vocale** - Reconnaissance vocale (Whisper) et synthese vocale (ElevenLabs)
- **Integration Google Complete** - Gmail, Drive, Docs, Sheets, Calendar, Photos, Tasks, YouTube
- **Productivite** - Gestion emails, calendrier, taches, notes
- **Divertissement** - Musique (Deezer, Spotify), Films (TMDB), Anime, Jeux
- **Finance** - Crypto, Actions, Devises en temps reel
- **Actualites** - NewsAPI, Hacker News, Reddit
- **Developpement** - GitHub, GitLab, documentation technique
- **Domotique** - Home Assistant, Philips Hue
- **Communication** - Discord, Telegram, Slack, SMS

---

## Architecture

```
A.B.E.L/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # Routes API REST
│   │   ├── brain/             # Services IA (RAG, Chat)
│   │   ├── core/              # Configuration, DB, Redis
│   │   ├── models/            # Modeles SQLAlchemy
│   │   ├── modules/           # Modules (Productivite, Social)
│   │   ├── senses/            # Audio (STT/TTS)
│   │   └── services/          # Services par domaine
│   │       ├── entertainment/ # Musique, Films, Anime, Jeux
│   │       ├── finance/       # Crypto, Actions, Devises
│   │       ├── google/        # Suite Google complete
│   │       └── utilities/     # Meteo, News, Traduction
│   ├── tests/
│   └── pyproject.toml
├── frontend/                   # Next.js 14 Dashboard
│   ├── app/
│   ├── components/
│   └── lib/
├── docker/
└── docker-compose.yml
```

---

## Services Integres

### Google Workspace
| Service | Fonctionnalites |
|---------|-----------------|
| Gmail | Lecture, envoi, recherche, labels, pieces jointes |
| Drive | Upload, download, partage, dossiers, recherche |
| Docs | Creation, edition, formatage, export |
| Sheets | Lecture/ecriture, formules, graphiques, formatage |
| Calendar | Evenements, rappels, invitations |
| Photos | Albums, recherche, upload, partage |
| Tasks | Listes, taches, sous-taches, dates d'echeance |
| Contacts | CRUD, groupes, recherche |
| YouTube | Recherche, playlists, subscriptions, trending |

### Divertissement
| Service | APIs |
|---------|------|
| Musique | Deezer, iTunes, MusicBrainz, Lyrics.ovh |
| Films/Series | TMDB, TVMaze |
| Anime | Jikan (MyAnimeList), AniList, Kitsu |
| Jeux | RAWG, CheapShark, Free-to-Game |

### Finance
| Service | APIs |
|---------|------|
| Crypto | CoinGecko, CoinCap, Binance |
| Actions | Alpha Vantage, Yahoo Finance, Finnhub |
| Devises | Frankfurter, ExchangeRate-API |

### Utilitaires
| Service | APIs |
|---------|------|
| Meteo | OpenWeatherMap, Open-Meteo |
| News | NewsAPI, Hacker News, Reddit |
| Traduction | MyMemory, Lingva, LibreTranslate |
| Outils | QR Code, URL Shortener, Password Generator |

---

## Installation Rapide

### Prerequis

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL, Redis, Qdrant (via Docker)

### 1. Cloner le repository

```bash
git clone https://github.com/Adam-Blf/A.B.E.L.git
cd A.B.E.L
```

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp backend/.env.example backend/.env

# Editer avec vos cles API
nano backend/.env
```

### 3. Lancer avec Docker

```bash
# Demarrer tous les services
docker-compose up -d

# Verifier les logs
docker-compose logs -f
```

### 4. Acceder a l'application

- **API Backend**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:3000
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Adminer (DB)**: http://localhost:8080

---

## Configuration des APIs

### APIs Gratuites (Aucune cle requise)

Ces APIs fonctionnent sans configuration :
- Deezer, iTunes, MusicBrainz
- Jikan (MyAnimeList), AniList, Kitsu
- CoinGecko, CoinCap
- Frankfurter (Devises)
- Open-Meteo (Meteo)
- Hacker News, Reddit
- Lingva (Traduction)

### APIs avec Cle Gratuite

Creez un compte gratuit pour obtenir une cle :

| Service | URL d'inscription |
|---------|-------------------|
| OpenAI | https://platform.openai.com |
| TMDB | https://www.themoviedb.org/settings/api |
| NewsAPI | https://newsapi.org |
| OpenWeatherMap | https://openweathermap.org/api |
| RAWG | https://rawg.io/apidocs |
| Alpha Vantage | https://www.alphavantage.co/support/#api-key |

### Google OAuth Setup

1. Creez un projet sur [Google Cloud Console](https://console.cloud.google.com)
2. Activez les APIs requises (Gmail, Drive, Calendar, etc.)
3. Creez des identifiants OAuth 2.0
4. Configurez les URIs de redirection
5. Copiez Client ID et Client Secret dans `.env`

---

## Utilisation

### API Endpoints Principaux

```bash
# Chat avec memoire
POST /api/chat
{
  "message": "Bonjour, quelles sont mes taches aujourd'hui ?",
  "context": "productivity"
}

# Recherche musique Deezer
GET /api/entertainment/music/search?q=artist_name

# Obtenir prix crypto
GET /api/finance/crypto/price/bitcoin

# Meteo
GET /api/utilities/weather?city=Paris

# Actualites tech
GET /api/utilities/news/tech
```

### WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.send(JSON.stringify({ message: "Hello A.B.E.L!" }));
```

---

## Fonctionnalites (120+)

<details>
<summary><b>Communication (15)</b></summary>

- Email Summarizer
- Smart Reply Suggestions
- Email Scheduler
- Meeting Transcription
- Voice Commands
- Multi-language Chat
- Notification Manager
- Contact Insights
- Email Templates
- Calendar Sync
- Meeting Notes
- Follow-up Reminders
- Email Analytics
- Spam Filter
- Priority Inbox

</details>

<details>
<summary><b>Productivite (20)</b></summary>

- Task Automation
- Smart Scheduling
- Document Generator
- Note Taking
- Project Tracker
- Time Tracking
- Habit Tracker
- Goal Setting
- Focus Mode
- Pomodoro Timer
- File Organizer
- Bookmark Manager
- Password Manager
- Clipboard History
- Quick Actions
- Template Library
- Workflow Builder
- Report Generator
- Data Export
- Backup Manager

</details>

<details>
<summary><b>Finance (15)</b></summary>

- Crypto Portfolio
- Stock Watchlist
- Price Alerts
- Investment Tracker
- Budget Planner
- Expense Tracker
- Bill Reminders
- Tax Calculator
- Currency Converter
- Market News
- Financial Reports
- Savings Goals
- Debt Tracker
- Net Worth Calculator
- Trading Signals

</details>

<details>
<summary><b>Divertissement (20)</b></summary>

- Music Recommender
- Playlist Generator
- Movie Finder
- TV Show Tracker
- Anime Recommender
- Game Deals Finder
- Event Finder
- Recipe Finder
- Book Recommender
- Podcast Finder
- News Aggregator
- Meme Generator
- Quiz Generator
- Trivia Games
- Story Generator
- Art Generator
- Music Player
- Video Summarizer
- Lyrics Finder
- Concert Alerts

</details>

<details>
<summary><b>Developpement (20)</b></summary>

- Code Reviewer
- Bug Tracker
- Documentation Generator
- API Tester
- Database Manager
- Log Analyzer
- Performance Monitor
- Deployment Manager
- Version Control
- Code Snippets
- Regex Tester
- JSON Formatter
- API Documentation
- Environment Manager
- Dependency Checker
- Security Scanner
- Code Formatter
- Git Assistant
- CI/CD Monitor
- Error Tracker

</details>

<details>
<summary><b>Utilitaires (20)</b></summary>

- Weather Forecast
- Translation
- Unit Converter
- Calculator
- QR Generator
- URL Shortener
- Image Converter
- PDF Tools
- Text Analyzer
- Hash Generator
- Color Picker
- Lorem Ipsum
- Countdown Timer
- Stopwatch
- World Clock
- Calendar
- Random Generator
- IP Lookup
- DNS Lookup
- Speed Test

</details>

<details>
<summary><b>Domotique (10)</b></summary>

- Light Control
- Thermostat
- Security Camera
- Door Lock
- Scene Manager
- Energy Monitor
- Voice Control
- Automation Rules
- Device Status
- Alerts

</details>

---

## Stack Technique

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Vector DB**: Qdrant
- **Task Queue**: Celery

### Frontend
- **Framework**: Next.js 14
- **UI**: shadcn/ui + Tailwind CSS
- **State**: Zustand
- **Animation**: Framer Motion
- **Charts**: Recharts

### IA/ML
- **LLM**: OpenAI GPT-4o
- **Embeddings**: text-embedding-3-small
- **STT**: OpenAI Whisper
- **TTS**: ElevenLabs

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx (production)

---

## Contribuer

Les contributions sont les bienvenues !

```bash
# Fork le repo
# Creer une branche feature
git checkout -b feature/amazing-feature

# Commit
git commit -m 'feat: add amazing feature'

# Push
git push origin feature/amazing-feature

# Ouvrir une Pull Request
```

---

## License

MIT License

---

## Auteur

**Adam Blf** - [@Adam-Blf](https://github.com/Adam-Blf)

---

<div align="center">

**A.B.E.L** - *Your Ultimate AI Companion*

![Made with Love](https://img.shields.io/badge/Made%20with-Love-ff69b4?style=flat-square)
![Powered by AI](https://img.shields.io/badge/Powered%20by-AI-00F0FF?style=flat-square)

</div>
