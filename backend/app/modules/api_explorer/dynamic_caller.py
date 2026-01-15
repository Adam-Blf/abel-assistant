"""
A.B.E.L - Dynamic API Caller
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger
from app.modules.api_explorer.api_discovery import ApiDiscovery


class DynamicApiCaller:
    """
    Dynamically call discovered APIs based on natural language requests.

    Features:
    - Parse user intent to find relevant API
    - Automatically construct API calls
    - Handle responses intelligently
    - Learn from successful calls
    """

    INTENT_PROMPT = """Tu es un assistant qui aide à trouver et utiliser des APIs publiques.

L'utilisateur veut: {user_request}

APIs disponibles dans la catégorie pertinente:
{available_apis}

Choisis l'API la plus appropriée et explique comment l'utiliser.
Réponds en JSON:
{{
    "selected_api": "nom de l'API",
    "api_url": "URL de base",
    "explanation": "explication courte",
    "example_endpoint": "endpoint suggéré si applicable",
    "confidence": 0.0-1.0
}}
"""

    def __init__(self):
        self.discovery = ApiDiscovery()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.call_history: List[Dict[str, Any]] = []

    async def find_api_for_request(
        self,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Find the best API for a user's natural language request.

        Args:
            user_request: What the user wants to do

        Returns:
            Selected API with usage instructions
        """
        try:
            # First, try keyword search
            keywords = user_request.lower().split()
            all_matches = []

            for keyword in keywords:
                if len(keyword) > 3:  # Skip short words
                    matches = await self.discovery.search_by_keyword(keyword, limit=5)
                    all_matches.extend(matches)

            # Remove duplicates
            seen = set()
            unique_matches = []
            for api in all_matches:
                api_name = api.get("API", "")
                if api_name not in seen:
                    seen.add(api_name)
                    unique_matches.append(api)

            if not unique_matches:
                # Fallback to random selection
                return {
                    "found": False,
                    "message": "Aucune API trouvée pour cette requête",
                    "suggestion": "Essaie de reformuler ou précise la catégorie",
                }

            # Use AI to select best match
            apis_text = "\n".join([
                f"- {api['API']}: {api['Description']} (URL: {api['Link']})"
                for api in unique_matches[:10]
            ])

            prompt = self.INTENT_PROMPT.format(
                user_request=user_request,
                available_apis=apis_text,
            )

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            selection = json.loads(result_text)

            return {
                "found": True,
                "selected_api": selection.get("selected_api"),
                "api_url": selection.get("api_url"),
                "explanation": selection.get("explanation"),
                "example_endpoint": selection.get("example_endpoint"),
                "confidence": selection.get("confidence", 0.5),
                "alternatives": unique_matches[:5],
            }

        except Exception as e:
            logger.error(f"Error finding API: {e}")
            return {
                "found": False,
                "error": str(e),
            }

    async def call_api(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Make a dynamic API call.

        Args:
            url: API endpoint URL
            method: HTTP method
            params: Query parameters
            headers: Request headers
            body: Request body for POST/PUT
            timeout: Request timeout

        Returns:
            API response with metadata
        """
        try:
            start_time = datetime.utcnow()

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    headers=headers,
                    json=body if body else None,
                    timeout=timeout,
                    follow_redirects=True,
                )

                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Try to parse JSON response
                try:
                    data = response.json()
                except Exception:
                    data = response.text

                result = {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "data": data,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Log call
                self.call_history.append({
                    "url": url,
                    "method": method,
                    "success": result["success"],
                    "timestamp": result["timestamp"],
                })

                return result

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"API call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def smart_call(
        self,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Intelligently find and call an API based on user request.

        Args:
            user_request: Natural language request

        Returns:
            API selection and call results
        """
        # Find appropriate API
        selection = await self.find_api_for_request(user_request)

        if not selection.get("found"):
            return selection

        # Test if the API is available
        api_url = selection.get("api_url", "")
        if api_url:
            test_result = await self.discovery.test_api_availability(api_url)

            if not test_result.get("available"):
                return {
                    **selection,
                    "call_result": None,
                    "api_status": "unavailable",
                    "test_result": test_result,
                }

            # Try to call the example endpoint if provided
            example = selection.get("example_endpoint")
            if example:
                call_url = f"{api_url.rstrip('/')}/{example.lstrip('/')}"
                call_result = await self.call_api(call_url)
            else:
                call_result = await self.call_api(api_url)

            return {
                **selection,
                "call_result": call_result,
                "api_status": "available",
            }

        return selection

    async def explain_response(
        self,
        api_response: Dict[str, Any],
        user_context: str,
    ) -> str:
        """
        Explain an API response in natural language.

        Args:
            api_response: The API response data
            user_context: What the user was trying to do

        Returns:
            Human-readable explanation
        """
        try:
            # Truncate response if too large
            response_str = json.dumps(api_response.get("data", {}), indent=2)
            if len(response_str) > 2000:
                response_str = response_str[:2000] + "..."

            prompt = f"""L'utilisateur voulait: {user_context}

Voici la réponse de l'API:
{response_str}

Explique cette réponse de manière claire et utile en français. Sois concis."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error explaining response: {e}")
            return "Impossible d'analyser la réponse de l'API."

    def get_call_stats(self) -> Dict[str, Any]:
        """Get statistics about API calls made."""
        total = len(self.call_history)
        successful = sum(1 for c in self.call_history if c.get("success"))

        return {
            "total_calls": total,
            "successful_calls": successful,
            "success_rate": successful / total if total > 0 else 0,
            "recent_calls": self.call_history[-10:],
        }
