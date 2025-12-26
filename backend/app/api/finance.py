"""
A.B.E.L - Finance API Routes
Crypto, Stocks, Currency
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.finance.crypto_service import CryptoService
from app.services.finance.stock_service import StockService
from app.services.finance.currency_service import CurrencyService

router = APIRouter(prefix="/finance", tags=["Finance"])

# Service instances
crypto_service = CryptoService()
stock_service = StockService()
currency_service = CurrencyService()


# ========================================
# CRYPTO ENDPOINTS
# ========================================
@router.get("/crypto/price/{coin_id}")
async def get_crypto_price(
    coin_id: str,
    currency: str = Query("usd", description="Target currency (usd, eur, etc.)"),
):
    """Get current price of a cryptocurrency"""
    price = await crypto_service.get_price(coin_id, currency)
    if price is None:
        raise HTTPException(status_code=404, detail="Coin not found")
    return {"coin": coin_id, "currency": currency, "price": price}


@router.get("/crypto/prices")
async def get_crypto_prices(
    coins: str = Query(..., description="Comma-separated coin IDs"),
    currency: str = Query("usd"),
):
    """Get prices for multiple cryptocurrencies"""
    coin_list = [c.strip() for c in coins.split(",")]
    prices = await crypto_service.get_prices(coin_list, currency)
    return {"currency": currency, "prices": prices}


@router.get("/crypto/market")
async def get_crypto_market(
    currency: str = Query("usd"),
    order: str = Query("market_cap_desc"),
    per_page: int = Query(100, ge=1, le=250),
    page: int = Query(1, ge=1),
):
    """Get cryptocurrency market data"""
    market = await crypto_service.get_market(currency, order, per_page, page)
    return {"currency": currency, "data": market, "count": len(market)}


@router.get("/crypto/{coin_id}")
async def get_crypto_details(coin_id: str):
    """Get detailed cryptocurrency information"""
    coin = await crypto_service.get_coin_details(coin_id)
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin


@router.get("/crypto/{coin_id}/history")
async def get_crypto_history(
    coin_id: str,
    days: int = Query(30, ge=1, le=365),
    currency: str = Query("usd"),
):
    """Get cryptocurrency price history"""
    history = await crypto_service.get_price_history(coin_id, days, currency)
    return {"coin": coin_id, "days": days, "history": history}


@router.get("/crypto/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies"""
    trending = await crypto_service.get_trending()
    return {"trending": trending}


@router.get("/crypto/search")
async def search_crypto(q: str = Query(..., description="Search query")):
    """Search cryptocurrencies"""
    results = await crypto_service.search_coins(q)
    return {"results": results, "count": len(results)}


@router.get("/crypto/exchanges")
async def get_crypto_exchanges(per_page: int = Query(100, ge=1, le=250)):
    """Get cryptocurrency exchanges"""
    exchanges = await crypto_service.get_exchanges(per_page)
    return {"exchanges": exchanges, "count": len(exchanges)}


@router.get("/crypto/global")
async def get_global_crypto_data():
    """Get global cryptocurrency market data"""
    data = await crypto_service.get_global_data()
    return data


# ========================================
# STOCKS ENDPOINTS
# ========================================
@router.get("/stocks/quote/{symbol}")
async def get_stock_quote(symbol: str):
    """Get stock quote"""
    quote = await stock_service.get_quote(symbol.upper())
    if not quote:
        raise HTTPException(status_code=404, detail="Stock not found")
    return quote


@router.get("/stocks/search")
async def search_stocks(q: str = Query(..., description="Search query")):
    """Search stocks by name or symbol"""
    results = await stock_service.search(q)
    return {"results": results, "count": len(results)}


@router.get("/stocks/{symbol}/intraday")
async def get_stock_intraday(
    symbol: str,
    interval: str = Query("5min", regex="^(1min|5min|15min|30min|60min)$"),
):
    """Get intraday stock data"""
    data = await stock_service.get_intraday(symbol.upper(), interval)
    return {"symbol": symbol.upper(), "interval": interval, "data": data}


@router.get("/stocks/{symbol}/daily")
async def get_stock_daily(symbol: str):
    """Get daily stock data"""
    data = await stock_service.get_daily(symbol.upper())
    return {"symbol": symbol.upper(), "data": data}


@router.get("/stocks/{symbol}/profile")
async def get_stock_profile(symbol: str):
    """Get company profile"""
    profile = await stock_service.get_company_profile(symbol.upper())
    if not profile:
        raise HTTPException(status_code=404, detail="Company not found")
    return profile


@router.get("/stocks/{symbol}/news")
async def get_stock_news(symbol: str):
    """Get company news"""
    news = await stock_service.get_company_news(symbol.upper())
    return {"symbol": symbol.upper(), "news": news}


@router.get("/stocks/market/news")
async def get_market_news(category: str = Query("general")):
    """Get market news"""
    news = await stock_service.get_market_news(category)
    return {"category": category, "news": news}


# ========================================
# CURRENCY ENDPOINTS
# ========================================
@router.get("/currency/rates")
async def get_exchange_rates(base: str = Query("EUR", description="Base currency")):
    """Get exchange rates for a base currency"""
    rates = await currency_service.get_rates(base.upper())
    return {"base": base.upper(), "rates": rates}


@router.get("/currency/convert")
async def convert_currency(
    amount: float = Query(..., description="Amount to convert"),
    from_currency: str = Query(..., alias="from", description="Source currency"),
    to_currency: str = Query(..., alias="to", description="Target currency"),
):
    """Convert between currencies"""
    result = await currency_service.convert(amount, from_currency.upper(), to_currency.upper())
    if result is None:
        raise HTTPException(status_code=400, detail="Conversion failed")
    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "result": result,
    }


@router.get("/currency/history")
async def get_currency_history(
    base: str = Query("EUR"),
    target: str = Query("USD"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """Get historical exchange rates"""
    history = await currency_service.get_history(
        base.upper(), target.upper(), start_date, end_date
    )
    return {
        "base": base.upper(),
        "target": target.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "history": history,
    }


@router.get("/currency/currencies")
async def get_available_currencies():
    """Get list of available currencies"""
    currencies = await currency_service.get_currencies()
    return {"currencies": currencies}
