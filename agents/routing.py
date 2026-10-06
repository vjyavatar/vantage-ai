import random
from core.config import CHEAP_SIDE, PREMIUM_SIDE

class RoutingExecutionAgent:
    def __init__(self, state, monitor, averaging):
        self.state = state
        self.monitor = monitor
        self.averaging = averaging
    def execute_side(self, job, side):
        candidates = self.monitor.get_cheapest_for_task(job.task_type, side=side)
        if not candidates:
            return None
        price = candidates[0]
        cost = price.cost_for_tokens(800, 250)
        success = random.random() < price.success_rate
        self.averaging.add_fill(side, price.provider, price.model, cost, 800, 250, job.task_type, success, 1.0 if success else 0.0)
        return {"side": side, "provider": price.provider, "model": price.model, "cost": cost, "success": success}
    def run_job(self, job):
        self.state.total_jobs += 1
        results = {"job_id": job.job_id, "fills": [], "locked": None}
        for side in (CHEAP_SIDE, PREMIUM_SIDE):
            fill = self.execute_side(job, side)
            if fill:
                results["fills"].append(fill)
        locked = self.averaging.lock_arbitrage(job)
        if locked:
            results["locked"] = {"arb_id": locked.arb_id, "edge": locked.edge, "blended": locked.blended_cost, "pnl": locked.realized_pnl}
        return results
