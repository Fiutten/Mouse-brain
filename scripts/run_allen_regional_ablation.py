"""Run target-aware regional feature ablations on normalized Allen sessions.

This script is intentionally conservative. It consumes the normalized
`session.json` artifacts and uses the core benchmark stack only; no AllenSDK is
required. For each usable session, it compares:

- a non-neural task/image/history baseline;
- the same model plus all coarse region-rate features;
- leave-one-region-out variants.

The result is a predictive feature-ablation report. It is useful for selecting
region hypotheses, but it is not causal lesion evidence.
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
from neurotwin_mvp.benchmark import run_regional_ablation


ROOT = Path(__file__).resolve().parents[1]


def summarize_region_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate leave-one-region-out effects across sessions."""
    by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_region[str(row["region"])].append(row)

    summary: dict[str, Any] = {}
    for region, items in sorted(by_region.items()):
        drops = [float(item["drop_from_full"]) for item in items]
        positive = sum(1 for value in drops if value > 0.0)
        summary[region] = {
            "n_sessions": len(items),
            "mean_drop_from_full": mean(drops),
            "median_drop_from_full": median(drops),
            "positive_drop_fraction": positive / len(drops),
        }
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write region/session ablation rows as a tabular artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-readable regional ablation summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen regional ablation: {payload['target_name']}",
        "",
        "## Summary",
        "",
        f"- Sessions considered: {payload['n_sessions_considered']}",
        f"- Sessions analyzed: {payload['n_sessions_analyzed']}",
        f"- Skipped sessions: {payload['n_sessions_skipped']}",
        f"- Mean full neural gain: {_fmt(payload['mean_full_neural_gain'])}",
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
            "- Positive drop means performance decreased when that region feature was removed.",
            "- Negative drop means the leave-one-region-out model did not get worse; this can happen with noisy or redundant features.",
            "- This is predictive feature ablation, not biological lesion evidence.",
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
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--require-usable-target", action="store_true")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_regional_ablation.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_regional_ablation.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_regional_ablation.md")
    args = parser.parse_args()

    target_name: TargetName = args.target_name
    session_reports = []
    region_rows: list[dict[str, Any]] = []
    skipped = []
    for session_json in sorted(args.datasets_root.glob("*/session.json")):
        session = read_session_artifact(session_json.parent)
        diagnostic = diagnose_target(session, target_name)
        if args.require_usable_target and not diagnostic.usable:
            skipped.append(
                {
                    "session_id": session.session_id,
                    "warnings": diagnostic.warnings,
                }
            )
            continue
        report = run_regional_ablation(session, target_name=target_name)
        session_reports.append(report.to_dict())
        for result in report.region_results:
            region_rows.append(
                {
                    "session_id": report.session_id,
                    "target_name": target_name,
                    "region": result.region,
                    "baseline_balanced_accuracy": report.baseline_balanced_accuracy,
                    "full_neural_balanced_accuracy": report.full_neural_balanced_accuracy,
                    "full_neural_gain": report.full_neural_gain,
                    "ablated_balanced_accuracy": result.ablated_balanced_accuracy,
                    "drop_from_full": result.drop_from_full,
                }
            )

    full_gains = [float(item["full_neural_gain"]) for item in session_reports]
    payload = {
        "target_name": target_name,
        "require_usable_target": bool(args.require_usable_target),
        "n_sessions_considered": len(list(args.datasets_root.glob("*/session.json"))),
        "n_sessions_analyzed": len(session_reports),
        "n_sessions_skipped": len(skipped),
        "mean_full_neural_gain": mean(full_gains) if full_gains else None,
        "region_summary": summarize_region_rows(region_rows),
        "sessions": session_reports,
        "skipped_sessions": skipped,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, region_rows)
    write_markdown(args.out_md, payload)
    print(f"regional_ablation_json={args.out_json}")
    print(f"regional_ablation_csv={args.out_csv}")
    print(f"regional_ablation_md={args.out_md}")
    print(f"n_sessions_analyzed={payload['n_sessions_analyzed']}")
    print(f"mean_full_neural_gain={_fmt(payload['mean_full_neural_gain'])}")


if __name__ == "__main__":
    main()
