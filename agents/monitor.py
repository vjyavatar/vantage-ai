"""Price & Quality Monitor Agent."""
from __future__ import annotations
import logging
import random
from typing import Dict, List
from core.models import ProviderPrice, SystemState
from core.config import SEED_PRICES

logger = logging.getLogger("arb.monitor")

class PriceMonitorAgent:
    def __init__(self, state: SystemState):
        self.state = state
        self._seed_prices()

    def _seed_prices(self) -> None:
        for p in SEED_PRICES:
            key = f"{p['provider']}:{p['model']}"
            self.state.prices[key] = ProviderPrice(**p)
        logger.info("Seeded %s provider prices", len(self.state.prices))

    def refresh(self, volatility: float = 0.04):
        for price in self.state.prices.values():
            factor = 1.0 + random.uniform(-volatility, volatility)
            price.input_per_mtok = max(0.01, price.input_per_mtok * factor)
            price.output_per_mtok = max(0.02, price.output_per_mtok * factor)
            price.latency_ms = max(80.0, price.latency_ms * (1 + random.uniform(-0.1, 0.15)))
            price.success_rate = min(0.98, max(0.55, price.success_rate + random.uniform(-0.02, 0.02)))
            price.available = random.random() > 0.03
        return self.state.prices

    def get_cheapest_for_task(self, task_type: str, side: str = "cheap") -> List[ProviderPrice]:
        candidates = [p for p in self.state.prices.values() if p.available and (task_type in p.task_types or "general" in p.task_types)]
        if side == "cheap":
            candidates.sort(key=lambda x: x.blended_3_1)
        else:
            candidates.sort(key=lambda x: (-x.success_rate, x.blended_3_1))
        return candidates[:5]

    def snapshot(self) -> Dict:
        return {k: {"blended": round(v.blended_3_1, 4), "success": round(v.success_rate, 3), "latency": round(v.latency_ms, 0), "available": v.available} for k, v in self.state.prices.items()}
