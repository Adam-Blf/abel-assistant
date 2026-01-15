"""
A.B.E.L - Voice API Endpoints (Speech-to-Text & Text-to-Speech)
"""

from typing import Optional
import io
import base64

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.senses.audio import AudioProcessor

router = APIRouter()


class TextToSpeechRequest(BaseModel):
    """TTS request schema."""

    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    output_format: str = Field(default="mp3", pattern="^(mp3|wav|ogg)$")


class TranscriptionResponse(BaseModel):
    """Transcription response schema."""

    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None


class TTSResponse(BaseModel):
    """TTS response schema (for base64 mode)."""

    audio_base64: str
    format: str
    duration_seconds: Optional[float] = None


@router.post("/listen", response_model=TranscriptionResponse)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, webm, ogg)"),
    language: Optional[str] = Form(default=None, description="Language code (e.g., 'fr', 'en')"),
):
    """
    Transcribe audio to text using OpenAI Whisper.

    Supported formats: wav, mp3, webm, ogg, m4a
    Max file size: 25MB
    """
    try:
        # Validate file type
        allowed_types = ["audio/wav", "audio/mpeg", "audio/webm", "audio/ogg", "audio/mp4"]
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {audio.content_type}",
            )

        # Read audio content
        audio_content = await audio.read()

        # Check file size (25MB limit for Whisper)
        if len(audio_content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")

        # Process with Whisper
        audio_processor = AudioProcessor()
        result = await audio_processor.transcribe(
            audio_data=audio_content,
            filename=audio.filename,
            language=language,
        )

        return TranscriptionResponse(
            text=result["text"],
            language=result.get("language"),
            confidence=result.get("confidence"),
            duration_seconds=result.get("duration"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/speak")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using ElevenLabs.

    Returns audio stream for direct playback.
    """
    try:
        audio_processor = AudioProcessor()

        # Generate audio
        audio_stream = await audio_processor.synthesize(
            text=request.text,
            voice_id=request.voice_id or settings.elevenlabs_voice_id,
            output_format=request.output_format,
        )

        # Return as streaming response
        content_type = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
        }.get(request.output_format, "audio/mpeg")

        return StreamingResponse(
            io.BytesIO(audio_stream),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=abel_speech.{request.output_format}"
            },
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/speak/base64", response_model=TTSResponse)
async def text_to_speech_base64(request: TextToSpeechRequest):
    """
    Convert text to speech and return as base64.

    Useful for frontend direct embedding.
    """
    try:
        audio_processor = AudioProcessor()

        # Generate audio
        audio_bytes = await audio_processor.synthesize(
            text=request.text,
            voice_id=request.voice_id or settings.elevenlabs_voice_id,
            output_format=request.output_format,
        )

        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return TTSResponse(
            audio_base64=audio_base64,
            format=request.output_format,
        )

    except Exception as e:
        logger.error(f"TTS base64 error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/voices")
async def list_voices():
    """List available TTS voices from ElevenLabs."""
    try:
        audio_processor = AudioProcessor()
        voices = await audio_processor.list_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    conversation_id: Optional[int] = Form(default=None),
    use_memory: bool = Form(default=True),
):
    """
    Full voice conversation: transcribe -> process -> respond with audio.

    This endpoint combines STT + Chat + TTS for a complete voice interaction.
    """
    try:
        audio_processor = AudioProcessor()

        # 1. Transcribe user audio
        audio_content = await audio.read()
        transcription = await audio_processor.transcribe(
            audio_data=audio_content,
            filename=audio.filename,
        )
        user_text = transcription["text"]

        # 2. Process through chat (import here to avoid circular)
        from app.brain.chat_service import ChatService
        from app.brain.memory_service import MemoryService
        from app.core.database import async_session_maker

        async with async_session_maker() as db:
            chat_service = ChatService(db)
            memory_service = MemoryService()

            memory_context = None
            if use_memory:
                memories = await memory_service.recall_memory(user_text, limit=3)
                if memories:
                    memory_context = "\n".join([m["content"] for m in memories])

            result = await chat_service.process_message(
                message=user_text,
                conversation_id=conversation_id,
                memory_context=memory_context,
            )

        # 3. Convert response to speech
        response_audio = await audio_processor.synthesize(
            text=result["response"],
            voice_id=settings.elevenlabs_voice_id,
        )

        # Return audio stream with metadata in headers
        return StreamingResponse(
            io.BytesIO(response_audio),
            media_type="audio/mpeg",
            headers={
                "X-User-Text": base64.b64encode(user_text.encode()).decode(),
                "X-Response-Text": base64.b64encode(result["response"].encode()).decode(),
                "X-Conversation-Id": str(result["conversation_id"]),
            },
        )

    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
