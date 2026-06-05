"""Validate the selected microcircuit against Allen session stability.

The selected microcircuit is calibrated only from robust sessions. This script
then projects every usable stability-matrix session through that fixed circuit
and checks whether the predicted circuit state follows the independent
robust/mixed/fragile labels. A negative result is scientifically valid here:
it means the mechanistic scaffold is not yet externally discriminative.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.artifacts import read_session_artifact
from neurotwin_mvp.microcircuit import (
    calibrate_microcircuit_from_sessions,
    validate_microcircuit_against_stability,
)


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read one small CSV artifact as dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def robust_session_ids(stability_rows: list[dict[str, str]]) -> list[str]:
    """Return the stability-matrix sessions that passed all current controls."""
    return [row["session_id"] for row in stability_rows if row["status"] == "robust"]


def mean_region_drop(path: Path, region: str) -> float:
    """Estimate region contribution from the all-session ablation table."""
    rows = [row for row in read_csv(path) if row["region"] == region]
    values = [float(row["drop_from_full"]) for row in rows]
    return sum(values) / len(values) if values else 0.0


def load_sessions(datasets_root: Path, session_ids: set[str]) -> list:
    """Load normalized session artifacts for the requested session ids."""
    return [
        read_session_artifact(path.parent)
        for path in sorted(datasets_root.glob("*/session.json"))
        if path.parent.name in session_ids
    ]


def write_session_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write one row per validated session for manual audit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "session_id",
        "status",
        "stability_score",
        "n_trials",
        "mean_visual_excitation",
        "mean_visual_inhibition",
        "mean_basal_gate",
        "mean_action_logit",
        "mean_action_probability",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a concise human-readable validation report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen microcircuit validation",
        "",
        "## External stability test",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Probability/stability correlation: {payload['probability_stability_correlation']:.3f}"
        if payload["probability_stability_correlation"] is not None
        else "- Probability/stability correlation: not available",
        f"- Robust minus fragile probability: {payload['robust_minus_fragile_probability']:.3f}"
        if payload["robust_minus_fragile_probability"] is not None
        else "- Robust minus fragile probability: not available",
        f"- Robust minus mixed probability: {payload['robust_minus_mixed_probability']:.3f}"
        if payload["robust_minus_mixed_probability"] is not None
        else "- Robust minus mixed probability: not available",
        "",
        "## Robustness",
        "",
    ]
    bootstrap = payload["robustness"].get("bootstrap", {})
    null = payload["robustness"].get("null", {})
    if bootstrap:
        lines.extend(
            [
                "| metric | mean | ci95 low | median | ci95 high |",
                "| --- | ---: | ---: | ---: | ---: |",
                _summary_row("bootstrap robust-fragile", bootstrap["robust_minus_fragile"]),
                _summary_row("bootstrap correlation", bootstrap["correlation"]),
                "",
            ]
        )
    if null:
        lines.extend(
            [
                "| null metric | mean | ci95 low | median | ci95 high | p-value |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
                _null_row(
                    "null robust-fragile",
                    null["robust_minus_fragile"],
                    null["robust_minus_fragile_p_value"],
                ),
                _null_row("null correlation", null["correlation"], null["correlation_p_value"]),
                "",
            ]
        )
    lines.extend(
        [
        "## Group means",
        "",
        "| status | mean action probability | mean stability score |",
        "| --- | ---: | ---: |",
        ]
    )
    groups = sorted(payload["group_mean_action_probability"])
    for status in groups:
        lines.append(
            "| {status} | {probability:.3f} | {stability:.3f} |".format(
                status=status,
                probability=payload["group_mean_action_probability"][status],
                stability=payload["group_mean_stability_score"][status],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The circuit was calibrated from robust sessions and evaluated without per-session refitting.",
            "- A strong result would require a robust > mixed > fragile gradient and positive stability correlation.",
            "- This is predictive/mechanistic validation, not causal perturbation evidence.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary_row(label: str, summary: dict[str, Any]) -> str:
    """Format one bootstrap summary row."""
    return "| {label} | {mean:.3f} | {ci95_low:.3f} | {median:.3f} | {ci95_high:.3f} |".format(
        label=label,
        mean=summary["mean"],
        ci95_low=summary["ci95_low"],
        median=summary["median"],
        ci95_high=summary["ci95_high"],
    )


def _null_row(label: str, summary: dict[str, Any], p_value: float | None) -> str:
    """Format one permutation-null summary row."""
    p_value_text = "NA" if p_value is None else f"{p_value:.3f}"
    return (
        "| {label} | {mean:.3f} | {ci95_low:.3f} | {median:.3f} | "
        "{ci95_high:.3f} | {p_value} |"
    ).format(
        label=label,
        mean=summary["mean"],
        ci95_low=summary["ci95_low"],
        median=summary["median"],
        ci95_high=summary["ci95_high"],
        p_value=p_value_text,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--stability-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--regional-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--n-null", type=int, default=1000)
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_microcircuit_validation.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_microcircuit_validation.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_microcircuit_validation.md")
    args = parser.parse_args()

    stability_rows = read_csv(args.stability_csv)
    stability_ids = {row["session_id"] for row in stability_rows}
    sessions = load_sessions(args.datasets_root, stability_ids)
    robust_sessions = load_sessions(args.datasets_root, set(robust_session_ids(stability_rows)))
    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    calibration = calibrate_microcircuit_from_sessions(
        robust_sessions,
        robust_session_ids=robust_session_ids(stability_rows),
        visual_cortex_drop=mean_region_drop(args.regional_csv, "visual_cortex"),
        basal_ganglia_drop=mean_region_drop(args.regional_csv, "basal_ganglia"),
        temporal_gain=float(uncertainty["temporal_gain"]["all_sessions"]["mean"]),
        seed=args.seed,
    )
    report = validate_microcircuit_against_stability(
        calibration,
        sessions,
        stability_rows=stability_rows,
        n_bootstrap=args.n_bootstrap,
        n_null=args.n_null,
        seed=args.seed,
    )
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_session_csv(args.out_csv, payload["sessions"])
    write_markdown(args.out_md, payload)
    print(f"microcircuit_validation_json={args.out_json}")
    print(f"microcircuit_validation_csv={args.out_csv}")
    print(f"decision={payload['decision']}")


if __name__ == "__main__":
    main()
