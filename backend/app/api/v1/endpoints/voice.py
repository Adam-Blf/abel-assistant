"""
===============================================================================
VOICE.PY - Voice API Endpoints
===============================================================================
A.B.E.L. Project - Speech-to-Text and Voice Commands
===============================================================================
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security.auth import get_current_user, get_optional_user
from app.services.gemini.voice import get_voice_service
from app.services.memory import get_rag_pipeline

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/voice", tags=["Voice"])

# Allowed audio formats
ALLOWED_AUDIO_TYPES = [
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/webm",
    "audio/ogg",
    "audio/m4a",
    "audio/x-m4a",
]

MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/transcribe")
@limiter.limit("10/minute")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    current_user: dict = Depends(get_current_user),
):
    """
    Transcribe audio to text.

    Supports: WAV, MP3, WebM, OGG, M4A
    Max size: 10MB
    """
    # Validate file type
    content_type = audio.content_type or "audio/wav"
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Format audio non supporté: {content_type}",
        )

    # Read and validate size
    audio_data = await audio.read()
    if len(audio_data) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Fichier audio trop volumineux (max 10MB)",
        )

    try:
        voice_service = get_voice_service()
        transcription = await voice_service.transcribe_audio(
            audio_data=audio_data,
            mime_type=content_type,
        )

        return {
            "transcription": transcription,
            "audio_size": len(audio_data),
            "format": content_type,
        }

    except Exception as e:
        logger.error(f"[Voice API] Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la transcription",
        )


@router.post("/command")
@limiter.limit("10/minute")
async def process_voice_command(
    audio: UploadFile = File(..., description="Audio command"),
    use_memory: bool = Form(default=True, description="Use personal memory"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Process voice command and get AI response.

    1. Transcribes the audio
    2. Processes with RAG context (if authenticated)
    3. Returns transcription + AI response
    """
    # Validate file
    content_type = audio.content_type or "audio/wav"
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Format audio non supporté: {content_type}",
        )

    audio_data = await audio.read()
    if len(audio_data) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Fichier audio trop volumineux (max 10MB)",
        )

    try:
        voice_service = get_voice_service()

        # Get user context if authenticated and memory enabled
        user_context = None
        if current_user and use_memory:
            try:
                rag = get_rag_pipeline()
                # First transcribe to get query
                transcription = await voice_service.transcribe_audio(
                    audio_data=audio_data,
                    mime_type=content_type,
                )

                if transcription and transcription != "AUDIO_INAUDIBLE":
                    context = await rag.retrieve_context(
                        user_id=current_user["id"],
                        query=transcription,
                        limit=3,
                    )
                    if context.memories:
                        user_context = "\n".join(
                            [f"- {m.content}" for m in context.memories]
                        )
            except Exception as ctx_err:
                logger.warning(f"[Voice API] Context retrieval failed: {ctx_err}")

        # Process voice command with context
        result = await voice_service.process_voice_command(
            audio_data=audio_data,
            mime_type=content_type,
            user_context=user_context,
        )

        # Learn from interaction if authenticated
        if current_user and result.get("transcription"):
            try:
                rag = get_rag_pipeline()
                await rag.extract_and_store_learnings(
                    user_id=current_user["id"],
                    user_message=result["transcription"],
                    assistant_response=result.get("response", ""),
                )
            except Exception:
                pass  # Non-blocking

        return {
            "transcription": result.get("transcription", ""),
            "response": result.get("response", ""),
            "intent": result.get("intent", "unclear"),
            "context_used": user_context is not None,
        }

    except Exception as e:
        logger.error(f"[Voice API] Command processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du traitement de la commande vocale",
        )


@router.post("/speak")
@limiter.limit("20/minute")
async def prepare_speech(
    text: str = Form(..., min_length=1, max_length=1000),
    style: str = Form(default="friendly", pattern="^(friendly|formal|excited)$"),
    current_user: dict = Depends(get_current_user),
):
    """
    Prepare text for speech synthesis.

    Optimizes text for natural TTS output.
    """
    try:
        voice_service = get_voice_service()
        optimized = await voice_service.generate_speech_text(
            text=text,
            style=style,
        )

        return {
            "original": text,
            "optimized": optimized,
            "style": style,
        }

    except Exception as e:
        logger.error(f"[Voice API] Speech preparation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la préparation du texte",
        )
