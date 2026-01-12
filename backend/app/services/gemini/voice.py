"""
===============================================================================
VOICE.PY - Voice Processing Service
===============================================================================
A.B.E.L. Project - Speech-to-Text and Text-to-Speech with Gemini
===============================================================================
"""

import base64
import logging
from typing import Optional

import google.generativeai as genai

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key.get_secret_value())


class VoiceService:
    """
    Voice processing service using Gemini multimodal capabilities.

    Handles:
    - Speech-to-Text (audio transcription)
    - Audio understanding and response generation
    """

    def __init__(self):
        """Initialize voice service with Gemini model."""
        self.model = genai.GenerativeModel(settings.gemini_model_chat)
        self.audio_model = genai.GenerativeModel("gemini-1.5-flash")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        mime_type: str = "audio/wav",
    ) -> str:
        """
        Transcribe audio to text using Gemini.

        Args:
            audio_data: Raw audio bytes
            mime_type: Audio MIME type (audio/wav, audio/mp3, etc.)

        Returns:
            Transcribed text
        """
        try:
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            # Create audio part for Gemini
            audio_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_base64,
                }
            }

            # Transcription prompt
            prompt = """Transcris cet audio en français.
            Retourne UNIQUEMENT le texte transcrit, sans aucune explication ni formatage.
            Si l'audio est inaudible ou vide, retourne "AUDIO_INAUDIBLE"."""

            # Generate transcription
            response = self.audio_model.generate_content([prompt, audio_part])

            transcription = response.text.strip()
            logger.info(f"[Voice] Transcription: {transcription[:50]}...")

            return transcription

        except Exception as e:
            logger.error(f"[Voice] Transcription error: {e}")
            raise

    async def process_voice_command(
        self,
        audio_data: bytes,
        mime_type: str = "audio/wav",
        user_context: Optional[str] = None,
    ) -> dict:
        """
        Process voice command: transcribe and generate response.

        Args:
            audio_data: Raw audio bytes
            mime_type: Audio MIME type
            user_context: Optional user context for personalization

        Returns:
            Dict with transcription and AI response
        """
        try:
            # Encode audio
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            audio_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_base64,
                }
            }

            # Build prompt with context
            system_prompt = """Tu es A.B.E.L., un assistant IA personnel comme Jarvis.

L'utilisateur t'envoie un message audio. Tu dois:
1. Comprendre ce qu'il dit
2. Répondre de manière utile et concise

Format de réponse (JSON strict):
{
    "transcription": "ce que l'utilisateur a dit",
    "response": "ta réponse à l'utilisateur",
    "intent": "question|command|conversation|unclear"
}"""

            if user_context:
                system_prompt += f"\n\nContexte utilisateur:\n{user_context}"

            # Generate response
            response = self.audio_model.generate_content(
                [system_prompt, audio_part],
                generation_config={
                    "response_mime_type": "application/json",
                },
            )

            # Parse JSON response
            import json
            result = json.loads(response.text)

            logger.info(f"[Voice] Processed: {result.get('intent', 'unknown')}")

            return result

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "transcription": "Transcription non disponible",
                "response": response.text if response else "Erreur de traitement",
                "intent": "unclear",
            }
        except Exception as e:
            logger.error(f"[Voice] Processing error: {e}")
            raise

    async def generate_speech_text(
        self,
        text: str,
        style: str = "friendly",
    ) -> str:
        """
        Generate text optimized for speech synthesis.

        Args:
            text: Input text to optimize
            style: Speech style (friendly, formal, excited)

        Returns:
            Text optimized for TTS
        """
        try:
            prompt = f"""Reformule ce texte pour qu'il sonne naturel quand il est lu à voix haute.
            Style: {style}

            Texte original: {text}

            Règles:
            - Évite les abréviations
            - Utilise des phrases courtes
            - Ajoute des pauses naturelles avec des virgules
            - Retourne UNIQUEMENT le texte reformulé"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"[Voice] Speech text generation error: {e}")
            return text  # Return original on error


# Singleton instance
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create voice service instance."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
