"""
A.B.E.L - Tools Service
QR codes, URL shortening, Password generation, Converters
"""

from typing import Optional, List, Dict, Any
import secrets
import string
import hashlib
import base64
import re
from datetime import datetime
import httpx
from app.core.logging import logger


class ToolsService:
    """
    Various utility tools:
    - QR Code generation
    - URL shortening
    - Password generation
    - Unit conversion
    - Text analysis
    - Hash generation
    """

    QR_API = "https://api.qrserver.com/v1"
    TINYURL_API = "https://tinyurl.com/api-create.php"
    CLEANURI_API = "https://cleanuri.com/api/v1/shorten"

    # ========================================
    # QR CODE GENERATION
    # ========================================
    async def generate_qr(
        self,
        data: str,
        size: int = 200,
        format: str = "png",  # png, gif, jpeg, svg
        error_correction: str = "M",  # L, M, Q, H
    ) -> Optional[bytes]:
        """Generate QR code image"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.QR_API}/create-qr-code/",
                    params={
                        "data": data,
                        "size": f"{size}x{size}",
                        "format": format,
                        "ecc": error_correction,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.error(f"QR generation error: {e}")
        return None

    def get_qr_url(
        self,
        data: str,
        size: int = 200,
        format: str = "png",
    ) -> str:
        """Get QR code URL (no download needed)"""
        return (
            f"{self.QR_API}/create-qr-code/"
            f"?data={data}&size={size}x{size}&format={format}"
        )

    # ========================================
    # URL SHORTENING
    # ========================================
    async def shorten_url(self, url: str) -> Optional[str]:
        """Shorten a URL using TinyURL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.TINYURL_API,
                    params={"url": url},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            logger.error(f"URL shortening error: {e}")
        return None

    async def shorten_url_cleanuri(self, url: str) -> Optional[str]:
        """Shorten a URL using CleanURI"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.CLEANURI_API,
                    data={"url": url},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("result_url")
        except Exception as e:
            logger.error(f"CleanURI error: {e}")
        return None

    # ========================================
    # PASSWORD GENERATION
    # ========================================
    def generate_password(
        self,
        length: int = 16,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_special: bool = True,
        exclude_ambiguous: bool = False,
    ) -> str:
        """Generate a secure random password"""
        chars = ""

        if include_lowercase:
            chars += string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_digits:
            chars += string.digits
        if include_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if exclude_ambiguous:
            chars = chars.replace("l", "").replace("1", "")
            chars = chars.replace("I", "").replace("O", "").replace("0", "")

        if not chars:
            chars = string.ascii_letters + string.digits

        return "".join(secrets.choice(chars) for _ in range(length))

    def generate_passphrase(
        self,
        word_count: int = 4,
        separator: str = "-",
    ) -> str:
        """Generate a passphrase from random words"""
        # Simple word list (in production, use a larger dictionary)
        words = [
            "apple", "banana", "cherry", "dragon", "eagle", "falcon",
            "guitar", "hammer", "island", "jungle", "knight", "lemon",
            "mountain", "neptune", "orange", "piano", "queen", "rocket",
            "sunset", "thunder", "umbrella", "victory", "wizard", "xenon",
            "yellow", "zebra", "anchor", "bridge", "castle", "diamond",
            "elephant", "forest", "glacier", "horizon", "igloo", "jupiter",
        ]
        selected = [secrets.choice(words) for _ in range(word_count)]
        return separator.join(selected)

    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """Analyze password strength"""
        score = 0
        feedback = []

        # Length check
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if len(password) < 8:
            feedback.append("Password should be at least 8 characters")

        # Character type checks
        if re.search(r"[a-z]", password):
            score += 1
        else:
            feedback.append("Add lowercase letters")

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Add uppercase letters")

        if re.search(r"\d", password):
            score += 1
        else:
            feedback.append("Add numbers")

        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        else:
            feedback.append("Add special characters")

        # Common patterns check
        common_patterns = ["password", "123456", "qwerty", "admin", "letmein"]
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 2
            feedback.append("Avoid common patterns")

        # Determine strength level
        if score <= 2:
            strength = "weak"
        elif score <= 4:
            strength = "fair"
        elif score <= 6:
            strength = "good"
        else:
            strength = "strong"

        return {
            "score": max(0, score),
            "max_score": 7,
            "strength": strength,
            "feedback": feedback,
        }

    # ========================================
    # HASH GENERATION
    # ========================================
    def hash_text(
        self,
        text: str,
        algorithm: str = "sha256",
    ) -> str:
        """Generate hash of text"""
        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }

        hash_func = algorithms.get(algorithm.lower(), hashlib.sha256)
        return hash_func(text.encode()).hexdigest()

    def base64_encode(self, text: str) -> str:
        """Encode text to base64"""
        return base64.b64encode(text.encode()).decode()

    def base64_decode(self, encoded: str) -> str:
        """Decode base64 to text"""
        try:
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            return ""

    # ========================================
    # UNIT CONVERSION
    # ========================================
    def convert_temperature(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert temperature between C, F, K"""
        # Convert to Celsius first
        if from_unit.upper() == "F":
            celsius = (value - 32) * 5 / 9
        elif from_unit.upper() == "K":
            celsius = value - 273.15
        else:
            celsius = value

        # Convert from Celsius to target
        if to_unit.upper() == "F":
            return celsius * 9 / 5 + 32
        elif to_unit.upper() == "K":
            return celsius + 273.15
        return celsius

    def convert_length(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert length between various units"""
        # Convert to meters first
        to_meters = {
            "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
            "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
        }
        from_meters = {k: 1 / v for k, v in to_meters.items()}

        meters = value * to_meters.get(from_unit.lower(), 1)
        return meters * from_meters.get(to_unit.lower(), 1)

    def convert_weight(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert weight between various units"""
        # Convert to grams first
        to_grams = {
            "mg": 0.001, "g": 1, "kg": 1000,
            "oz": 28.3495, "lb": 453.592, "st": 6350.29,
        }
        from_grams = {k: 1 / v for k, v in to_grams.items()}

        grams = value * to_grams.get(from_unit.lower(), 1)
        return grams * from_grams.get(to_unit.lower(), 1)

    # ========================================
    # TEXT ANALYSIS
    # ========================================
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text statistics"""
        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        paragraphs = text.split("\n\n")

        return {
            "characters": len(text),
            "characters_no_spaces": len(text.replace(" ", "")),
            "words": len(words),
            "sentences": len([s for s in sentences if s.strip()]),
            "paragraphs": len([p for p in paragraphs if p.strip()]),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "reading_time_minutes": len(words) / 200,  # Average reading speed
        }

    def count_word_frequency(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Count word frequency in text"""
        words = re.findall(r"\b\w+\b", text.lower())
        frequency = {}

        for word in words:
            if len(word) > 2:  # Skip short words
                frequency[word] = frequency.get(word, 0) + 1

        sorted_words = sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"word": word, "count": count}
            for word, count in sorted_words[:top_n]
        ]

    # ========================================
    # DATE & TIME
    # ========================================
    def get_timezone_time(self, timezone: str = "Europe/Paris") -> str:
        """Get current time in a timezone"""
        from datetime import timezone as tz
        import pytz

        try:
            tz_obj = pytz.timezone(timezone)
            return datetime.now(tz_obj).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def calculate_date_diff(
        self,
        date1: str,
        date2: str,
        format: str = "%Y-%m-%d",
    ) -> Dict[str, int]:
        """Calculate difference between two dates"""
        try:
            d1 = datetime.strptime(date1, format)
            d2 = datetime.strptime(date2, format)
            diff = abs((d2 - d1).days)

            return {
                "days": diff,
                "weeks": diff // 7,
                "months": diff // 30,
                "years": diff // 365,
            }
        except Exception:
            return {"error": "Invalid date format"}
