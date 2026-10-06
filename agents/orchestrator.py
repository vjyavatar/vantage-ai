"""Orchestrator Agent."""
from __future__ import annotations
import logging
import uuid
from typing import List, Optional
from core.models import SystemState, JobRequest
from core.config import DEFAULT_CUSTOMER_PRICE, DATA_DIR
from agents.monitor import PriceMonitorAgent
from agents.averaging import InventoryAveragingAgent
from agents.routing import RoutingExecutionAgent

logger = logging.getLogger("arb.orchestrator")

class OrchestratorAgent:
    def __init__(self):
        self.state = SystemState()
        self.monitor = PriceMonitorAgent(self.state)
        self.averaging = InventoryAveragingAgent(self.state)
        self.routing = RoutingExecutionAgent(self.state, self.monitor, self.averaging)
        logger.info("Orchestrator online")

    def submit_job(self, prompt: str, task_type: str = "general", customer_price: float = DEFAULT_CUSTOMER_PRICE, max_attempts: int = 3) -> dict:
        job = JobRequest(job_id=str(uuid.uuid4())[:10], prompt=prompt, task_type=task_type, customer_price=customer_price, max_attempts=max_attempts)
        logger.info("JOB RECEIVED %s | type=%s | price=$%.4f", job.job_id, task_type, customer_price)
        return self.routing.run_job(job)

    def refresh_market(self) -> None:
        self.monitor.refresh()

    def status(self) -> dict:
        base = self.state.to_dict()
        base["averaging"] = self.averaging.status()
        base["prices_snapshot"] = self.monitor.snapshot()
        return base

    def save_state(self) -> str:
        path = str(DATA_DIR / "system_state.json")
        self.state.save(path)
        return path
