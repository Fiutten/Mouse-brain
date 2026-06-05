"""Run the calibrated generative surrogate for current Allen evidence."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.generative import GenerativeCalibration, simulate_evidence_sessions


ROOT = Path(__file__).resolve().parents[1]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def regional_drop_means(path: Path) -> dict[str, float]:
    """Aggregate region drops for generator calibration."""
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in read_csv_rows(path):
        grouped[str(row["region"])].append(float(row["drop_from_full"]))
    return {region: mean(values) for region, values in grouped.items()}


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a compact surrogate report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    calibration = payload["calibration"]
    lines = [
        f"# Allen generative surrogate: {calibration['target_name']} / {calibration['window_name']}",
        "",
        "## Calibration",
        "",
        f"- Empirical sessions: {calibration['n_sessions']}",
        f"- Temporal gain mean: {calibration['temporal_gain_mean']:.3f}",
        f"- Temporal gain CI95: [{calibration['temporal_gain_ci95'][0]:.3f}, {calibration['temporal_gain_ci95'][1]:.3f}]",
        f"- Seed: {calibration['seed']}",
        "",
        "## Generated Summary",
        "",
        f"- Generated mean temporal gain: {payload['mean_temporal_gain']:.3f}",
        "",
        "| region | generated mean drop | calibrated empirical drop |",
        "| --- | ---: | ---: |",
    ]
    for region, value in sorted(payload["mean_regional_drops"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {region} | {value:.3f} | {calibration['regional_drops'][region]:.3f} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This surrogate generates session-level evidence, not spike trains or biological microcircuits.",
            "- It is useful for stress-testing graph/agent workflows before adding mechanistic detail.",
            "- Empirical reports remain the source of scientific claims.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-name", default="pre_response")
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--n-generated-sessions", type=int, default=10)
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--region-drop-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_generative_surrogate.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_generative_surrogate.md")
    args = parser.parse_args()

    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    temporal = uncertainty["temporal_gain"]["all_sessions"]
    calibration = GenerativeCalibration(
        target_name=args.target_name,
        window_name=args.window_name,
        n_sessions=int(temporal["n_sessions"]),
        temporal_gain_mean=float(temporal["mean"]),
        temporal_gain_ci95=[float(temporal["ci95_low"]), float(temporal["ci95_high"])],
        regional_drops=regional_drop_means(args.region_drop_csv),
        seed=args.seed,
    )
    report = simulate_evidence_sessions(calibration, n_generated_sessions=args.n_generated_sessions)
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"generative_surrogate_json={args.out_json}")
    print(f"generative_surrogate_md={args.out_md}")
    print(f"mean_temporal_gain={payload['mean_temporal_gain']:.3f}")
    print(f"n_generated_sessions={len(payload['generated_sessions'])}")


if __name__ == "__main__":
    main()
