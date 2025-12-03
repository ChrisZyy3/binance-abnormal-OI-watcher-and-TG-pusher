from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict

import aiohttp

BINANCE_FUTURES_REST = "https://fapi.binance.com"


@dataclass
class OIReading:
    symbol: str
    open_interest: float
    price: float


class BinanceDataSource:
    """Minimal Binance client for open interest and price."""

    def __init__(self, session: aiohttp.ClientSession, price_cache_ttl: float = 5.0):
        self.session = session
        self.price_cache_ttl = price_cache_ttl
        self._price_cache: Dict[str, tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def fetch_open_interest(self, symbol: str) -> float:
        url = f"{BINANCE_FUTURES_REST}/fapi/v1/openInterest"
        params = {"symbol": symbol.upper()}
        async with self.session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return float(data["openInterest"])

    async def fetch_price(self, symbol: str) -> float:
        async with self._lock:
            cached = self._price_cache.get(symbol)
            if cached and cached[1] > asyncio.get_event_loop().time():
                return cached[0]

        url = f"{BINANCE_FUTURES_REST}/fapi/v1/ticker/price"
        params = {"symbol": symbol.upper()}
        async with self.session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()
            price = float(data["price"])

        async with self._lock:
            expires_at = asyncio.get_event_loop().time() + self.price_cache_ttl
            self._price_cache[symbol] = (price, expires_at)
        return price

    async def fetch_oi_reading(self, symbol: str) -> OIReading:
        oi, price = await asyncio.gather(
            self.fetch_open_interest(symbol), self.fetch_price(symbol)
        )
        return OIReading(symbol=symbol.upper(), open_interest=oi, price=price)
