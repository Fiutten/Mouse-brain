"""Run region-by-window ablation for Allen temporal features.

This script is intentionally downstream of the temporal permutation screen. Use
`--significant-only` to restrict interpretation to sessions that reject the
shuffled temporal-window null.
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
from neurotwin_mvp.behavioral_targets import TargetName, diagnose_target
from neurotwin_mvp.benchmark import run_temporal_regional_ablation


ROOT = Path(__file__).resolve().parents[1]


def load_significant_sessions(path: Path, alpha: float) -> set[str]:
    """Return sessions significant in the temporal permutation report."""
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(row["session_id"])
        for row in payload.get("sessions", [])
        if float(row.get("p_value", 1.0)) < alpha
    }


def summarize_regions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate leave-one-region-out drops across sessions."""
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["region"])].append(float(row["drop_from_full"]))
    return {
        region: {
            "n_sessions": len(values),
            "mean_drop_from_full": mean(values),
            "median_drop_from_full": median(values),
            "positive_drop_fraction": sum(1 for value in values if value > 0.0) / len(values),
        }
        for region, values in sorted(grouped.items())
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write per-session region rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a readable region-by-window ablation summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen temporal regional ablation: {payload['target_name']} / {payload['window_name']}",
        "",
        "## Summary",
        "",
        f"- Sessions considered: {payload['n_sessions_considered']}",
        f"- Sessions analyzed: {payload['n_sessions_analyzed']}",
        f"- Skipped sessions: {payload['n_sessions_skipped']}",
        f"- Significant-only mode: {str(payload['significant_only']).lower()}",
        f"- Mean full-window gain: {_fmt(payload['mean_full_window_gain'])}",
        "",
        "## Region Ranking",
        "",
        "| region | sessions | mean drop | median drop | positive drop fraction |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    ranked = sorted(
        payload["region_summary"].items(),
        key=lambda item: item[1]["mean_drop_from_full"],
        reverse=True,
    )
    for region, stats in ranked:
        lines.append(
            "| {region} | {n} | {mean_drop} | {median_drop} | {positive_fraction} |".format(
                region=region,
                n=stats["n_sessions"],
                mean_drop=_fmt(stats["mean_drop_from_full"]),
                median_drop=_fmt(stats["median_drop_from_full"]),
                positive_fraction=_fmt(stats["positive_drop_fraction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Positive drop means the temporal-window model worsened when that region feature was removed.",
            "- Use significant-only mode for the main interpretation; all-session mode is a sensitivity check.",
            "- This is predictive feature ablation, not causal lesion evidence.",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-name", default="pre_response")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--significant-only", action="store_true")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--permutation-report", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation.md")
    args = parser.parse_args()

    target_name: TargetName = args.target_name
    significant = load_significant_sessions(args.permutation_report, args.alpha)
    rows = []
    session_reports = []
    skipped = []
    session_dirs = sorted(path.parent for path in args.datasets_root.glob("*/session.json"))
    for session_dir in session_dirs:
        session = read_session_artifact(session_dir)
        diagnostic = diagnose_target(session, target_name)
        if args.require_usable_target and not diagnostic.usable:
            skipped.append({"session_id": session.session_id, "reason": "target_not_usable", "warnings": diagnostic.warnings})
            continue
        if args.significant_only and session.session_id not in significant:
            skipped.append({"session_id": session.session_id, "reason": "not_temporal_permutation_significant"})
            continue
        try:
            report = run_temporal_regional_ablation(
                session,
                window_name=args.window_name,
                target_name=target_name,
            )
        except ValueError as exc:
            skipped.append({"session_id": session.session_id, "reason": "temporal_window_unavailable", "warnings": [str(exc)]})
            continue
        session_reports.append(report.to_dict())
        for result in report.region_results:
            rows.append(
                {
                    "session_id": report.session_id,
                    "target_name": target_name,
                    "window_name": args.window_name,
                    "region": result.region,
                    "baseline_balanced_accuracy": report.baseline_balanced_accuracy,
                    "full_window_balanced_accuracy": report.full_window_balanced_accuracy,
                    "full_window_gain": report.full_window_gain,
                    "ablated_balanced_accuracy": result.ablated_balanced_accuracy,
                    "drop_from_full": result.drop_from_full,
                }
            )

    full_gains = [float(report["full_window_gain"]) for report in session_reports]
    payload = {
        "target_name": target_name,
        "window_name": args.window_name,
        "alpha": args.alpha,
        "significant_only": bool(args.significant_only),
        "n_sessions_considered": len(session_dirs),
        "n_sessions_analyzed": len(session_reports),
        "n_sessions_skipped": len(skipped),
        "mean_full_window_gain": mean(full_gains) if full_gains else None,
        "region_summary": summarize_regions(rows),
        "sessions": session_reports,
        "skipped_sessions": skipped,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, payload)
    print(f"temporal_regional_ablation_json={args.out_json}")
    print(f"temporal_regional_ablation_csv={args.out_csv}")
    print(f"temporal_regional_ablation_md={args.out_md}")
    print(f"n_sessions_analyzed={payload['n_sessions_analyzed']}")
    print(f"mean_full_window_gain={_fmt(payload['mean_full_window_gain'])}")


if __name__ == "__main__":
    main()
