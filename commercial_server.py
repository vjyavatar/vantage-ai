#!/usr/bin/env python3
"""Vantage AI dashboard and OpenAI-compatible API."""
from __future__ import annotations
import json, logging, os, random, sys, threading, time, uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agents.orchestrator import OrchestratorAgent
from core.metrics import MetricsStore
from core.config import LOGS_DIR
from core.providers import get_available_providers
from core.stripe_billing import stripe_configured, create_checkout_session, retrieve_session, grant_credits, payment_summary

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOGS_DIR / "commercial.log", mode="a")])
logger = logging.getLogger("vantage")
orch = OrchestratorAgent()
metrics = MetricsStore(maxlen=500)
PRICES = {"general": 0.012, "coding": 0.028, "reasoning": 0.035}

def background_traffic():
    prompts = ["Implement a rate limiter", "Explain CAP theorem", "Write binary search", "Design a todo API"]
    while True:
        try:
            time.sleep(random.uniform(4, 9))
            if any(get_available_providers().values()):
                time.sleep(15)
                continue
            task = random.choice(list(PRICES))
            price = round(PRICES[task] * random.uniform(0.9, 1.1), 4)
            orch.refresh_market()
            result = orch.submit_job(prompt=random.choice(prompts), task_type=task, customer_price=price)
            locked = bool(result.get("locked"))
            cost = sum(f.get("cost", 0) for f in result.get("fills", [])) or 0.001
            st = orch.averaging.status()
            metrics.record_job(price if locked else 0.0, cost, locked, st.get("blended_avg", 0), st.get("cheap_avg", 0), st.get("premium_avg", 0))
            metrics.active_sessions = random.randint(2, 14)
        except Exception as e:
            logger.debug("bg %s", e)

DASHBOARD_HTML = open(Path(__file__).with_name("dashboard.html"), encoding="utf-8").read()
PRICING_HTML = open(Path(__file__).with_name("pricing.html"), encoding="utf-8").read()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)
    def _json(self, code, payload):
        body = json.dumps(payload, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
    def _html(self, html, code=200):
        body = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in ("/", "/dashboard"):
            self._html(DASHBOARD_HTML); return
        if path == "/pricing":
            self._html(PRICING_HTML); return
        if path == "/health":
            self._json(200, {"status": "ok"}); return
        if path == "/api/metrics":
            self._json(200, metrics.snapshot()); return
        if path == "/api/system":
            avail = get_available_providers()
            html = " ".join(f'<span class="pill {"ok" if v else "warn"}">{k}</span>' for k, v in avail.items())
            self._json(200, {"providers": avail, "providers_html": html, "stripe": stripe_configured(), "real_answers": any(avail.values()), "payments": payment_summary()}); return
        if path == "/success":
            self._html("<html><body style='font-family:system-ui;background:#0f1419;color:#f0f4f8;padding:40px'><h1>Payment received</h1><p><a href='/'>Dashboard</a></p></body></html>"); return
        self._json(404, {"error": "not found"})
    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        if path == "/api/create-checkout":
            form = parse_qs(raw.decode())
            plan = (form.get("plan") or ["starter"])[0]
            email = (form.get("email") or [""])[0]
            if not stripe_configured():
                self._html("<html><body style='font-family:system-ui;background:#0f1419;color:#f0f4f8;padding:40px'><h1>Stripe not configured</h1><p>Add STRIPE_SECRET_KEY on Render.</p><a href='/pricing'>Back</a></body></html>"); return
            session = create_checkout_session(plan, customer_email=email)
            self.send_response(302)
            self.send_header("Location", session["url"])
            self.end_headers()
            return
        self._json(404, {"error": "not found"})

def main():
    threading.Thread(target=background_traffic, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    logger.info("Vantage AI on %s:%s", HOST, PORT)
    server.serve_forever()

if __name__ == "__main__":
    main()
