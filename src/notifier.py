from __future__ import annotations

import asyncio
from typing import Optional

import aiohttp


class TelegramNotifier:
    """Send formatted alerts to a Telegram bot chat."""

    def __init__(self, token: Optional[str], chat_id: Optional[str]):
        self.token = token
        self.chat_id = chat_id
        self._lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return bool(self.token and self.chat_id)

    async def send_message(self, session: aiohttp.ClientSession, text: str) -> None:
        if not self.configured:
            raise RuntimeError("Telegram configuration missing")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
        async with self._lock:
            async with session.post(url, data=payload, timeout=10) as resp:
                resp.raise_for_status()
                # consume response to free connection
                await resp.text()

    @staticmethod
    def format_alert(symbol: str, change: float, pct_change: float, price: float) -> str:
        direction = "⬆️" if change > 0 else "⬇️"
        pct_display = f"{pct_change:.2%}"
        change_abs = f"{change:.4f}"
        return (
            f"*Open Interest Alert*\n"
            f"Symbol: `{symbol}`\n"
            f"Direction: {direction} ({pct_display})\n"
            f"Change: {change_abs}\n"
            f"Price: {price:.2f} USDT"
        )
