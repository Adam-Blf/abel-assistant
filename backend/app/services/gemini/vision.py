"""
===============================================================================
VISION.PY - Vision Processing Service
===============================================================================
A.B.E.L. Project - Image Analysis with Gemini Vision
===============================================================================
"""

import base64
import logging
from typing import List, Optional

import google.generativeai as genai

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key.get_secret_value())


class VisionService:
    """
    Vision processing service using Gemini Pro Vision.

    Handles:
    - Image analysis and description
    - Object detection and identification
    - Text extraction (OCR)
    - Scene understanding
    """

    def __init__(self):
        """Initialize vision service with Gemini Pro Vision."""
        self.model = genai.GenerativeModel(settings.gemini_model_vision)

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str = "image/jpeg",
        question: Optional[str] = None,
    ) -> dict:
        """
        Analyze an image and return detailed description.

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type (image/jpeg, image/png, etc.)
            question: Optional specific question about the image

        Returns:
            Dict with analysis results
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            image_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64,
                }
            }

            # Build prompt
            if question:
                prompt = f"""Tu es A.B.E.L., un assistant IA avec vision.

L'utilisateur te montre une image et demande: "{question}"

Analyse l'image et réponds à sa question de manière utile et détaillée en français."""
            else:
                prompt = """Tu es A.B.E.L., un assistant IA avec vision.

Analyse cette image et décris ce que tu vois. Inclus:
- Description générale de la scène
- Objets principaux identifiés
- Texte visible (si présent)
- Détails importants ou intéressants

Réponds en français de manière naturelle et utile."""

            # Generate analysis
            response = self.model.generate_content([prompt, image_part])

            result = {
                "description": response.text.strip(),
                "has_text": self._detect_text_presence(response.text),
                "confidence": "high",  # Gemini doesn't provide confidence scores
            }

            logger.info("[Vision] Image analyzed successfully")
            return result

        except Exception as e:
            logger.error(f"[Vision] Analysis error: {e}")
            raise

    async def extract_text(
        self,
        image_data: bytes,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """
        Extract text from image (OCR).

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type

        Returns:
            Dict with extracted text
        """
        try:
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            image_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64,
                }
            }

            prompt = """Extrais TOUT le texte visible dans cette image.

Format de réponse:
- Liste chaque bloc de texte sur une ligne séparée
- Préserve la mise en forme si possible
- Si aucun texte n'est visible, réponds "AUCUN_TEXTE"

Retourne uniquement le texte extrait, sans commentaires."""

            response = self.model.generate_content([prompt, image_part])
            extracted = response.text.strip()

            return {
                "text": extracted if extracted != "AUCUN_TEXTE" else "",
                "has_text": extracted != "AUCUN_TEXTE",
            }

        except Exception as e:
            logger.error(f"[Vision] Text extraction error: {e}")
            raise

    async def identify_objects(
        self,
        image_data: bytes,
        mime_type: str = "image/jpeg",
    ) -> List[dict]:
        """
        Identify objects in the image.

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type

        Returns:
            List of identified objects
        """
        try:
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            image_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64,
                }
            }

            prompt = """Identifie tous les objets principaux dans cette image.

Pour chaque objet, donne:
- name: nom de l'objet
- category: catégorie (personne, animal, véhicule, meuble, électronique, nourriture, nature, autre)
- description: brève description

Réponds en JSON strict:
[{"name": "...", "category": "...", "description": "..."}]"""

            response = self.model.generate_content(
                [prompt, image_part],
                generation_config={
                    "response_mime_type": "application/json",
                },
            )

            import json
            objects = json.loads(response.text)

            logger.info(f"[Vision] Identified {len(objects)} objects")
            return objects

        except Exception as e:
            logger.error(f"[Vision] Object identification error: {e}")
            return []

    async def compare_images(
        self,
        image1_data: bytes,
        image2_data: bytes,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """
        Compare two images and describe differences.

        Args:
            image1_data: First image bytes
            image2_data: Second image bytes
            mime_type: Image MIME type

        Returns:
            Dict with comparison results
        """
        try:
            image1_base64 = base64.b64encode(image1_data).decode("utf-8")
            image2_base64 = base64.b64encode(image2_data).decode("utf-8")

            image1_part = {
                "inline_data": {"mime_type": mime_type, "data": image1_base64}
            }
            image2_part = {
                "inline_data": {"mime_type": mime_type, "data": image2_base64}
            }

            prompt = """Compare ces deux images et décris:
1. Ce qu'elles ont en commun
2. Les différences principales
3. Tout changement notable entre les deux

Réponds en français de manière claire et structurée."""

            response = self.model.generate_content(
                [prompt, image1_part, image2_part]
            )

            return {
                "comparison": response.text.strip(),
                "images_analyzed": 2,
            }

        except Exception as e:
            logger.error(f"[Vision] Comparison error: {e}")
            raise

    def _detect_text_presence(self, analysis: str) -> bool:
        """Check if analysis mentions text in the image."""
        text_indicators = [
            "texte", "écrit", "lettres", "mots", "phrase",
            "titre", "légende", "panneau", "affiche",
        ]
        analysis_lower = analysis.lower()
        return any(indicator in analysis_lower for indicator in text_indicators)


# Singleton instance
_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    """Get or create vision service instance."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
