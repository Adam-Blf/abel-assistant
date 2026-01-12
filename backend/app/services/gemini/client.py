"""
===============================================================================
CLIENT.PY - Gemini API Client Wrapper
===============================================================================
A.B.E.L. Project - Google Gemini AI Integration
Secure wrapper for Gemini API calls
===============================================================================
"""

import logging
from typing import Any, Dict, List

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmBlockThreshold, HarmCategory

from app.config.settings import get_settings
from app.core.exceptions import GeminiError

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiClient:
    """
    Wrapper for Google Gemini API.

    Provides secure, configured access to Gemini models
    with proper error handling and safety settings.
    """

    def __init__(self) -> None:
        """Initialize Gemini client with API key from settings."""
        api_key = settings.gemini_api_key.get_secret_value()
        if not api_key:
            raise GeminiError("Gemini API key not configured")

        genai.configure(api_key=api_key)

        # Safety settings - block harmful content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Default generation config
        self.default_generation_config = GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )

        # Initialize models
        self._chat_model = None
        self._vision_model = None

    @property
    def chat_model(self) -> genai.GenerativeModel:
        """Get or create chat model instance."""
        if self._chat_model is None:
            self._chat_model = genai.GenerativeModel(
                model_name=settings.gemini_model_chat,
                generation_config=self.default_generation_config,
                safety_settings=self.safety_settings,
            )
        return self._chat_model

    @property
    def vision_model(self) -> genai.GenerativeModel:
        """Get or create vision model instance."""
        if self._vision_model is None:
            self._vision_model = genai.GenerativeModel(
                model_name=settings.gemini_model_vision,
                generation_config=self.default_generation_config,
                safety_settings=self.safety_settings,
            )
        return self._vision_model

    async def generate_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] | None = None,
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate a text response from Gemini.

        Args:
            prompt: User's message
            history: Optional conversation history
            system_instruction: Optional system prompt

        Returns:
            Generated text response

        Raises:
            GeminiError: If generation fails
        """
        try:
            # Create model with system instruction if provided
            model = self.chat_model
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=settings.gemini_model_chat,
                    generation_config=self.default_generation_config,
                    safety_settings=self.safety_settings,
                    system_instruction=system_instruction,
                )

            # Start chat with history if provided
            chat = model.start_chat(history=self._format_history(history) if history else [])

            # Generate response
            response = chat.send_message(prompt)

            if not response.text:
                raise GeminiError("Empty response from Gemini")

            return response.text

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise GeminiError(f"Failed to generate response: {str(e)}")

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str = "Describe this image in detail.",
        mime_type: str = "image/jpeg",
    ) -> str:
        """
        Analyze an image using Gemini Vision.

        Args:
            image_data: Raw image bytes
            prompt: Analysis prompt
            mime_type: Image MIME type

        Returns:
            Image analysis text

        Raises:
            GeminiError: If analysis fails
        """
        try:
            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_data,
            }

            # Generate response
            response = self.vision_model.generate_content([prompt, image_part])

            if not response.text:
                raise GeminiError("Empty response from Gemini Vision")

            return response.text

        except Exception as e:
            logger.error(f"Gemini vision error: {e}")
            raise GeminiError(f"Failed to analyze image: {str(e)}")

    def _format_history(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Format conversation history for Gemini.

        Args:
            history: List of messages with 'role' and 'content'

        Returns:
            Formatted history for Gemini
        """
        formatted = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            formatted.append({
                "role": role,
                "parts": [msg.get("content", "")],
            })
        return formatted


# Singleton instance
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """Get singleton Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
