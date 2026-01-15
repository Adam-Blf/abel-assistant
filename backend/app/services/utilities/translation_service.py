"""
A.B.E.L - Translation Service
Integrates LibreTranslate, MyMemory, Lingva
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.logging import logger


class TranslationService:
    """
    Translation service integrating:
    - LibreTranslate (self-hosted or public)
    - MyMemory Translation API (FREE)
    - Lingva Translate (FREE)
    """

    LIBRETRANSLATE_API = "https://libretranslate.com"
    MYMEMORY_API = "https://api.mymemory.translated.net"
    LINGVA_API = "https://lingva.ml/api/v1"

    # Language codes
    LANGUAGES = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "el": "Greek",
        "he": "Hebrew",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "cs": "Czech",
        "ro": "Romanian",
        "hu": "Hungarian",
        "uk": "Ukrainian",
    }

    # ========================================
    # MYMEMORY API (FREE - 1000 words/day)
    # ========================================
    async def mymemory_translate(
        self,
        text: str,
        source: str,
        target: str,
        email: Optional[str] = None,  # For higher limits
    ) -> Optional[Dict[str, Any]]:
        """Translate using MyMemory API"""
        try:
            params = {
                "q": text,
                "langpair": f"{source}|{target}",
            }
            if email:
                params["de"] = email

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.MYMEMORY_API}/get",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "translated_text": data["responseData"]["translatedText"],
                        "match": data["responseData"]["match"],
                        "source": source,
                        "target": target,
                    }
        except Exception as e:
            logger.error(f"MyMemory translation error: {e}")
        return None

    # ========================================
    # LINGVA TRANSLATE (FREE - No auth)
    # ========================================
    async def lingva_translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> Optional[str]:
        """Translate using Lingva Translate"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.LINGVA_API}/{source}/{target}/{text}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("translation")
        except Exception as e:
            logger.error(f"Lingva translation error: {e}")
        return None

    async def lingva_languages(self) -> List[Dict[str, str]]:
        """Get supported languages from Lingva"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.LINGVA_API}/languages",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json().get("languages", [])
        except Exception as e:
            logger.error(f"Lingva languages error: {e}")
        return []

    # ========================================
    # LIBRETRANSLATE (Self-hosted or public)
    # ========================================
    async def libretranslate(
        self,
        text: str,
        source: str,
        target: str,
        api_key: Optional[str] = None,
    ) -> Optional[str]:
        """Translate using LibreTranslate"""
        try:
            data = {
                "q": text,
                "source": source,
                "target": target,
            }
            if api_key:
                data["api_key"] = api_key

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.LIBRETRANSLATE_API}/translate",
                    json=data,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json().get("translatedText")
        except Exception as e:
            logger.error(f"LibreTranslate error: {e}")
        return None

    async def libretranslate_detect(
        self,
        text: str,
        api_key: Optional[str] = None,
    ) -> Optional[str]:
        """Detect language using LibreTranslate"""
        try:
            data = {"q": text}
            if api_key:
                data["api_key"] = api_key

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.LIBRETRANSLATE_API}/detect",
                    json=data,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        return results[0].get("language")
        except Exception as e:
            logger.error(f"LibreTranslate detect error: {e}")
        return None

    # ========================================
    # UNIFIED TRANSLATION
    # ========================================
    async def translate(
        self,
        text: str,
        target: str,
        source: str = "auto",
    ) -> Dict[str, Any]:
        """Translate text using the best available service"""
        # Try MyMemory first (most reliable free option)
        if source == "auto":
            source = "en"  # Default to English if auto-detect not available

        result = await self.mymemory_translate(text, source, target)

        if result:
            return {
                "success": True,
                "original": text,
                "translated": result["translated_text"],
                "source_language": source,
                "target_language": target,
                "service": "mymemory",
            }

        # Fallback to Lingva
        translated = await self.lingva_translate(text, source, target)
        if translated:
            return {
                "success": True,
                "original": text,
                "translated": translated,
                "source_language": source,
                "target_language": target,
                "service": "lingva",
            }

        return {
            "success": False,
            "error": "Translation failed",
        }

    async def translate_batch(
        self,
        texts: List[str],
        target: str,
        source: str = "en",
    ) -> List[Dict[str, Any]]:
        """Translate multiple texts"""
        results = []
        for text in texts:
            result = await self.translate(text, target, source)
            results.append(result)
        return results

    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        return self.LANGUAGES.get(code.lower(), code)

    def get_all_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return self.LANGUAGES

    # Common translation pairs for quick access
    COMMON_PAIRS = [
        ("en", "fr"),
        ("en", "es"),
        ("en", "de"),
        ("en", "it"),
        ("en", "pt"),
        ("en", "zh"),
        ("en", "ja"),
        ("fr", "en"),
        ("es", "en"),
        ("de", "en"),
    ]
