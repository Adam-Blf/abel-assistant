"""
=============================================================================
NEWS TOOL - News Information Service
=============================================================================
A.B.E.L. Project - News data using free RSS feeds and APIs
=============================================================================
"""

import httpx
import re
import html
from typing import Dict, Any, List, Optional
from datetime import datetime
from xml.etree import ElementTree
import logging

from app.services.tools.registry import (
    ToolDefinition,
    ToolCategory,
    get_tool_registry
)

logger = logging.getLogger(__name__)

# News sources with RSS feeds (free, no API key required)
NEWS_SOURCES = {
    "france": {
        "le_monde": "https://www.lemonde.fr/rss/une.xml",
        "le_figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
        "france_info": "https://www.francetvinfo.fr/titres.rss",
        "liberation": "https://www.liberation.fr/arc/outboundfeeds/rss/?outputType=xml",
    },
    "tech": {
        "hackernews": "https://news.ycombinator.com/rss",
        "techcrunch": "https://techcrunch.com/feed/",
        "the_verge": "https://www.theverge.com/rss/index.xml",
    },
    "international": {
        "bbc": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "reuters": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    },
    "science": {
        "science_daily": "https://www.sciencedaily.com/rss/all.xml",
        "phys_org": "https://phys.org/rss-feed/",
    }
}

# Category labels in French
CATEGORY_LABELS = {
    "france": "France",
    "tech": "Technologie",
    "international": "International",
    "science": "Science"
}


async def get_news(
    category: str = "france",
    source: Optional[str] = None,
    limit: int = 5,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get latest news from RSS feeds

    Args:
        category: News category (france, tech, international, science)
        source: Specific source name (optional)
        limit: Number of articles to return (max 10)
        search: Optional search term to filter articles

    Returns:
        News articles dict
    """
    logger.info(f"[NewsTool] Getting news - category: {category}, source: {source}")

    category = category.lower().strip()
    limit = min(max(1, limit), 10)

    # Get sources for category
    if category not in NEWS_SOURCES:
        return {
            "error": f"Catégorie '{category}' non trouvée. Catégories disponibles: {', '.join(NEWS_SOURCES.keys())}"
        }

    sources = NEWS_SOURCES[category]

    # Filter by specific source if provided
    if source:
        source_lower = source.lower().replace(" ", "_")
        if source_lower in sources:
            sources = {source_lower: sources[source_lower]}
        else:
            return {
                "error": f"Source '{source}' non trouvée dans {category}. Sources disponibles: {', '.join(sources.keys())}"
            }

    # Fetch articles from all sources
    all_articles: List[Dict[str, Any]] = []

    for source_name, rss_url in sources.items():
        try:
            articles = await _fetch_rss(rss_url, source_name, limit)
            all_articles.extend(articles)
        except Exception as e:
            logger.warning(f"[NewsTool] Failed to fetch {source_name}: {e}")

    # Filter by search term
    if search:
        search_lower = search.lower()
        all_articles = [
            a for a in all_articles
            if search_lower in a.get("title", "").lower()
            or search_lower in a.get("description", "").lower()
        ]

    # Sort by date (newest first) and limit
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    all_articles = all_articles[:limit]

    result = {
        "category": CATEGORY_LABELS.get(category, category),
        "sources": list(sources.keys()),
        "count": len(all_articles),
        "articles": all_articles
    }

    # Generate summary
    if all_articles:
        titles = [a["title"] for a in all_articles[:3]]
        result["summary"] = f"Voici les dernières actualités {CATEGORY_LABELS.get(category, category).lower()}: " + "; ".join(titles)
    else:
        result["summary"] = "Aucun article trouvé pour ces critères."

    logger.info(f"[NewsTool] Fetched {len(all_articles)} articles")
    return result


async def _fetch_rss(url: str, source_name: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch and parse RSS feed"""
    articles = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

        # Parse XML
        root = ElementTree.fromstring(response.content)

        # Find items (RSS 2.0 format)
        items = root.findall(".//item")[:limit]

        # Try Atom format if no items found
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//atom:entry", ns)[:limit]

        for item in items:
            article = _parse_rss_item(item, source_name)
            if article:
                articles.append(article)

    except Exception as e:
        logger.error(f"[NewsTool] RSS fetch error for {source_name}: {e}")

    return articles


def _parse_rss_item(item: ElementTree.Element, source_name: str) -> Optional[Dict[str, Any]]:
    """Parse an RSS item/entry element"""
    try:
        # RSS 2.0 format
        title = item.findtext("title")
        link = item.findtext("link")
        description = item.findtext("description")
        pub_date = item.findtext("pubDate")

        # Atom format fallback
        if not title:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            title = item.findtext("atom:title", namespaces=ns)
            link_el = item.find("atom:link", ns)
            link = link_el.get("href") if link_el is not None else None
            description = item.findtext("atom:summary", namespaces=ns) or item.findtext("atom:content", namespaces=ns)
            pub_date = item.findtext("atom:published", namespaces=ns) or item.findtext("atom:updated", namespaces=ns)

        if not title:
            return None

        # Clean HTML from description
        if description:
            description = _clean_html(description)[:300]

        return {
            "title": html.unescape(title.strip()) if title else "",
            "link": link,
            "description": description,
            "source": source_name.replace("_", " ").title(),
            "published": pub_date or ""
        }

    except Exception as e:
        logger.error(f"[NewsTool] RSS parse error: {e}")
        return None


def _clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


async def get_headlines(limit: int = 5) -> Dict[str, Any]:
    """
    Get top headlines from all categories

    Args:
        limit: Number of articles per category

    Returns:
        Headlines from all categories
    """
    logger.info(f"[NewsTool] Getting headlines")

    results = {
        "categories": {},
        "total_count": 0
    }

    for category in ["france", "tech", "international"]:
        news = await get_news(category=category, limit=limit)
        if "error" not in news:
            results["categories"][category] = {
                "label": CATEGORY_LABELS.get(category, category),
                "articles": news.get("articles", [])
            }
            results["total_count"] += len(news.get("articles", []))

    return results


def register_news_tool():
    """Register the news tool with the registry"""
    registry = get_tool_registry()

    # Main news tool
    news_tool = ToolDefinition(
        name="get_news",
        description="Obtient les dernières actualités par catégorie (france, tech, international, science). Utilise des flux RSS gratuits.",
        category=ToolCategory.NEWS,
        parameters={
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Catégorie d'actualités: france, tech, international, science",
                    "enum": ["france", "tech", "international", "science"]
                },
                "source": {
                    "type": "string",
                    "description": "Source spécifique (optionnel): le_monde, hackernews, bbc, etc."
                },
                "limit": {
                    "type": "integer",
                    "description": "Nombre d'articles à retourner (1-10, défaut: 5)"
                },
                "search": {
                    "type": "string",
                    "description": "Terme de recherche pour filtrer les articles"
                }
            },
            "required": []
        },
        handler=get_news,
        rate_limit=20
    )
    registry.register(news_tool)

    # Headlines tool
    headlines_tool = ToolDefinition(
        name="get_headlines",
        description="Obtient les gros titres de toutes les catégories d'actualités en un coup d'œil.",
        category=ToolCategory.NEWS,
        parameters={
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Nombre d'articles par catégorie (1-5, défaut: 5)"
                }
            },
            "required": []
        },
        handler=get_headlines,
        rate_limit=10
    )
    registry.register(headlines_tool)

    logger.info("[NewsTool] News tools registered")
