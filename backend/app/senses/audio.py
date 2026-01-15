"""
A.B.E.L - Audio Processing (Speech-to-Text & Text-to-Speech)
"""

import io
from typing import Optional, List, Dict, Any

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger


class AudioProcessor:
    """
    Audio processing service for A.B.E.L.

    Features:
    - Speech-to-Text via OpenAI Whisper
    - Text-to-Speech via ElevenLabs
    """

    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe(
        self,
        audio_data: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using OpenAI Whisper.

        Args:
            audio_data: Raw audio bytes
            filename: Original filename (for format detection)
            language: Optional language code (e.g., 'fr', 'en')

        Returns:
            Dict with transcription text and metadata
        """
        try:
            # Create a file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename

            # Transcribe with Whisper
            kwargs = {"model": "whisper-1", "file": audio_file}
            if language:
                kwargs["language"] = language

            response = await self.openai_client.audio.transcriptions.create(**kwargs)

            logger.info(f"Transcribed audio: {len(response.text)} characters")

            return {
                "text": response.text,
                "language": language,
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_format: str = "mp3",
        model_id: str = "eleven_multilingual_v2",
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs.

        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID
            output_format: Output format (mp3, wav, ogg)
            model_id: ElevenLabs model ID

        Returns:
            Audio bytes
        """
        try:
            voice_id = voice_id or settings.elevenlabs_voice_id

            if not settings.elevenlabs_api_key:
                raise ValueError("ElevenLabs API key not configured")

            if not voice_id:
                raise ValueError("No voice ID specified")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
                    headers={
                        "Accept": f"audio/{output_format}",
                        "xi-api-key": settings.elevenlabs_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.5,
                            "use_speaker_boost": True,
                        },
                    },
                    timeout=60.0,
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"ElevenLabs error: {error_detail}")
                    raise Exception(f"ElevenLabs API error: {response.status_code}")

                logger.info(f"Synthesized {len(text)} characters to audio")

                return response.content

        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise

    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available ElevenLabs voices."""
        try:
            if not settings.elevenlabs_api_key:
                return []

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ELEVENLABS_API_URL}/voices",
                    headers={"xi-api-key": settings.elevenlabs_api_key},
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to list voices: {response.text}")
                    return []

                data = response.json()
                voices = []

                for voice in data.get("voices", []):
                    voices.append({
                        "voice_id": voice["voice_id"],
                        "name": voice["name"],
                        "category": voice.get("category", "unknown"),
                        "description": voice.get("description"),
                        "labels": voice.get("labels", {}),
                        "preview_url": voice.get("preview_url"),
                    })

                return voices

        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []

    async def get_voice_info(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific voice."""
        try:
            if not settings.elevenlabs_api_key:
                return None

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ELEVENLABS_API_URL}/voices/{voice_id}",
                    headers={"xi-api-key": settings.elevenlabs_api_key},
                    timeout=30.0,
                )

                if response.status_code != 200:
                    return None

                return response.json()

        except Exception as e:
            logger.error(f"Error getting voice info: {e}")
            return None
