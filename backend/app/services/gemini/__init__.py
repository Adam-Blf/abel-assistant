"""
===============================================================================
GEMINI SERVICES - Init
===============================================================================
A.B.E.L. Project - Google Gemini AI Integration
===============================================================================
"""

from app.services.gemini.client import GeminiClient, get_gemini_client

# Import vision and voice services if they exist
try:
    from app.services.gemini.vision import VisionService, get_vision_service

    __all__ = [
        "GeminiClient",
        "get_gemini_client",
        "VisionService",
        "get_vision_service",
    ]
except ImportError:
    __all__ = [
        "GeminiClient",
        "get_gemini_client",
    ]

try:
    from app.services.gemini.voice import VoiceService, get_voice_service

    __all__.extend([
        "VoiceService",
        "get_voice_service",
    ])
except ImportError:
    pass
