import asyncio
import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from config import ConfigManager  # noqa: E402
from memory import ConversationMemory  # noqa: E402
from tools.google_search import get_current_datetime  # noqa: E402
from tools.weather import get_current_city, get_weather  # noqa: E402


def metric_summary(name: str, durations: List[float], successes: int, total: int) -> Dict[str, Any]:
    if not durations:
        return {
            "benchmark": name,
            "runs": total,
            "successes": successes,
            "success_rate_pct": round((successes / total) * 100, 2) if total else 0,
            "avg_ms": None,
            "min_ms": None,
            "max_ms": None,
            "std_dev_ms": None,
            "p95_ms": None,
        }

    sorted_durations = sorted(durations)
    p95_index = max(0, min(len(sorted_durations) - 1, int(0.95 * (len(sorted_durations) - 1))))
    return {
        "benchmark": name,
        "runs": total,
        "successes": successes,
        "success_rate_pct": round((successes / total) * 100, 2) if total else 0,
        "avg_ms": round(statistics.mean(durations), 2),
        "min_ms": round(min(durations), 2),
        "max_ms": round(max(durations), 2),
        "std_dev_ms": round(statistics.pstdev(durations), 2) if len(durations) > 1 else 0.0,
        "p95_ms": round(sorted_durations[p95_index], 2),
    }


async def benchmark_async_callable(
    name: str,
    fn: Callable[[], Awaitable[Any]],
    runs: int = 5,
) -> Dict[str, Any]:
    durations: List[float] = []
    successes = 0

    for _ in range(runs):
        started = time.perf_counter()
        try:
            result = await fn()
            result_text = str(result).strip() if result is not None else ""
            looks_like_error = result_text.lower().startswith("error") or "an error occurred" in result_text.lower()
            if result_text not in ("", "Unknown") and not looks_like_error:
                successes += 1
                durations.append((time.perf_counter() - started) * 1000)
        except Exception:
            pass

    return metric_summary(name, durations, successes, runs)


def summarize_existing_event_log() -> Dict[str, Any]:
    log_path = ROOT / "backend" / "logs" / "experiment_events.jsonl"
    if not log_path.exists():
        return {"event_log_present": False}

    total = 0
    tool_events = 0
    tool_successes = 0
    tool_durations: List[float] = []

    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            total += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if row.get("event_type") != "tool_invocation":
                continue

            tool_events += 1
            payload = row.get("payload", {})
            if payload.get("status") == "success":
                tool_successes += 1
            duration = payload.get("duration_ms")
            if isinstance(duration, (int, float)):
                tool_durations.append(float(duration))

    summary = {
        "event_log_present": True,
        "total_logged_events": total,
        "tool_events": tool_events,
        "tool_success_rate_pct": round((tool_successes / tool_events) * 100, 2)
        if tool_events
        else None,
        "tool_avg_latency_ms": round(statistics.mean(tool_durations), 2)
        if tool_durations
        else None,
    }
    return summary


async def main():
    parser = argparse.ArgumentParser(description="Run local benchmark suite for J.A.R.V.I.S.")
    parser.add_argument("--runs", type=int, default=5, help="Number of runs per benchmark.")
    args = parser.parse_args()

    cfg = ConfigManager()
    mem = ConversationMemory(user_id=cfg.get_user_id(), mem0_api_key=cfg.get_mem0_key())

    results = []
    results.append(
        await benchmark_async_callable("mds_calculation", mem.get_personalisation_score, runs=args.runs)
    )
    results.append(
        await benchmark_async_callable("get_current_datetime", get_current_datetime, runs=args.runs)
    )
    results.append(await benchmark_async_callable("get_current_city", get_current_city, runs=args.runs))

    if cfg.get_openweather_key():
        results.append(
            await benchmark_async_callable(
                "get_weather",
                lambda: get_weather("Delhi"),
                runs=args.runs,
            )
        )

    summary = {
        "config": {
            "user_id": cfg.get_user_id(),
            "mds_enabled": cfg.is_mds_enabled(),
            "openweather_configured": bool(cfg.get_openweather_key()),
            "n8n_configured": bool(cfg.get_n8n_url()),
            "benchmark_runs": args.runs,
        },
        "benchmarks": results,
        "existing_event_log_summary": summarize_existing_event_log(),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
