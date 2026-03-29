import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict

logger = logging.getLogger(__name__)

LOGS_DIR = Path(__file__).resolve().parent / "logs"
EVENT_LOG_FILE = LOGS_DIR / "experiment_events.jsonl"
_write_lock = Lock()


def log_experiment_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Append one structured experiment event as JSONL.
    This keeps later analysis simple and scriptable.
    """
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload,
        }
        with _write_lock:
            with EVENT_LOG_FILE.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning("Failed to write experiment event: %s", exc)
