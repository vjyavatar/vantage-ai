from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from datetime import datetime, timezone
import json

def utcnow():
    return datetime.now(timezone.utc)

@dataclass
class ProviderPrice:
    provider: str
    model: str
    input_per_mtok: float
    output_per_mtok: float
    latency_ms: float = 500.0
    success_rate: float = 0.85
    available: bool = True
    task_types: List[str] = field(default_factory=lambda: ["general"])
    @property
    def blended_3_1(self):
        return (3 * self.input_per_mtok + self.output_per_mtok) / 4
    def cost_for_tokens(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens / 1_000_000) * self.input_per_mtok + (output_tokens / 1_000_000) * self.output_per_mtok

@dataclass
class AverageCostState:
    side: str
    total_cost: float = 0.0
    total_units: float = 0.0
    def add(self, cost, units=1.0):
        self.total_cost += cost
        self.total_units += units
    @property
    def average_cost(self):
        return self.total_cost / self.total_units if self.total_units else 0.0

@dataclass
class JobRequest:
    job_id: str
    prompt: str
    task_type: str = "general"
    customer_price: float = 0.05
    max_attempts: int = 3

@dataclass
class LockedArb:
    arb_id: str
    job_id: str
    blended_cost: float
    customer_price: float
    edge: float
    realized_pnl: float = 0.0

@dataclass
class SystemState:
    cheap: AverageCostState = field(default_factory=lambda: AverageCostState("cheap"))
    premium: AverageCostState = field(default_factory=lambda: AverageCostState("premium"))
    total_pnl: float = 0.0
    total_jobs: int = 0
    successful_jobs: int = 0
    prices: Dict[str, ProviderPrice] = field(default_factory=dict)
    locked_arbs: list = field(default_factory=list)
    inventory: list = field(default_factory=list)
    def to_dict(self):
        return {"cheap_avg": self.cheap.average_cost, "premium_avg": self.premium.average_cost, "total_pnl": self.total_pnl, "total_jobs": self.total_jobs}
    def save(self, path):
        Path = __import__("pathlib").Path
        Path(path).write_text("{}")
