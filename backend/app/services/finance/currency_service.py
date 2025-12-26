"""
A.B.E.L - Currency Exchange Service
Integrates ExchangeRate-API, Fixer, Open Exchange Rates
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from app.core.config import settings
from app.core.logging import logger


class CurrencyService:
    """
    Currency exchange service integrating:
    - ExchangeRate-API (FREE tier available)
    - Fixer.io
    - Open Exchange Rates
    - FreeCurrencyAPI
    """

    EXCHANGERATE_API = "https://api.exchangerate-api.com/v4"
    FIXER_API = "http://data.fixer.io/api"
    FRANKFURTER_API = "https://api.frankfurter.app"  # FREE, no auth
    FREECURRENCY_API = "https://api.freecurrencyapi.com/v1"

    # Common currency codes
    CURRENCIES = {
        "EUR": "Euro",
        "USD": "US Dollar",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "CHF": "Swiss Franc",
        "CAD": "Canadian Dollar",
        "AUD": "Australian Dollar",
        "CNY": "Chinese Yuan",
        "INR": "Indian Rupee",
        "BRL": "Brazilian Real",
        "MXN": "Mexican Peso",
        "KRW": "South Korean Won",
        "SGD": "Singapore Dollar",
        "HKD": "Hong Kong Dollar",
        "NOK": "Norwegian Krone",
        "SEK": "Swedish Krona",
        "DKK": "Danish Krone",
        "NZD": "New Zealand Dollar",
        "ZAR": "South African Rand",
        "RUB": "Russian Ruble",
        "TRY": "Turkish Lira",
        "PLN": "Polish Zloty",
        "THB": "Thai Baht",
        "IDR": "Indonesian Rupiah",
        "MYR": "Malaysian Ringgit",
        "PHP": "Philippine Peso",
        "CZK": "Czech Koruna",
        "ILS": "Israeli Shekel",
        "AED": "UAE Dirham",
        "SAR": "Saudi Riyal",
    }

    def __init__(self):
        self.fixer_key = getattr(settings, 'fixer_api_key', '')
        self.freecurrency_key = getattr(settings, 'freecurrency_api_key', '')

    # ========================================
    # FRANKFURTER API (FREE - No auth)
    # ========================================
    async def frankfurter_latest(
        self,
        base: str = "EUR",
        symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get latest exchange rates"""
        try:
            params = {"from": base}
            if symbols:
                params["to"] = ",".join(symbols)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FRANKFURTER_API}/latest",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Frankfurter latest error: {e}")
        return {}

    async def frankfurter_convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> Optional[Dict[str, Any]]:
        """Convert currency"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FRANKFURTER_API}/latest",
                    params={
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Frankfurter convert error: {e}")
        return None

    async def frankfurter_historical(
        self,
        date: str,  # YYYY-MM-DD
        base: str = "EUR",
        symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get historical exchange rates"""
        try:
            params = {"from": base}
            if symbols:
                params["to"] = ",".join(symbols)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FRANKFURTER_API}/{date}",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Frankfurter historical error: {e}")
        return {}

    async def frankfurter_timeseries(
        self,
        start_date: str,
        end_date: str,
        base: str = "EUR",
        symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get time series exchange rates"""
        try:
            params = {"from": base}
            if symbols:
                params["to"] = ",".join(symbols)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FRANKFURTER_API}/{start_date}..{end_date}",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Frankfurter timeseries error: {e}")
        return {}

    async def frankfurter_currencies(self) -> Dict[str, str]:
        """Get available currencies"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FRANKFURTER_API}/currencies",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Frankfurter currencies error: {e}")
        return {}

    # ========================================
    # EXCHANGERATE-API (FREE tier)
    # ========================================
    async def exchangerate_latest(self, base: str = "EUR") -> Dict[str, Any]:
        """Get latest rates from ExchangeRate-API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.EXCHANGERATE_API}/latest/{base}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"ExchangeRate-API error: {e}")
        return {}

    # ========================================
    # HELPER FUNCTIONS
    # ========================================
    async def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> Dict[str, Any]:
        """Convert currency amount"""
        result = await self.frankfurter_convert(amount, from_currency, to_currency)

        if result:
            converted = result.get("rates", {}).get(to_currency, 0)
            return {
                "from": from_currency,
                "to": to_currency,
                "amount": amount,
                "result": converted,
                "rate": converted / amount if amount > 0 else 0,
                "date": result.get("date"),
            }

        return {"error": "Conversion failed"}

    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Optional[float]:
        """Get exchange rate between two currencies"""
        result = await self.frankfurter_latest(from_currency, [to_currency])
        if result and "rates" in result:
            return result["rates"].get(to_currency)
        return None

    async def get_popular_rates(
        self,
        base: str = "EUR",
    ) -> Dict[str, float]:
        """Get rates for popular currencies"""
        popular = ["USD", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY"]
        result = await self.frankfurter_latest(base, popular)
        return result.get("rates", {})

    def get_currency_name(self, code: str) -> str:
        """Get currency name from code"""
        return self.CURRENCIES.get(code.upper(), code)

    def get_all_currencies(self) -> Dict[str, str]:
        """Get all supported currencies"""
        return self.CURRENCIES

    async def calculate_multi_currency(
        self,
        amount: float,
        base: str,
        targets: List[str],
    ) -> Dict[str, float]:
        """Calculate amount in multiple currencies"""
        result = await self.frankfurter_latest(base, targets)
        rates = result.get("rates", {})

        converted = {}
        for currency, rate in rates.items():
            converted[currency] = round(amount * rate, 2)

        return converted
