"""
Expert Mode - Direct LLM API payload editing

Saves the JSON request to disk before sending so the user can hand-edit it.
Logs every request/response pair for later review and tuning.

Directory layout (inside llm-sim-poc/):
    expert_mode/
        pending_request.json   ← current payload, editable before send
        log.json               ← append-only history of all expert requests
"""

import os
import json
from datetime import datetime

EXPERT_DIR = os.path.join(os.path.dirname(__file__), "expert_mode")
PENDING_FILE = os.path.join(EXPERT_DIR, "pending_request.json")
LOG_FILE = os.path.join(EXPERT_DIR, "log.json")


def ensure_dir():
    os.makedirs(EXPERT_DIR, exist_ok=True)


# ── write / read pending payload ────────────────────────────────────────

def save_pending_request(payload: dict) -> str:
    """
    Write the full API payload to pending_request.json.
    Returns the absolute path (for display in the UI).
    """
    ensure_dir()
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return os.path.abspath(PENDING_FILE)


def load_pending_request() -> dict:
    """
    Read the (possibly hand-edited) payload back from disk.
    """
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def pending_exists() -> bool:
    return os.path.isfile(PENDING_FILE)


def clear_pending():
    if os.path.isfile(PENDING_FILE):
        os.remove(PENDING_FILE)


# ── append-only log ─────────────────────────────────────────────────────

def log_exchange(request_payload: dict, response_text: str, model: str, provider: str, user_prompt: str):
    """
    Append a request+response entry to log.json.
    Each entry contains everything needed to reproduce / compare later.
    """
    ensure_dir()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "user_prompt": user_prompt,
        "request_payload": request_payload,
        "response": response_text,
    }

    # Read existing log (or start fresh)
    log = []
    if os.path.isfile(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    return len(log)  # entry number


def get_log() -> list:
    """Return the full log (list of dicts)."""
    if not os.path.isfile(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_log_count() -> int:
    return len(get_log())


def write_pending_from_text(text: str) -> dict:
    """
    Validate JSON text and write it to pending_request.json.
    Returns {"ok": True, "path": "..."} on success or {"ok": False, "error": "..."} on failure.
    """
    ensure_dir()
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            return {"ok": False, "error": "Payload must be a JSON object (not array or primitive)"}
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"ok": True, "path": os.path.abspath(PENDING_FILE)}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
