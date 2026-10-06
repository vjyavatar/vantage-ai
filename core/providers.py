import os
PROVIDER_CONFIG = {
    "openai": {"env_key": "OPENAI_API_KEY"},
    "deepseek": {"env_key": "DEEPSEEK_API_KEY"},
    "anthropic": {"env_key": "ANTHROPIC_API_KEY"},
    "xai": {"env_key": "XAI_API_KEY"},
    "openrouter": {"env_key": "OPENROUTER_API_KEY"},
}
def get_available_providers():
    return {name: bool(os.environ.get(cfg["env_key"], "").strip()) for name, cfg in PROVIDER_CONFIG.items()}
def call_provider(*args, **kwargs):
    return {"success": False, "error": "not configured"}
def verify_answer(prompt, answer, task_type="general"):
    return {"verified": bool(answer and len(answer) > 20), "score": 0.7, "reason": "heuristic"}
