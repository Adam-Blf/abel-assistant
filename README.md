# A.B.E.L. - Assistant IA Mobile

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React Native](https://img.shields.io/badge/React%20Native-Expo-blue.svg)](https://expo.dev/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)

**A.B.E.L.** (Advanced Biometric Enhanced Liaison) est un assistant IA mobile full-stack open source, propulsé par Google Gemini avec des fonctionnalités vocales, visuelles et mémoire contextuelle.

## Features

- **Chat IA** - Conversation intelligente avec Gemini 1.5 Flash
- **Voice** - Interaction vocale STT/TTS multimodale
- **Vision** - Analyse d'images en temps réel avec Gemini 1.5 Pro
- **Memory** - Mémoire contextuelle RAG avec pgvector
- **Tools** - Intégration APIs externes (météo, actualités, etc.)
- **Security** - Authentification biométrique, session timeout, chiffrement

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+ / FastAPI |
| Mobile | React Native / Expo SDK 52+ |
| IA | Google Gemini 1.5 Flash/Pro |
| BDD | Supabase (PostgreSQL + pgvector) |
| Auth | Supabase Auth + JWT |
| UI | NativeWind (Tailwind CSS) |

## Quick Start

### Backend

```bash
cd backend
poetry install
cp .env.example .env
# Configurer les variables d'environnement
poetry run uvicorn app.main:app --reload
```

### Mobile

```bash
cd mobile
npm install
cp .env.example .env
npx expo start
```

## Architecture

```
abel-assistant/
├── backend/          # API Python FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints REST
│   │   ├── services/ # Gemini, Supabase, Memory
│   │   └── core/     # Security, middleware
│   └── tests/
├── mobile/           # App React Native Expo
│   ├── app/          # Screens (Expo Router)
│   └── src/          # Components, hooks, services
└── docs/             # Documentation
```

## Security

- HTTPS obligatoire
- Headers sécurisés (HSTS, X-Frame-Options, CSP)
- Rate limiting par endpoint
- Validation stricte des entrées (Pydantic)
- Biométrie (Face ID / Touch ID)
- Session timeout (15 min)
- Stockage sécurisé des tokens (Keychain/Keystore)

## License

MIT License - voir [LICENSE](LICENSE)

## Contributing

Voir [CONTRIBUTING.md](CONTRIBUTING.md)
