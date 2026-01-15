"""
A.B.E.L - Configuration Hybride Local/Cloud
============================================
Priorise les solutions locales et open source.
Fallback vers les APIs cloud si disponibles.
"""

from enum import Enum
from typing import Optional
import os


class RunMode(Enum):
    """Mode d'execution d'A.B.E.L."""
    LOCAL = "local"        # 100% local, pas d'internet requis
    HYBRID = "hybrid"      # Local par defaut, cloud en fallback
    CLOUD = "cloud"        # Utilise les APIs cloud


class ServiceProvider:
    """Configuration d'un service avec fallback."""

    def __init__(
        self,
        name: str,
        local_provider: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        requires_api_key: bool = False,
        is_free: bool = True,
    ):
        self.name = name
        self.local_provider = local_provider
        self.cloud_provider = cloud_provider
        self.requires_api_key = requires_api_key
        self.is_free = is_free


# ============================================================
# CONFIGURATION DES SERVICES - LOCAL FIRST
# ============================================================

SERVICES = {
    # === INTELLIGENCE ARTIFICIELLE ===
    "llm": ServiceProvider(
        name="Large Language Model",
        local_provider="ollama",           # Ollama avec Qwen/Llama/Mistral
        cloud_provider="openai",           # GPT-4o (payant)
        requires_api_key=False,            # Local = pas de cle
        is_free=True,
    ),

    "embeddings": ServiceProvider(
        name="Embeddings/Vectorisation",
        local_provider="sentence-transformers",  # all-MiniLM-L6-v2
        cloud_provider="openai",                 # text-embedding-3-small
        requires_api_key=False,
        is_free=True,
    ),

    # === VOIX ===
    "tts": ServiceProvider(
        name="Text-to-Speech",
        local_provider="piper",            # Piper TTS (open source)
        cloud_provider="elevenlabs",       # ElevenLabs (freemium)
        requires_api_key=False,
        is_free=True,
    ),

    "stt": ServiceProvider(
        name="Speech-to-Text",
        local_provider="whisper",          # OpenAI Whisper local
        cloud_provider="openai-whisper",   # Whisper API
        requires_api_key=False,
        is_free=True,
    ),

    # === BASE DE DONNEES ===
    "database": ServiceProvider(
        name="Base de donnees",
        local_provider="sqlite",           # SQLite pour dev
        cloud_provider="postgresql",       # PostgreSQL
        requires_api_key=False,
        is_free=True,
    ),

    "vector_db": ServiceProvider(
        name="Base vectorielle",
        local_provider="qdrant",           # Qdrant self-hosted
        cloud_provider="qdrant-cloud",     # Qdrant Cloud
        requires_api_key=False,
        is_free=True,
    ),

    "cache": ServiceProvider(
        name="Cache",
        local_provider="memory",           # Cache en memoire
        cloud_provider="redis",            # Redis
        requires_api_key=False,
        is_free=True,
    ),
}


# ============================================================
# APIS 100% GRATUITES (SANS CLE API)
# ============================================================

