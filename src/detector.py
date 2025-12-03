from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .state import SymbolState


@dataclass
class DetectionResult:
    should_alert: bool
    change_abs: float
    change_pct: float


class OIDetector:
    def __init__(self, percentage_threshold: float, absolute_threshold: Optional[float], cooldown_seconds: float):
        self.percentage_threshold = percentage_threshold
        self.absolute_threshold = absolute_threshold
        self.cooldown_seconds = cooldown_seconds

    def evaluate(self, symbol: str, oi_value: float, observed_at: datetime, state: SymbolState | None) -> tuple[SymbolState, DetectionResult]:
        if state is None:
            new_state = SymbolState(last_oi=oi_value, last_seen=observed_at)
            return new_state, DetectionResult(False, 0.0, 0.0)

        change_abs = oi_value - state.last_oi
        if state.last_oi == 0:
            change_pct = 0.0
        else:
            change_pct = change_abs / state.last_oi

        should_alert = self._passes_threshold(change_abs, change_pct) and self._outside_cooldown(state, observed_at)
        updated_state = SymbolState(last_oi=oi_value, last_seen=observed_at, last_alert=observed_at if should_alert else state.last_alert)
        return updated_state, DetectionResult(should_alert, change_abs, change_pct)

    def _passes_threshold(self, change_abs: float, change_pct: float) -> bool:
        if self.absolute_threshold is not None and abs(change_abs) >= self.absolute_threshold:
            return True
        return abs(change_pct) >= self.percentage_threshold

    def _outside_cooldown(self, state: SymbolState, observed_at: datetime) -> bool:
        if not state.last_alert:
            return True
        elapsed = (observed_at - state.last_alert).total_seconds()
        return elapsed >= self.cooldown_seconds
