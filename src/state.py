from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SymbolState:
    last_oi: float
    last_seen: datetime
    last_alert: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "SymbolState":
        return cls(
            last_oi=float(data["last_oi"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            last_alert=datetime.fromisoformat(data["last_alert"]) if data.get("last_alert") else None,
        )

    def to_dict(self) -> Dict[str, str]:
        payload = asdict(self)
        payload["last_seen"] = self.last_seen.isoformat()
        payload["last_alert"] = self.last_alert.isoformat() if self.last_alert else None
        return payload


class StateStore:
    """Persist symbol-level state in a small JSON file."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Dict[str, SymbolState]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as fp:
            raw = json.load(fp)
        return {symbol: SymbolState.from_dict(value) for symbol, value in raw.items()}

    def save(self, states: Dict[str, SymbolState]) -> None:
        payload = {symbol: state.to_dict() for symbol, state in states.items()}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
