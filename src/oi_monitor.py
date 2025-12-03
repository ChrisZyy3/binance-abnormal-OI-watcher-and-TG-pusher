from __future__ import annotations

import asyncio
import logging
from typing import Dict

import aiohttp

from .config import AppConfig
from .datasource import BinanceDataSource
from .detector import OIDetector
from .notifier import TelegramNotifier
from .state import StateStore, SymbolState

logger = logging.getLogger(__name__)


class OIMonitor:
    def __init__(self, config: AppConfig):
        self.config = config
        self.state_store = StateStore(config.storage_path)
        self.detector = OIDetector(
            percentage_threshold=config.percentage_threshold,
            absolute_threshold=config.absolute_threshold,
            cooldown_seconds=config.cooldown_seconds,
        )
        self.notifier = TelegramNotifier(config.telegram_token, config.telegram_chat_id)
        self.states: Dict[str, SymbolState] = {}

    async def initialize(self):
        self.states = self.state_store.load()
        logger.info("Loaded %d symbol states", len(self.states))

    async def run(self):
        await self.initialize()
        async with aiohttp.ClientSession() as session:
            datasource = BinanceDataSource(session, price_cache_ttl=self.config.price_cache_ttl)
            tasks = [self._poll_symbol(symbol, datasource, session) for symbol in self.config.symbols]
            await asyncio.gather(*tasks)

    async def _poll_symbol(self, symbol: str, datasource: BinanceDataSource, session: aiohttp.ClientSession):
        while True:
            try:
                await self._handle_symbol_once(symbol, datasource, session)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Error while polling %s", symbol)
            await asyncio.sleep(self.config.poll_interval)

    async def _handle_symbol_once(self, symbol: str, datasource: BinanceDataSource, session: aiohttp.ClientSession):
        reading = await datasource.fetch_oi_reading(symbol)
        observed_at = StateStore.now()
        state = self.states.get(symbol)
        new_state, detection = self.detector.evaluate(symbol, reading.open_interest, observed_at, state)
        self.states[symbol] = new_state
        self.state_store.save(self.states)

        if detection.should_alert:
            logger.info(
                "%s change detected: %.4f (%.2f%%)",
                symbol,
                detection.change_abs,
                detection.change_pct * 100,
            )
            await self._send_alert(symbol, detection.change_abs, detection.change_pct, reading.price, session)
        else:
            logger.debug("%s change within threshold", symbol)

    async def _send_alert(self, symbol: str, change_abs: float, change_pct: float, price: float, session: aiohttp.ClientSession):
        if not self.notifier.configured:
            logger.warning("Telegram credentials missing; skipping alert for %s", symbol)
            return
        message = self.notifier.format_alert(symbol, change_abs, change_pct, price)
        await self.notifier.send_message(session, message)
