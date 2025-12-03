from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class AppConfig:
    """Runtime configuration for the OI watcher."""

    symbols: List[str] = field(default_factory=lambda: ["BTCUSDT"])
    poll_interval: float = 15.0
    percentage_threshold: float = 0.05
    absolute_threshold: float | None = None
    cooldown_seconds: float = 300.0
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    storage_path: Path = field(default_factory=lambda: Path(".state.json"))
    price_cache_ttl: float = 5.0


def _parse_symbols(raw: str | None) -> List[str]:
    if not raw:
        return ["BTCUSDT"]
    return [item.strip().upper() for item in raw.split(",") if item.strip()]


def load_config() -> AppConfig:
    """Load configuration from environment variables.

    Defaults are conservative so the script can run without additional setup.
    """

    symbols = _parse_symbols(os.getenv("SYMBOLS"))
    poll_interval = float(os.getenv("POLL_INTERVAL", "15"))
    pct_threshold = float(os.getenv("PCT_THRESHOLD", "0.05"))
    abs_threshold = os.getenv("ABS_THRESHOLD")
    abs_threshold_value = float(abs_threshold) if abs_threshold is not None else None
    cooldown = float(os.getenv("COOLDOWN", "300"))
    storage_path = Path(os.getenv("STATE_PATH", ".state.json"))
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    price_cache_ttl = float(os.getenv("PRICE_CACHE_TTL", "5"))

    return AppConfig(
        symbols=symbols,
        poll_interval=poll_interval,
        percentage_threshold=pct_threshold,
        absolute_threshold=abs_threshold_value,
        cooldown_seconds=cooldown,
        telegram_token=telegram_token,
        telegram_chat_id=telegram_chat_id,
        storage_path=storage_path,
        price_cache_ttl=price_cache_ttl,
    )
