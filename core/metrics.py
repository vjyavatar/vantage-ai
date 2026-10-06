from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
from datetime import datetime, timezone
import collections

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

@dataclass
class MetricPoint:
    ts: str
    pnl: float = 0.0
    inflow: float = 0.0
    outflow: float = 0.0
    jobs: int = 0
    locked: int = 0
    blended_avg: float = 0.0
    cheap_avg: float = 0.0
    premium_avg: float = 0.0

class MetricsStore:
    def __init__(self, maxlen=300):
        self.points = collections.deque(maxlen=maxlen)
        self.total_inflow = self.total_outflow = self.total_revenue = 0.0
        self.total_jobs = self.total_locked = self.active_sessions = 0
        self.recent_events = collections.deque(maxlen=50)
    def record_job(self, customer_paid, provider_cost, locked, blended, cheap, premium):
        edge = max(0.0, customer_paid - provider_cost) if locked else 0.0
        self.total_inflow += customer_paid
        self.total_outflow += provider_cost
        self.total_revenue += edge
        self.total_jobs += 1
        if locked:
            self.total_locked += 1
        point = MetricPoint(utcnow_iso(), self.total_revenue, self.total_inflow, self.total_outflow, self.total_jobs, self.total_locked, blended, cheap, premium)
        self.points.append(point)
        self.recent_events.appendleft({"ts": point.ts, "type": "LOCK" if locked else "FILL", "inflow": customer_paid, "outflow": provider_cost, "edge": edge, "blended": blended})
    def snapshot(self):
        return {"total_inflow": round(self.total_inflow, 4), "total_outflow": round(self.total_outflow, 4), "total_revenue": round(self.total_revenue, 4), "total_jobs": self.total_jobs, "total_locked": self.total_locked, "active_sessions": self.active_sessions, "lock_rate": round(self.total_locked / max(1, self.total_jobs) * 100, 1), "series": [asdict(p) for p in self.points], "recent_events": list(self.recent_events)[:25]}
