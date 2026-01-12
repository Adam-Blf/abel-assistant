"""
=============================================================================
WEB SEARCH TOOL - Web Search Service
=============================================================================
A.B.E.L. Project - Web search using DuckDuckGo (free, no API key required)
=============================================================================
"""

import httpx
import re
import html
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, urljoin
import logging

from app.services.tools.registry import (
    ToolDefinition,
    ToolCategory,
    get_tool_registry
)

logger = logging.getLogger(__name__)

# DuckDuckGo endpoints
DDG_HTML_SEARCH = "https://html.duckduckgo.com/html/"
DDG_INSTANT_ANSWER = "https://api.duckduckgo.com/"


async def web_search(
    query: str,
    limit: int = 5,
    region: str = "fr-fr"
) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo

    Args:
        query: Search query
        limit: Number of results to return (max 10)
        region: Region for results (fr-fr, us-en, etc.)

    Returns:
        Search results dict
    """
    logger.info(f"[WebSearchTool] Searching: {query}")

    if not query or len(query.strip()) < 2:
        return {"error": "La requête de recherche est trop courte."}

    limit = min(max(1, limit), 10)

    try:
        # Try instant answer API first
        instant_result = await _get_instant_answer(query)

        # Get web results
        web_results = await _search_ddg_html(query, limit, region)

        result = {
            "query": query,
            "region": region,
            "count": len(web_results),
            "results": web_results
        }

        # Add instant answer if available
        if instant_result:
            result["instant_answer"] = instant_result

        # Generate summary
        if instant_result:
            result["summary"] = f"Pour '{query}': {instant_result.get('abstract', 'Résultat trouvé.')[:200]}"
        elif web_results:
            titles = [r["title"] for r in web_results[:3]]
            result["summary"] = f"Résultats pour '{query}': " + " | ".join(titles)
        else:
            result["summary"] = f"Aucun résultat trouvé pour '{query}'."

        logger.info(f"[WebSearchTool] Found {len(web_results)} results")
        return result

    except Exception as e:
        logger.error(f"[WebSearchTool] Search error: {e}")
        return {"error": f"Erreur lors de la recherche: {str(e)}"}


async def _get_instant_answer(query: str) -> Optional[Dict[str, Any]]:
    """Get instant answer from DuckDuckGo API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                DDG_INSTANT_ANSWER,
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1
                }
            )
            response.raise_for_status()
            data = response.json()

        # Check for abstract (Wikipedia-style answer)
        abstract = data.get("Abstract")
        if abstract:
            return {
                "type": data.get("Type", ""),
                "abstract": abstract,
                "source": data.get("AbstractSource", ""),
                "url": data.get("AbstractURL", ""),
                "image": data.get("Image", "")
            }

        # Check for answer (calculation, conversion, etc.)
        answer = data.get("Answer")
        if answer:
            return {
                "type": "answer",
                "abstract": answer,
                "source": "DuckDuckGo",
                "url": "",
                "image": ""
            }

        return None

    except Exception as e:
        logger.warning(f"[WebSearchTool] Instant answer error: {e}")
        return None


async def _search_ddg_html(query: str, limit: int, region: str) -> List[Dict[str, Any]]:
    """Search using DuckDuckGo HTML endpoint"""
    results = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                DDG_HTML_SEARCH,
                data={
                    "q": query,
                    "kl": region,
                    "df": ""  # Any time
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()

        # Parse HTML response
        html_content = response.text
        results = _parse_ddg_html(html_content, limit)

    except Exception as e:
        logger.error(f"[WebSearchTool] HTML search error: {e}")

    return results


def _parse_ddg_html(html_content: str, limit: int) -> List[Dict[str, Any]]:
    """Parse DuckDuckGo HTML search results"""
    results = []

    # Find result blocks
    result_pattern = r'<div class="result[^"]*">.*?<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>'

    # Alternative pattern for different HTML structure
    alt_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]*)'

    matches = re.findall(result_pattern, html_content, re.DOTALL)

    if not matches:
        matches = re.findall(alt_pattern, html_content, re.DOTALL)

    # Fallback: simpler extraction
    if not matches:
        # Extract links with titles
        link_pattern = r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
        all_links = re.findall(link_pattern, html_content)

        # Filter out DuckDuckGo internal links
        for url, title in all_links:
            if "duckduckgo.com" not in url and len(title.strip()) > 10:
                results.append({
                    "title": _clean_text(title),
                    "url": url,
                    "description": ""
                })
                if len(results) >= limit:
                    break

        return results

    for match in matches[:limit]:
        url, title, snippet = match
        results.append({
            "title": _clean_text(title),
            "url": _clean_url(url),
            "description": _clean_text(snippet)
        })

    return results


def _clean_text(text: str) -> str:
    """Clean text from HTML entities and extra whitespace"""
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _clean_url(url: str) -> str:
    """Clean and decode URL"""
    # DuckDuckGo wraps URLs, extract actual URL if needed
    if "uddg=" in url:
        import urllib.parse
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if "uddg" in parsed:
            return urllib.parse.unquote(parsed["uddg"][0])
    return url


async def quick_answer(query: str) -> Dict[str, Any]:
    """
    Get a quick answer for a factual question

    Args:
        query: Question or query

    Returns:
        Quick answer if available
    """
    logger.info(f"[WebSearchTool] Quick answer for: {query}")

    instant = await _get_instant_answer(query)

    if instant and instant.get("abstract"):
        return {
            "query": query,
            "answer": instant["abstract"],
            "source": instant.get("source", ""),
            "url": instant.get("url", ""),
            "found": True
        }

    return {
        "query": query,
        "answer": None,
        "found": False,
        "suggestion": "Aucune réponse directe trouvée. Essayez une recherche web complète."
    }


def register_search_tool():
    """Register the search tool with the registry"""
    registry = get_tool_registry()

    # Web search tool
    search_tool = ToolDefinition(
        name="web_search",
        description="Recherche sur le web en utilisant DuckDuckGo. Retourne des résultats de recherche avec titres, URLs et descriptions.",
        category=ToolCategory.SEARCH,
        parameters={
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La requête de recherche"
                },
                "limit": {
                    "type": "integer",
                    "description": "Nombre de résultats (1-10, défaut: 5)"
                },
                "region": {
                    "type": "string",
                    "description": "Région pour les résultats (fr-fr, us-en, etc.)"
                }
            },
            "required": ["query"]
        },
        handler=web_search,
        rate_limit=20
    )
    registry.register(search_tool)

    # Quick answer tool
    answer_tool = ToolDefinition(
        name="quick_answer",
        description="Obtient une réponse rapide pour une question factuelle simple (définitions, conversions, calculs, etc.).",
        category=ToolCategory.SEARCH,
        parameters={
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La question ou requête"
                }
            },
            "required": ["query"]
        },
        handler=quick_answer,
        rate_limit=30
    )
    registry.register(answer_tool)

    logger.info("[WebSearchTool] Search tools registered")
