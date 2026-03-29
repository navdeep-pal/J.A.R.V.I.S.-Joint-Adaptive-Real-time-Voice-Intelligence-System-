import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional


ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "docs" / "results"
BENCHMARK_PATH = RESULTS_DIR / "local_benchmark_results.json"
EVENT_SUMMARY_PATH = RESULTS_DIR / "event_log_summary.json"
HUMAN_CSV_PATH = ROOT / "docs" / "MDS_Human_Evaluation_Sheet.csv"
OUTPUT_MD_PATH = RESULTS_DIR / "paper_ready_summary.md"


def load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_human_summary() -> Dict[str, Optional[float]]:
    if not HUMAN_CSV_PATH.exists():
        return {
            "baseline_count": 0,
            "mds_count": 0,
            "baseline_avg": None,
            "mds_avg": None,
            "delta": None,
            "percent_improvement": None,
        }

    baseline_scores: List[float] = []
    mds_scores: List[float] = []

    with HUMAN_CSV_PATH.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            score = safe_float(row.get("overall_quality_score_1_to_5", ""))
            if score is None:
                continue

            condition = (row.get("condition") or "").strip().lower()
            if condition == "baseline":
                baseline_scores.append(score)
            elif condition == "mds_enabled":
                mds_scores.append(score)

    baseline_avg = mean(baseline_scores) if baseline_scores else None
    mds_avg = mean(mds_scores) if mds_scores else None
    delta = (mds_avg - baseline_avg) if baseline_avg is not None and mds_avg is not None else None
    pct = ((delta / baseline_avg) * 100) if baseline_avg and delta is not None else None

    return {
        "baseline_count": len(baseline_scores),
        "mds_count": len(mds_scores),
        "baseline_avg": round(baseline_avg, 3) if baseline_avg is not None else None,
        "mds_avg": round(mds_avg, 3) if mds_avg is not None else None,
        "delta": round(delta, 3) if delta is not None else None,
        "percent_improvement": round(pct, 2) if pct is not None else None,
    }


def format_metric(value) -> str:
    return "N/A" if value is None else str(value)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    benchmark = load_json(BENCHMARK_PATH) or {}
    event_summary = load_json(EVENT_SUMMARY_PATH) or {}
    human_summary = load_human_summary()

    benchmark_rows = []
    for item in benchmark.get("benchmarks", []):
        benchmark_rows.append(
            "| {benchmark} | {runs} | {successes} | {success_rate_pct} | {avg_ms} | {min_ms} | {max_ms} |".format(
                benchmark=item.get("benchmark", "unknown"),
                runs=format_metric(item.get("runs")),
                successes=format_metric(item.get("successes")),
                success_rate_pct=format_metric(item.get("success_rate_pct")),
                avg_ms=format_metric(item.get("avg_ms")),
                min_ms=format_metric(item.get("min_ms")),
                max_ms=format_metric(item.get("max_ms")),
            )
        )

    tool_summary = event_summary.get("tool_summary", {})
    md = [
        "# Paper-Ready Experimental Summary",
        "",
        "## Local Runtime Benchmarks",
        "",
        "| Benchmark | Runs | Successes | Success Rate (%) | Avg Latency (ms) | Min (ms) | Max (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    md.extend(benchmark_rows or ["| No benchmark data available | N/A | N/A | N/A | N/A | N/A | N/A |"])

    md.extend(
        [
            "",
            "## Live Event Log Summary",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Event log present | {format_metric(event_summary.get('event_log_present'))} |",
            f"| Total logged events | {format_metric(event_summary.get('total_events'))} |",
            f"| Tool event count | {format_metric(tool_summary.get('tool_event_count'))} |",
            f"| Tool success rate (%) | {format_metric(tool_summary.get('tool_success_rate_pct'))} |",
            f"| Tool avg latency (ms) | {format_metric(tool_summary.get('tool_avg_latency_ms'))} |",
            f"| Tool p95 latency (ms) | {format_metric(tool_summary.get('tool_p95_latency_ms'))} |",
            "",
            "## Human Evaluation Summary",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Baseline scored sessions | {format_metric(human_summary.get('baseline_count'))} |",
            f"| MDS scored sessions | {format_metric(human_summary.get('mds_count'))} |",
            f"| Baseline average | {format_metric(human_summary.get('baseline_avg'))} |",
            f"| MDS average | {format_metric(human_summary.get('mds_avg'))} |",
            f"| Absolute delta | {format_metric(human_summary.get('delta'))} |",
            f"| Percent improvement | {format_metric(human_summary.get('percent_improvement'))} |",
            "",
            "## Notes",
            "",
            "- Use only rows with real measurements in the paper.",
            "- If human evaluation remains empty, do not claim user-rating improvements.",
            "- If event logs are empty, do not claim live MCP tool success metrics.",
        ]
    )

    OUTPUT_MD_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Generated: {OUTPUT_MD_PATH}")


if __name__ == "__main__":
    main()
