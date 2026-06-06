"""Test whether fragile Allen sessions express signal in alternative windows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.benchmark import run_temporal_window_permutation_test


ROOT = Path(__file__).resolve().parents[1]


def fragile_session_ids(path: Path) -> list[str]:
    """Return fragile session ids from the stability matrix."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            str(row["session_id"])
            for row in csv.DictReader(handle)
            if str(row["status"]) == "fragile"
        ]


def classify_rescue(rows: list[dict[str, Any]], alpha: float) -> str:
    """Classify whether an alternative window rescues a fragile session."""
    significant = {
        str(row["window_name"])
        for row in rows
        if float(row["observed_gain"]) > 0.0 and float(row["p_value"]) < alpha
    }
    if "stimulus" in significant:
        return "stimulus_window_rescue"
    if "decision" in significant:
        return "decision_window_rescue_motor_possible"
    if "baseline" in significant:
        return "baseline_state_signal"
    return "no_alternative_window_rescue"


def summarize(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """Aggregate per-window alternative evidence."""
    summary = {}
    for window in sorted({str(row["window_name"]) for row in rows}):
        window_rows = [row for row in rows if row["window_name"] == window]
        gains = [float(row["observed_gain"]) for row in window_rows]
        summary[window] = {
            "n_sessions": len(window_rows),
            "mean_gain": mean(gains),
            "positive_fraction": sum(value > 0.0 for value in gains) / len(gains),
            "significant_fraction": sum(float(row["p_value"]) < alpha for row in window_rows) / len(window_rows),
        }
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-readable alternative-window report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Alternative temporal windows in fragile Allen sessions",
        "",
        "## Summary",
        "",
        f"- Fragile sessions: {len(payload['session_classification'])}",
        f"- Permutations per session/window: {payload['n_permutations']}",
        "",
        "| window | sessions | mean gain | positive fraction | significant fraction |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for window, stats in payload["window_summary"].items():
        lines.append(
            f"| {window} | {stats['n_sessions']} | {stats['mean_gain']:.3f} | "
            f"{stats['positive_fraction']:.3f} | {stats['significant_fraction']:.3f} |"
        )
    lines.extend(["", "## Session Classification", "", "| session | classification |", "| --- | --- |"])
    for session_id, classification in payload["session_classification"].items():
        lines.append(f"| {session_id} | `{classification}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A stimulus-window rescue suggests earlier sensory-aligned predictivity.",
            "- A decision-window rescue may reflect later decision or motor-related activity and is not a pre-response rescue.",
            "- No rescue supports a genuine broad temporal-null interpretation under the current coarse features.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--windows", nargs="+", default=["baseline", "stimulus", "decision"])
    parser.add_argument("--n-permutations", type=int, default=50)
    parser.add_argument("--seed", type=int, default=83)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--stability-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_alternative_windows.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_alternative_windows.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragile_alternative_windows.md")
    args = parser.parse_args()

    rows = []
    classifications = {}
    skipped = []
    for session_id in fragile_session_ids(args.stability_csv):
        session_dir = args.datasets_root / session_id
        session = read_session_artifact(session_dir)
        session_rows = []
        for index, window in enumerate(args.windows):
            try:
                report = run_temporal_window_permutation_test(
                    session,
                    target_name=args.target_name,
                    window_name=window,
                    n_permutations=args.n_permutations,
                    seed=args.seed + index,
                )
            except ValueError as exc:
                skipped.append({"session_id": session_id, "window_name": window, "reason": str(exc)})
                continue
            row = report.to_dict()
            row["significant"] = bool(row["p_value"] < args.alpha)
            row["warnings"] = "; ".join(row["warnings"])
            rows.append(row)
            session_rows.append(row)
        classifications[session_id] = classify_rescue(session_rows, args.alpha)

    payload = {
        "target_name": args.target_name,
        "windows": args.windows,
        "n_permutations": args.n_permutations,
        "alpha": args.alpha,
        "window_summary": summarize(rows, args.alpha),
        "session_classification": classifications,
        "rows": rows,
        "skipped": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"alternative_windows_json={args.out_json}")
    print(f"alternative_windows_md={args.out_md}")
    print(f"fragile_sessions={len(classifications)}")


if __name__ == "__main__":
    main()
