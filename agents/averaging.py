import uuid
from core.models import LockedArb
from core.config import MAX_BLENDED_COST_RATIO, MIN_EDGE_TO_LOCK, CHEAP_SIDE

class InventoryAveragingAgent:
    def __init__(self, state):
        self.state = state
    def add_fill(self, side, provider, model, cost, tokens_in, tokens_out, task_type, success, units=1.0, metadata=None):
        if success:
            bucket = self.state.cheap if side == CHEAP_SIDE else self.state.premium
            bucket.add(cost, units)
        return type("U", (), {"unit_id": "u"})()
    def blended_average(self):
        c, p = self.state.cheap, self.state.premium
        if c.total_units + p.total_units == 0:
            return 0.0
        return (c.average_cost * c.total_units + p.average_cost * p.total_units) / (c.total_units + p.total_units)
    def can_lock(self, customer_price):
        blended = self.blended_average()
        edge = customer_price - blended
        can = blended > 0 and blended < customer_price * MAX_BLENDED_COST_RATIO and edge >= MIN_EDGE_TO_LOCK and self.state.cheap.total_units > 0 and self.state.premium.total_units > 0
        return can, blended, edge
    def lock_arbitrage(self, job):
        can, blended, edge = self.can_lock(job.customer_price)
        if not can:
            return None
        self.state.total_pnl += edge
        self.state.successful_jobs += 1
        arb = LockedArb(str(uuid.uuid4())[:8], job.job_id, blended, job.customer_price, edge, edge)
        self.state.locked_arbs.append(arb)
        return arb
    def status(self):
        return {"cheap_avg": self.state.cheap.average_cost, "premium_avg": self.state.premium.average_cost, "blended_avg": self.blended_average(), "total_pnl": self.state.total_pnl, "locked_count": len(self.state.locked_arbs)}
