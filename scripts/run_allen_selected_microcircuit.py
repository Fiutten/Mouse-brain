"""Run the selected visual-cortex/basal-ganglia microcircuit layer."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.microcircuit import calibrate_microcircuit_from_sessions, run_selected_microcircuit


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def robust_session_ids(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [row["session_id"] for row in data["rows"] if row["status"] == "robust"]


def mean_region_drop(path: Path, region: str) -> float:
    rows = [row for row in read_csv(path) if row["region"] == region]
    values = [float(row["drop_from_full"]) for row in rows]
    return sum(values) / len(values) if values else 0.0


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    calibration = payload["calibration"]
    lines = [
        "# Allen selected microcircuit",
        "",
        "## Calibration",
        "",
        f"- Target: `{calibration['target_name']}`",
        f"- Window: `{calibration['window_name']}`",
        f"- Robust sessions: {', '.join(calibration['robust_session_ids'])}",
        f"- Temporal gain: {calibration['temporal_gain']:.3f}",
        f"- Visual-cortex drop: {calibration['visual_cortex_drop']:.3f}",
        f"- Basal-ganglia drop: {calibration['basal_ganglia_drop']:.3f}",
        "",
        "## Perturbations",
        "",
        "| perturbation | mean action probability | drop from intact |",
        "| --- | ---: | ---: |",
    ]
    for row in payload["perturbations"]:
        lines.append(
            "| {perturbation} | {mean_action_probability:.3f} | {drop_from_intact:.3f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a selected mechanistic scaffold for controlled graph edges.",
            "- Perturbations are in-silico subpopulation probes, not biological lesion evidence.",
            "- A useful microcircuit should reproduce directionality and prioritize follow-up hypotheses.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--stability-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.json")
    parser.add_argument("--regional-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--n-trials", type=int, default=300)
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_selected_microcircuit.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_selected_microcircuit.md")
    args = parser.parse_args()

    session_ids = robust_session_ids(args.stability_json)
    sessions = [
        read_session_artifact(path.parent)
        for path in sorted(args.datasets_root.glob("*/session.json"))
        if path.parent.name in set(session_ids)
    ]
    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    temporal_gain = float(uncertainty["temporal_gain"]["all_sessions"]["mean"])
    calibration = calibrate_microcircuit_from_sessions(
        sessions,
        robust_session_ids=session_ids,
        visual_cortex_drop=mean_region_drop(args.regional_csv, "visual_cortex"),
        basal_ganglia_drop=mean_region_drop(args.regional_csv, "basal_ganglia"),
        temporal_gain=temporal_gain,
        seed=args.seed,
    )
    report = run_selected_microcircuit(calibration, n_trials=args.n_trials)
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"selected_microcircuit_json={args.out_json}")
    print(f"selected_microcircuit_md={args.out_md}")
    print(f"intact_mean_action_probability={payload['intact_mean_action_probability']:.3f}")


if __name__ == "__main__":
    main()
