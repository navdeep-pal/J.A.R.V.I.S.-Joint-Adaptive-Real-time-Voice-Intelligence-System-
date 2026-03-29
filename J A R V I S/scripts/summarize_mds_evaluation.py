import csv
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "docs" / "MDS_Human_Evaluation_Sheet.csv"


def safe_float(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    if not CSV_PATH.exists():
        print(f"Evaluation sheet not found: {CSV_PATH}")
        return

    baseline_scores = []
    mds_scores = []

    with CSV_PATH.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            overall = safe_float(row.get("overall_quality_score_1_to_5", ""))
            if overall is None:
                continue

            condition = (row.get("condition") or "").strip().lower()
            if condition == "baseline":
                baseline_scores.append(overall)
            elif condition == "mds_enabled":
                mds_scores.append(overall)

    baseline_avg = mean(baseline_scores) if baseline_scores else None
    mds_avg = mean(mds_scores) if mds_scores else None

    print("MDS Evaluation Summary")
    print("----------------------")
    print(f"Baseline sessions counted: {len(baseline_scores)}")
    print(f"MDS sessions counted: {len(mds_scores)}")
    print(f"Baseline average: {baseline_avg if baseline_avg is not None else 'N/A'}")
    print(f"MDS average: {mds_avg if mds_avg is not None else 'N/A'}")

    if baseline_avg is not None and mds_avg is not None:
        delta = round(mds_avg - baseline_avg, 3)
        pct = round((delta / baseline_avg) * 100, 2) if baseline_avg else None
        print(f"Absolute delta: {delta}")
        print(f"Percent improvement: {pct if pct is not None else 'N/A'}")


if __name__ == "__main__":
    main()
