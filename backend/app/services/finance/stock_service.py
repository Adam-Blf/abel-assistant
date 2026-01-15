"""
A.B.E.L - Stock Market Service
Integrates Alpha Vantage, Yahoo Finance, Finnhub
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class StockService:
    """
    Stock market service integrating:
    - Alpha Vantage
    - Yahoo Finance (unofficial)
    - Finnhub
    - IEX Cloud
    """

    ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
    YAHOO_API = "https://query1.finance.yahoo.com/v8/finance"
    FINNHUB_API = "https://finnhub.io/api/v1"

    def __init__(self):
        self.alpha_key = getattr(settings, 'alpha_vantage_api_key', '')
        self.finnhub_key = getattr(settings, 'finnhub_api_key', '')

    # ========================================
    # ALPHA VANTAGE API
    # ========================================
    async def alpha_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock quote from Alpha Vantage"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.ALPHA_VANTAGE_API,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.alpha_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("Global Quote")
        except Exception as e:
            logger.error(f"Alpha Vantage quote error: {e}")
        return None

    async def alpha_search(self, keywords: str) -> List[Dict[str, Any]]:
        """Search stocks on Alpha Vantage"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.ALPHA_VANTAGE_API,
                    params={
                        "function": "SYMBOL_SEARCH",
                        "keywords": keywords,
                        "apikey": self.alpha_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("bestMatches", [])
        except Exception as e:
            logger.error(f"Alpha Vantage search error: {e}")
        return []

    async def alpha_daily(
        self,
        symbol: str,
        outputsize: str = "compact",  # compact (100 days) or full
    ) -> Dict[str, Any]:
        """Get daily time series"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.ALPHA_VANTAGE_API,
                    params={
                        "function": "TIME_SERIES_DAILY",
                        "symbol": symbol,
                        "outputsize": outputsize,
                        "apikey": self.alpha_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Alpha Vantage daily error: {e}")
        return {}

    async def alpha_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.ALPHA_VANTAGE_API,
                    params={
                        "function": "OVERVIEW",
                        "symbol": symbol,
                        "apikey": self.alpha_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Alpha Vantage overview error: {e}")
        return None

    # ========================================
    # YAHOO FINANCE (Unofficial)
    # ========================================
    async def yahoo_quote(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get quotes from Yahoo Finance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.YAHOO_API}/quote",
                    params={"symbols": ",".join(symbols)},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("quoteResponse", {}).get("result", [])
        except Exception as e:
            logger.error(f"Yahoo quote error: {e}")
        return []

    # ========================================
    # FINNHUB API
    # ========================================
    async def finnhub_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote from Finnhub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FINNHUB_API}/quote",
                    params={"symbol": symbol, "token": self.finnhub_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Finnhub quote error: {e}")
        return None

    async def finnhub_news(
        self,
        category: str = "general",  # general, forex, crypto, merger
    ) -> List[Dict[str, Any]]:
        """Get market news from Finnhub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FINNHUB_API}/news",
                    params={"category": category, "token": self.finnhub_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Finnhub news error: {e}")
        return []

    async def finnhub_company_news(
        self,
        symbol: str,
        from_date: str,  # YYYY-MM-DD
        to_date: str,
    ) -> List[Dict[str, Any]]:
        """Get company-specific news"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FINNHUB_API}/company-news",
                    params={
                        "symbol": symbol,
                        "from": from_date,
                        "to": to_date,
                        "token": self.finnhub_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Finnhub company news error: {e}")
        return []

    async def finnhub_peers(self, symbol: str) -> List[str]:
        """Get company peers"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FINNHUB_API}/stock/peers",
                    params={"symbol": symbol, "token": self.finnhub_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Finnhub peers error: {e}")
        return []

    async def finnhub_recommendation(self, symbol: str) -> List[Dict[str, Any]]:
        """Get analyst recommendations"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FINNHUB_API}/stock/recommendation",
                    params={"symbol": symbol, "token": self.finnhub_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Finnhub recommendation error: {e}")
        return []

    # ========================================
    # PORTFOLIO TRACKING
    # ========================================
    async def track_portfolio(
        self,
        holdings: Dict[str, Dict[str, float]],  # {"AAPL": {"shares": 10, "avg_price": 150}}
    ) -> Dict[str, Any]:
        """Track portfolio performance"""
        symbols = list(holdings.keys())
        quotes = await self.yahoo_quote(symbols)

        total_value = 0
        total_cost = 0
        positions = []

        for quote in quotes:
            symbol = quote.get("symbol")
            if symbol in holdings:
                shares = holdings[symbol]["shares"]
                avg_price = holdings[symbol]["avg_price"]
                current_price = quote.get("regularMarketPrice", 0)

                position_value = shares * current_price
                position_cost = shares * avg_price
                gain_loss = position_value - position_cost
                gain_loss_pct = ((current_price / avg_price) - 1) * 100 if avg_price > 0 else 0

                total_value += position_value
                total_cost += position_cost

                positions.append({
                    "symbol": symbol,
                    "shares": shares,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "value": position_value,
                    "cost": position_cost,
                    "gain_loss": gain_loss,
                    "gain_loss_pct": gain_loss_pct,
                    "day_change": quote.get("regularMarketChange"),
                    "day_change_pct": quote.get("regularMarketChangePercent"),
                })

        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain_loss": total_value - total_cost,
            "total_gain_loss_pct": ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0,
            "positions": positions,
        }

    # ========================================
    # MARKET INDICES
    # ========================================
    async def get_indices(self) -> List[Dict[str, Any]]:
        """Get major market indices"""
        symbols = ["^GSPC", "^DJI", "^IXIC", "^FCHI", "^GDAXI", "^FTSE", "^N225"]
        return await self.yahoo_quote(symbols)
