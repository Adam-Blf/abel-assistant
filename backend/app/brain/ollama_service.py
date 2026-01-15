"""
A.B.E.L - Service Ollama (LLM Local)
====================================
Integration avec Ollama pour l'inference LLM 100% locale.
Aucune API key requise, aucune donnee envoyee sur internet.
"""

import os
from typing import Optional, List, Dict, Any, AsyncGenerator
import httpx

from app.core.logging import logger


class OllamaService:
    """
    Service d'inference LLM local via Ollama.

    Modeles recommandes:
    - qwen2.5:7b      : Assistant general (7B params)
    - qwen2.5:3b      : Version legere (3B params)
    - qwen2.5-coder:7b: Specialise code
    - llama3.2:3b     : Meta Llama (3B params)
    - mistral:7b      : Mistral AI (7B params)
    """

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.timeout = 120.0  # LLM peut etre lent

    async def is_available(self) -> bool:
        """Verifie si Ollama est en cours d'execution."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modeles installes."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            logger.error(f"Ollama list_models error: {e}")
            return []

    async def pull_model(self, model: str) -> bool:
        """Telecharge un modele."""
        try:
            async with httpx.AsyncClient(timeout=3600) as client:  # 1h timeout
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model},
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama pull_model error: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """
        Genere une reponse complete.

        Args:
            prompt: Le message utilisateur
            model: Modele a utiliser (defaut: qwen2.5:7b)
            system: Message systeme
            temperature: Creativite (0-1)
            max_tokens: Longueur max de la reponse
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                data = response.json()
                return data.get("response")

        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            return None

    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Genere une reponse en streaming.

        Usage:
            async for chunk in ollama.generate_stream("Bonjour"):
                print(chunk, end="", flush=True)
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]

        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield f"[Erreur: {e}]"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Chat multi-tour (format OpenAI).

        Args:
            messages: [{"role": "user/assistant/system", "content": "..."}]
            model: Modele a utiliser
            temperature: Creativite
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                data = response.json()
                return data.get("message", {}).get("content")

        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return None

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Chat multi-tour en streaming."""
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content

        except Exception as e:
            logger.error(f"Ollama chat_stream error: {e}")
            yield f"[Erreur: {e}]"

    async def embeddings(
        self,
        text: str,
        model: str = "nomic-embed-text",
    ) -> Optional[List[float]]:
        """
        Genere des embeddings pour le RAG.

        Modeles d'embeddings:
        - nomic-embed-text : 768 dimensions, rapide
        - mxbai-embed-large: 1024 dimensions, precis
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": model, "prompt": text},
                )
                data = response.json()
                return data.get("embedding")

        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            return None


# Instance globale
ollama_service = OllamaService()


# ============================================================
# SYSTEM PROMPTS POUR A.B.E.L
# ============================================================

ABEL_SYSTEM_PROMPT = """Tu es A.B.E.L (Autonomous Backend Entity for Living), un assistant IA personnel.

Caracteristiques:
- Tu es helpful, concis et precis
- Tu reponds en francais par defaut
- Tu peux aider avec: productivite, code, finance, divertissement, utilitaires
- Tu as acces a des outils locaux et APIs gratuites

Style:
- Reponses courtes et directes
- Utilise des listes pour la clarte
- Propose des actions concretes
- Pas de blabla inutile

Tu tournes en local sur la machine de l'utilisateur. Aucune donnee n'est envoyee sur internet."""


ABEL_CODER_PROMPT = """Tu es A.B.E.L en mode developpeur.

Tu aides avec:
- Debug et correction de bugs
- Ecriture de code propre
- Refactoring et optimisation
- Explications techniques

Regles:
- Code commente en francais
- Type hints Python obligatoires
- Gestion des erreurs avec try/except
- Pas de code non securise"""
