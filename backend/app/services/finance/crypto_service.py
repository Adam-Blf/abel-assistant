"""
A.B.E.L - Cryptocurrency Service
Integrates CoinGecko, CoinCap, Binance
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.logging import logger


class CryptoService:
    """
    Cryptocurrency service integrating:
    - CoinGecko (FREE - most comprehensive)
    - CoinCap (FREE - real-time)
    - Binance Public API
    - CryptoCompare
    """

    COINGECKO_API = "https://api.coingecko.com/api/v3"
    COINCAP_API = "https://api.coincap.io/v2"
    BINANCE_API = "https://api.binance.com/api/v3"
    CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data"

    # ========================================
    # COINGECKO API (FREE - No auth)
    # ========================================
    async def coingecko_prices(
        self,
        ids: List[str] = None,
        vs_currencies: str = "eur,usd",
    ) -> Dict[str, Any]:
        """Get current prices for cryptocurrencies"""
        try:
            ids = ids or ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/simple/price",
                    params={
                        "ids": ",".join(ids),
                        "vs_currencies": vs_currencies,
                        "include_24hr_change": "true",
                        "include_market_cap": "true",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CoinGecko prices error: {e}")
        return {}

    async def coingecko_market(
        self,
        vs_currency: str = "eur",
        order: str = "market_cap_desc",
        per_page: int = 100,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get market data for top cryptocurrencies"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/coins/markets",
                    params={
                        "vs_currency": vs_currency,
                        "order": order,
                        "per_page": per_page,
                        "page": page,
                        "sparkline": "false",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CoinGecko market error: {e}")
        return []

    async def coingecko_coin(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed coin data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/coins/{coin_id}",
                    params={
                        "localization": "false",
                        "tickers": "true",
                        "market_data": "true",
                        "community_data": "true",
                        "developer_data": "false",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CoinGecko coin error: {e}")
        return None

    async def coingecko_trending(self) -> List[Dict[str, Any]]:
        """Get trending coins"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/search/trending",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("coins", [])
        except Exception as e:
            logger.error(f"CoinGecko trending error: {e}")
        return []

    async def coingecko_history(
        self,
        coin_id: str,
        days: int = 30,
        vs_currency: str = "eur",
    ) -> Dict[str, Any]:
        """Get price history"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/coins/{coin_id}/market_chart",
                    params={
                        "vs_currency": vs_currency,
                        "days": days,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CoinGecko history error: {e}")
        return {}

    async def coingecko_search(self, query: str) -> List[Dict[str, Any]]:
        """Search cryptocurrencies"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/search",
                    params={"query": query},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("coins", [])
        except Exception as e:
            logger.error(f"CoinGecko search error: {e}")
        return []

    async def coingecko_global(self) -> Dict[str, Any]:
        """Get global crypto market data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API}/global",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json().get("data", {})
        except Exception as e:
            logger.error(f"CoinGecko global error: {e}")
        return {}

    # ========================================
    # COINCAP API (FREE - Real-time)
    # ========================================
    async def coincap_assets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top assets from CoinCap"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINCAP_API}/assets",
                    params={"limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"CoinCap assets error: {e}")
        return []

    async def coincap_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get specific asset from CoinCap"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINCAP_API}/assets/{asset_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
        except Exception as e:
            logger.error(f"CoinCap asset error: {e}")
        return None

    async def coincap_rates(self) -> List[Dict[str, Any]]:
        """Get exchange rates"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINCAP_API}/rates",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"CoinCap rates error: {e}")
        return []

    # ========================================
    # BINANCE API (FREE - No auth for public)
    # ========================================
    async def binance_price(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Get current price from Binance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_API}/ticker/price",
                    params={"symbol": symbol},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Binance price error: {e}")
        return None

    async def binance_24h(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Get 24h stats from Binance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_API}/ticker/24hr",
                    params={"symbol": symbol},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Binance 24h error: {e}")
        return None

    async def binance_all_prices(self) -> List[Dict[str, Any]]:
        """Get all prices from Binance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_API}/ticker/price",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Binance all prices error: {e}")
        return []

    # ========================================
    # PORTFOLIO TRACKING
    # ========================================
    async def calculate_portfolio_value(
        self,
        holdings: Dict[str, float],  # {"bitcoin": 0.5, "ethereum": 2}
        vs_currency: str = "eur",
    ) -> Dict[str, Any]:
        """Calculate portfolio value"""
        coin_ids = list(holdings.keys())
        prices = await self.coingecko_prices(coin_ids, vs_currency)

        total_value = 0
        breakdown = {}

        for coin_id, amount in holdings.items():
            if coin_id in prices and vs_currency in prices[coin_id]:
                price = prices[coin_id][vs_currency]
                value = price * amount
                total_value += value
                breakdown[coin_id] = {
                    "amount": amount,
                    "price": price,
                    "value": value,
                    "change_24h": prices[coin_id].get(f"{vs_currency}_24h_change"),
                }

        return {
            "total_value": total_value,
            "currency": vs_currency,
            "breakdown": breakdown,
        }

    async def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """Get Fear & Greed Index"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.alternative.me/fng/",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [{}])[0]
        except Exception as e:
            logger.error(f"Fear & Greed error: {e}")
        return None
