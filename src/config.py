from __future__ import annotations

import os


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"{name} is required")
    return value


def get_meta_verify_token() -> str:
    return _require_env("META_VERIFY_TOKEN")


def get_meta_app_secret() -> str:
    return _require_env("META_APP_SECRET")


def should_debug_log_raw_payload() -> bool:
    return os.getenv("DEBUG_LOG_RAW_PAYLOAD", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

