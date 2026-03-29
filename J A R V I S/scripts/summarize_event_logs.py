import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "backend" / "logs" / "experiment_events.jsonl"


def summarize_tool_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    tool_events = [e for e in events if e.get("event_type") == "tool_invocation"]
    durations = []
    status_counter: Counter[str] = Counter()
    tool_counter: Counter[str] = Counter()

    for event in tool_events:
        payload = event.get("payload", {})
        status = payload.get("status", "unknown")
        status_counter[status] += 1
        tool_counter[payload.get("tool_name", "unknown")] += 1
        duration = payload.get("duration_ms")
        if isinstance(duration, (int, float)):
            durations.append(float(duration))

    total = len(tool_events)
    success_count = status_counter.get("success", 0)
    sorted_durations = sorted(durations)
    p95 = None
    if sorted_durations:
        idx = max(0, min(len(sorted_durations) - 1, int(0.95 * (len(sorted_durations) - 1))))
        p95 = round(sorted_durations[idx], 2)

    return {
        "tool_event_count": total,
        "tool_success_count": success_count,
        "tool_success_rate_pct": round((success_count / total) * 100, 2) if total else None,
        "tool_avg_latency_ms": round(statistics.mean(durations), 2) if durations else None,
        "tool_min_latency_ms": round(min(durations), 2) if durations else None,
        "tool_max_latency_ms": round(max(durations), 2) if durations else None,
        "tool_p95_latency_ms": p95,
        "tool_status_breakdown": dict(status_counter),
        "tool_name_breakdown": dict(tool_counter),
    }


def main():
    if not LOG_PATH.exists():
        print(
            json.dumps(
                {
                    "event_log_present": False,
                    "path": str(LOG_PATH),
                },
                indent=2,
            )
        )
        return

    events: List[Dict[str, Any]] = []
    with LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    summary = {
        "event_log_present": True,
        "path": str(LOG_PATH),
        "total_events": len(events),
        "event_type_breakdown": dict(Counter(e.get("event_type", "unknown") for e in events)),
        "tool_summary": summarize_tool_events(events),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
