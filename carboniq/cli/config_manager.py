"""
CarbonIQ CLI Configuration Manager
Stores and retrieves persistent user configuration such as API keys and backend URL.
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".carboniq"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_REMOTE_URL = "https://carboniq-backend-duel.onrender.com/api"


def get_config() -> Dict[str, Any]:
    """Load configuration from ~/.carboniq/config.json"""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config_value(key: str, value: Any):
    """Save a key-value pair to ~/.carboniq/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = get_config()
    cfg[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get_api_key() -> Optional[str]:
    """
    Get configured CarbonIQ API Key.
    Checks:
    1. ~/.carboniq/config.json
    2. CARBONIQ_API_KEY environment variable
    """
    return get_config().get("api_key") or os.getenv("CARBONIQ_API_KEY")


def get_api_url() -> str:
    """
    Get configured CarbonIQ Backend API URL.
    Checks:
    1. ~/.carboniq/config.json
    2. CARBONIQ_API_URL environment variable
    3. Production URL default
    """
    return get_config().get("api_url") or os.getenv("CARBONIQ_API_URL") or DEFAULT_REMOTE_URL
