"""Run temporal neural-window benchmarks on normalized Allen sessions.

The benchmark requires artifacts exported with temporal region-rate metadata:
`trial.metadata["region_rates_by_window"]`. Older artifacts are skipped instead
of being coerced into temporal data, because that would create a misleading
scientific result.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target, materialize_target_session
from neurotwin_mvp.benchmark import run_temporal_window_benchmark


ROOT = Path(__file__).resolve().parents[1]


def summarize_windows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate temporal-window gains across analyzed sessions."""
    grouped: dict[str, list[float]] = defaultdict(list)
    validity: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["window_name"])].append(float(row["gain_over_baseline"]))
        validity[str(row["window_name"])].append(float(row["valid_trial_fraction"]))
    return {
        window: {
            "n_sessions": len(values),
            "mean_gain": mean(values),
            "median_gain": median(values),
            "positive_gain_fraction": sum(1 for value in values if value > 0.0) / len(values),
            "mean_valid_trial_fraction": mean(validity[window]),
        }
        for window, values in sorted(grouped.items())
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write per-session temporal-window rows as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a concise temporal-window report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen temporal-window benchmark: {payload['target_name']}",
        "",
        "## Summary",
        "",
        f"- Sessions considered: {payload['n_sessions_considered']}",
        f"- Sessions analyzed: {payload['n_sessions_analyzed']}",
        f"- Skipped sessions: {payload['n_sessions_skipped']}",
        f"- Mean all-window gain: {_fmt(payload['mean_all_windows_gain'])}",
        "",
        "## Window Ranking",
        "",
        "| window | sessions | mean gain | median gain | positive gain fraction | valid trial fraction |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    ranked = sorted(
        payload["window_summary"].items(),
        key=lambda item: item[1]["mean_gain"],
        reverse=True,
    )
    for window, stats in ranked:
        lines.append(
            "| {window} | {n} | {mean_gain} | {median_gain} | {positive_fraction} | {valid_fraction} |".format(
                window=window,
                n=stats["n_sessions"],
                mean_gain=_fmt(stats["mean_gain"]),
                median_gain=_fmt(stats["median_gain"]),
                positive_fraction=_fmt(stats["positive_gain_fraction"]),
                valid_fraction=_fmt(stats["mean_valid_trial_fraction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Window gains are measured over the same task/image/history baseline.",
            "- Skipped sessions usually indicate old artifacts without temporal neural metadata.",
            "- The default decision window is post-stimulus and may include motor/response-related activity.",
            "- The `pre_response` window is dynamically truncated before response time and reports valid-trial coverage.",
            "- This is a predictive temporal analysis, not causal timing evidence.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def _valid_trial_fraction(session, target_name: TargetName, window_name: str) -> float:
    """Return fraction of target-labeled trials with a valid temporal window."""
    target_session = materialize_target_session(session, target_name)
    values = []
    for trial in target_session.trials:
        valid = trial.metadata.get("time_window_valid", {})
        values.append(bool(isinstance(valid, dict) and valid.get(window_name, False)))
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-names", nargs="+", default=["baseline", "stimulus", "decision", "pre_response"])
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_windows.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_windows.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_temporal_windows.md")
    args = parser.parse_args()

    target_name: TargetName = args.target_name
    session_reports = []
    window_rows: list[dict[str, Any]] = []
    skipped = []
    session_dirs = sorted(path.parent for path in args.datasets_root.glob("*/session.json"))
    for session_dir in session_dirs:
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, target_name)
        if args.require_usable_target and not diagnostic.usable:
            skipped.append({"session_id": session.session_id, "reason": "target_not_usable", "warnings": diagnostic.warnings})
            continue
        try:
            report = run_temporal_window_benchmark(
                session,
                target_name=target_name,
                window_names=args.window_names,
            )
        except ValueError as exc:
            skipped.append({"session_id": session.session_id, "reason": "temporal_metadata_missing", "warnings": [str(exc)]})
            continue
        session_reports.append(report.to_dict())
        for result in report.window_results:
            valid_fraction = _valid_trial_fraction(session, target_name, result.window_name)
            window_rows.append(
                {
                    "session_id": report.session_id,
                    "target_name": target_name,
                    "window_name": result.window_name,
                    "baseline_balanced_accuracy": report.baseline_balanced_accuracy,
                    "window_balanced_accuracy": result.balanced_accuracy,
                    "gain_over_baseline": result.gain_over_baseline,
                    "all_windows_balanced_accuracy": report.all_windows_balanced_accuracy,
                    "all_windows_gain": report.all_windows_gain,
                    "valid_trial_fraction": valid_fraction,
                }
            )

    all_gains = [float(item["all_windows_gain"]) for item in session_reports]
    payload = {
        "target_name": target_name,
        "window_names": args.window_names,
        "require_usable_target": bool(args.require_usable_target),
        "n_sessions_considered": len(session_dirs),
        "n_sessions_analyzed": len(session_reports),
        "n_sessions_skipped": len(skipped),
        "mean_all_windows_gain": mean(all_gains) if all_gains else None,
        "window_summary": summarize_windows(window_rows),
        "sessions": session_reports,
        "skipped_sessions": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, window_rows)
    write_markdown(args.out_md, payload)
    print(f"temporal_windows_json={args.out_json}")
    print(f"temporal_windows_csv={args.out_csv}")
    print(f"temporal_windows_md={args.out_md}")
    print(f"n_sessions_analyzed={payload['n_sessions_analyzed']}")
    print(f"n_sessions_skipped={payload['n_sessions_skipped']}")
    print(f"mean_all_windows_gain={_fmt(payload['mean_all_windows_gain'])}")


if __name__ == "__main__":
    main()
