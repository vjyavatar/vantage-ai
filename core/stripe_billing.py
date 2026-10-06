import os
PLANS = {
    "starter": {"name": "Vantage AI Starter", "amount_cents": 2900, "credits": 200, "description": "200 verified jobs"},
    "growth": {"name": "Vantage AI Growth", "amount_cents": 9900, "credits": 900, "description": "900 verified jobs"},
    "scale": {"name": "Vantage AI Scale", "amount_cents": 29900, "credits": 3500, "description": "3500 verified jobs"},
}
def stripe_configured():
    return bool(os.environ.get("STRIPE_SECRET_KEY", "").strip())
def create_checkout_session(plan_id, customer_email=None, success_url=None, cancel_url=None):
    raise RuntimeError("Stripe checkout requires STRIPE_SECRET_KEY")
def retrieve_session(session_id):
    return {}
def grant_credits(*args, **kwargs):
    return None
def payment_summary():
    return {"stripe_configured": stripe_configured(), "total_payments": 0}
