"""
Configuration for the live Computational Arbitrage System.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

for d in [DATA_DIR, LOGS_DIR, CONFIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TARGET_MARGIN = 0.15
MAX_BLENDED_COST_RATIO = 0.85
CHEAP_SIDE = "cheap"
PREMIUM_SIDE = "premium"

SEED_PRICES = [
    {"provider": "deepseek", "model": "deepseek-v4-flash", "input_per_mtok": 0.14, "output_per_mtok": 0.28, "latency_ms": 420, "success_rate": 0.78, "task_types": ["general", "coding"]},
    {"provider": "together", "model": "llama-4-maverick", "input_per_mtok": 0.27, "output_per_mtok": 0.85, "latency_ms": 380, "success_rate": 0.80, "task_types": ["general", "coding"]},
    {"provider": "fireworks", "model": "qwen3.8-flash", "input_per_mtok": 0.11, "output_per_mtok": 0.38, "latency_ms": 350, "success_rate": 0.76, "task_types": ["general"]},
    {"provider": "groq", "model": "llama-3.3-70b", "input_per_mtok": 0.59, "output_per_mtok": 0.79, "latency_ms": 180, "success_rate": 0.82, "task_types": ["general", "reasoning"]},
    {"provider": "xai", "model": "grok-4.5", "input_per_mtok": 2.00, "output_per_mtok": 6.00, "latency_ms": 520, "success_rate": 0.88, "task_types": ["general", "coding", "reasoning"]},
    {"provider": "anthropic", "model": "claude-sonnet-5", "input_per_mtok": 2.00, "output_per_mtok": 10.00, "latency_ms": 610, "success_rate": 0.91, "task_types": ["coding", "reasoning"]},
    {"provider": "openai", "model": "gpt-5.6-luna", "input_per_mtok": 0.20, "output_per_mtok": 1.20, "latency_ms": 450, "success_rate": 0.86, "task_types": ["general", "coding"]},
    {"provider": "openai", "model": "gpt-5.6-sol", "input_per_mtok": 2.00, "output_per_mtok": 12.00, "latency_ms": 580, "success_rate": 0.92, "task_types": ["coding", "reasoning"]},
    {"provider": "anthropic", "model": "claude-opus-5.5", "input_per_mtok": 4.00, "output_per_mtok": 20.00, "latency_ms": 780, "success_rate": 0.94, "task_types": ["reasoning", "coding"]},
    {"provider": "google", "model": "gemini-3.1-pro", "input_per_mtok": 2.00, "output_per_mtok": 12.00, "latency_ms": 540, "success_rate": 0.89, "task_types": ["general", "reasoning"]},
]

MAX_INVENTORY_UNITS = 500
MAX_DAILY_LOSS = 50.0
MIN_EDGE_TO_LOCK = 0.01
DEFAULT_CUSTOMER_PRICE = 0.08
DEFAULT_INPUT_TOKENS = 1200
DEFAULT_OUTPUT_TOKENS = 400