FREE_APIS = {
    # === METEO ===
    "weather": {
        "provider": "open-meteo",
        "url": "https://api.open-meteo.com/v1/forecast",
        "docs": "https://open-meteo.com/",
        "rate_limit": "10000/jour",
        "requires_key": False,
    },

    # === CRYPTO ===
    "crypto": {
        "provider": "coingecko",
        "url": "https://api.coingecko.com/api/v3",
        "docs": "https://www.coingecko.com/api/documentation",
        "rate_limit": "10-30/min",
        "requires_key": False,
    },

    # === DEVISES ===
    "currency": {
        "provider": "frankfurter",
        "url": "https://api.frankfurter.app",
        "docs": "https://www.frankfurter.app/docs/",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === MUSIQUE (recherche) ===
    "music_search": {
        "provider": "itunes",
        "url": "https://itunes.apple.com/search",
        "docs": "https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/",
        "rate_limit": "20/min",
        "requires_key": False,
    },

    # === PAROLES ===
    "lyrics": {
        "provider": "lyrics.ovh",
        "url": "https://api.lyrics.ovh/v1",
        "docs": "https://lyricsovh.docs.apiary.io/",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === ANIME ===
    "anime": {
        "provider": "jikan",
        "url": "https://api.jikan.moe/v4",
        "docs": "https://docs.api.jikan.moe/",
        "rate_limit": "3/sec",
        "requires_key": False,
    },

    # === FILMS ===
    "movies": {
        "provider": "omdb",  # Avec cle gratuite
        "url": "https://www.omdbapi.com/",
        "docs": "https://www.omdbapi.com/",
        "rate_limit": "1000/jour (gratuit)",
        "requires_key": True,  # Mais gratuit
        "free_tier": True,
    },

    # === TRADUCTION ===
    "translation": {
        "provider": "mymemory",
        "url": "https://api.mymemory.translated.net/get",
        "docs": "https://mymemory.translated.net/doc/spec.php",
        "rate_limit": "5000 mots/jour",
        "requires_key": False,
    },

    # === WIKIPEDIA ===
    "wikipedia": {
        "provider": "wikipedia",
        "url": "https://fr.wikipedia.org/api/rest_v1",
        "docs": "https://www.mediawiki.org/wiki/REST_API",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === CITATIONS ===
    "quotes": {
        "provider": "quotable",
        "url": "https://api.quotable.io",
        "docs": "https://github.com/lukePeavey/quotable",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === BLAGUES ===
    "jokes": {
        "provider": "jokeapi",
        "url": "https://v2.jokeapi.dev/joke",
        "docs": "https://jokeapi.dev/",
        "rate_limit": "120/min",
        "requires_key": False,
    },

    # === IP/GEOLOC ===
    "geolocation": {
        "provider": "ip-api",
        "url": "http://ip-api.com/json",
        "docs": "https://ip-api.com/docs/",
        "rate_limit": "45/min",
        "requires_key": False,
    },

    # === QR CODE ===
    "qrcode": {
        "provider": "goqr",
        "url": "https://api.qrserver.com/v1/create-qr-code/",
        "docs": "https://goqr.me/api/",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === HACKER NEWS ===
    "hackernews": {
        "provider": "hackernews",
        "url": "https://hacker-news.firebaseio.com/v0",
        "docs": "https://github.com/HackerNews/API",
        "rate_limit": "Illimite",
        "requires_key": False,
    },

    # === GITHUB (public) ===
    "github": {
        "provider": "github",
        "url": "https://api.github.com",
        "docs": "https://docs.github.com/rest",
        "rate_limit": "60/heure (sans auth)",
        "requires_key": False,
    },

    # === DICTIONNAIRE ===
    "dictionary": {
        "provider": "dictionaryapi",
        "url": "https://api.dictionaryapi.dev/api/v2/entries",
        "docs": "https://dictionaryapi.dev/",
        "rate_limit": "Illimite",
        "requires_key": False,
    },
}


# ============================================================
# CONFIGURATION OLLAMA (LLM LOCAL)
# ============================================================

OLLAMA_CONFIG = {
    "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "models": {
        "default": "qwen2.5:7b",           # Modele par defaut
        "light": "qwen2.5:3b",             # Version legere
        "coding": "qwen2.5-coder:7b",      # Specialise code
        "fast": "qwen2.5:1.5b",            # Ultra rapide
    },
    "download_command": "ollama pull {model}",
}


# ============================================================
# CONFIGURATION PIPER TTS (LOCAL)
# ============================================================

PIPER_CONFIG = {
    "voices": {
        "fr": "fr_FR-upmc-medium",         # Francais
        "en": "en_US-lessac-medium",       # Anglais
    },
    "download_url": "https://github.com/rhasspy/piper/releases",
}


# ============================================================
# CONFIGURATION WHISPER (STT LOCAL)
# ============================================================

WHISPER_CONFIG = {
    "models": {
        "tiny": "tiny",           # 39M params - ultra rapide
        "base": "base",           # 74M params - rapide
        "small": "small",         # 244M params - equilibre
        "medium": "medium",       # 769M params - precis
    },
    "default_model": "base",
    "language": "fr",
}


def get_run_mode() -> RunMode:
    """Determine le mode d'execution."""
    mode = os.getenv("ABEL_RUN_MODE", "hybrid").lower()
    return RunMode(mode)


def is_local_available(service: str) -> bool:
    """Verifie si un service local est disponible."""
    if service == "llm":
        # Verifier si Ollama est en cours d'execution
        try:
            import httpx
            response = httpx.get(f"{OLLAMA_CONFIG['host']}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    elif service == "tts":
        # Verifier si Piper est installe
        import shutil
        return shutil.which("piper") is not None

    elif service == "stt":
        # Whisper est toujours disponible via Python
        try:
            import whisper
            return True
        except ImportError:
            return False

    return True


def get_provider(service: str) -> str:
    """Retourne le provider a utiliser pour un service."""
    mode = get_run_mode()
    svc = SERVICES.get(service)

    if not svc:
        raise ValueError(f"Service inconnu: {service}")

    if mode == RunMode.LOCAL:
        return svc.local_provider

    elif mode == RunMode.CLOUD:
        return svc.cloud_provider

    else:  # HYBRID
        if is_local_available(service):
            return svc.local_provider
        return svc.cloud_provider
