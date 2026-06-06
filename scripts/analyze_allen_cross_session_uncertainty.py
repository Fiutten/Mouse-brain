"""Estimate cross-session uncertainty for temporal Allen results.

This script answers a narrow reviewer-facing question: are the current
`pre_response` and visual-cortex effects stable across sessions, or are they
mostly driven by one or two strong sessions?

It uses session-level bootstrap confidence intervals and leave-one-session-out
sensitivity. That is deliberately simple and transparent for the current
10-session cohort.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def percentile(values: list[float], q: float) -> float:
    """Return a linear-interpolated percentile for sorted or unsorted values."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be between 0 and 1")
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def bootstrap_ci(values: list[float], iterations: int, seed: int) -> dict[str, float]:
    """Bootstrap the mean of session-level values."""
    if not values:
        raise ValueError("values must not be empty")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in values]
        estimates.append(mean(sample))
    return {
        "mean": mean(values),
        "ci95_low": percentile(estimates, 0.025),
        "ci95_high": percentile(estimates, 0.975),
    }


def leave_one_out(values_by_session: dict[str, float]) -> list[dict[str, Any]]:
    """Compute leave-one-session-out means."""
    rows = []
    for session_id in sorted(values_by_session):
        remaining = [
            value
            for other_id, value in values_by_session.items()
            if other_id != session_id
        ]
        rows.append(
            {
                "left_out_session_id": session_id,
                "n_remaining": len(remaining),
                "mean": mean(remaining) if remaining else None,
            }
        )
    return rows


def summarize_values(values_by_session: dict[str, float], iterations: int, seed: int) -> dict[str, Any]:
    """Summarize one session-level metric with bootstrap and LOO sensitivity."""
    values = list(values_by_session.values())
    ci = bootstrap_ci(values, iterations, seed)
    loo = leave_one_out(values_by_session)
    loo_means = [float(row["mean"]) for row in loo if row["mean"] is not None]
    return {
        "n_sessions": len(values),
        "mean": ci["mean"],
        "median": median(values),
        "ci95_low": ci["ci95_low"],
        "ci95_high": ci["ci95_high"],
        "positive_fraction": sum(1 for value in values if value > 0.0) / len(values),
        "leave_one_out_min_mean": min(loo_means) if loo_means else None,
        "leave_one_out_max_mean": max(loo_means) if loo_means else None,
        "leave_one_out": loo,
    }


def permutation_gain_by_session(rows: list[dict[str, str]]) -> dict[str, float]:
    """Extract observed temporal gains by session."""
    return {
        str(row["session_id"]): float(row["observed_gain"])
        for row in rows
    }


def significant_sessions(rows: list[dict[str, str]], alpha: float) -> set[str]:
    """Return sessions significant under the temporal permutation test."""
    return {
        str(row["session_id"])
        for row in rows
        if float(row["p_value"]) < alpha
    }


def region_drop_by_session(rows: list[dict[str, str]], region: str) -> dict[str, float]:
    """Extract one region's drop from temporal regional ablation rows."""
    return {
        str(row["session_id"]): float(row["drop_from_full"])
        for row in rows
        if row["region"] == region
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write the uncertainty analysis in a compact reviewer-facing form."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen cross-session uncertainty",
        "",
        "## Summary",
        "",
        f"- Target: `{payload['target_name']}`",
        f"- Window: `{payload['window_name']}`",
        f"- Region: `{payload['region']}`",
        f"- Bootstrap iterations: {payload['bootstrap_iterations']}",
        "",
        "## Temporal Gain",
        "",
        "| cohort | sessions | mean | CI95 low | CI95 high | positive fraction | LOO min mean | LOO max mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ["all_sessions", "significant_sessions"]:
        stats = payload["temporal_gain"][name]
        lines.append(_summary_row(name, stats))
    lines.extend(
        [
            "",
            "## Regional Drop",
            "",
            "| cohort | sessions | mean | CI95 low | CI95 high | positive fraction | LOO min mean | LOO max mean |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name in ["all_sessions", "significant_sessions"]:
        stats = payload["regional_drop"][name]
        lines.append(_summary_row(name, stats))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- CI95 intervals are session-bootstrap intervals over the current cohort, not population guarantees.",
            "- Leave-one-session-out ranges expose whether a mean collapses when one session is removed.",
            "- The significant-session regional estimate is explanatory and should be tied to the temporal permutation result.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary_row(name: str, stats: dict[str, Any]) -> str:
    return "| {name} | {n} | {mean} | {low} | {high} | {positive} | {loo_min} | {loo_max} |".format(
        name=name,
        n=stats["n_sessions"],
        mean=_fmt(stats["mean"]),
        low=_fmt(stats["ci95_low"]),
        high=_fmt(stats["ci95_high"]),
        positive=_fmt(stats["positive_fraction"]),
        loo_min=_fmt(stats["leave_one_out_min_mean"]),
        loo_max=_fmt(stats["leave_one_out_max_mean"]),
    )


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
    parser.add_argument("--region", default="visual_cortex")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--bootstrap-iterations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--permutation-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation_500.csv")
    parser.add_argument("--regional-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--regional-significant-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.md")
    args = parser.parse_args()

    permutation_rows = read_csv_rows(args.permutation_csv)
    regional_rows = read_csv_rows(args.regional_csv)
    regional_sig_rows = read_csv_rows(args.regional_significant_csv)
    significant = significant_sessions(permutation_rows, args.alpha)

    all_temporal = permutation_gain_by_session(permutation_rows)
    sig_temporal = {
        session_id: value
        for session_id, value in all_temporal.items()
        if session_id in significant
    }
    all_drop = region_drop_by_session(regional_rows, args.region)
    sig_drop = region_drop_by_session(regional_sig_rows, args.region)

    payload = {
        "target_name": args.target_name,
        "window_name": args.window_name,
        "region": args.region,
        "alpha": args.alpha,
        "bootstrap_iterations": args.bootstrap_iterations,
        "seed": args.seed,
        "significant_session_ids": sorted(significant),
        "temporal_gain": {
            "all_sessions": summarize_values(all_temporal, args.bootstrap_iterations, args.seed),
            "significant_sessions": summarize_values(sig_temporal, args.bootstrap_iterations, args.seed + 1),
        },
        "regional_drop": {
            "all_sessions": summarize_values(all_drop, args.bootstrap_iterations, args.seed + 2),
            "significant_sessions": summarize_values(sig_drop, args.bootstrap_iterations, args.seed + 3),
        },
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"uncertainty_json={args.out_json}")
    print(f"uncertainty_md={args.out_md}")
    print(f"temporal_all_mean={payload['temporal_gain']['all_sessions']['mean']:.3f}")
    print(f"temporal_all_ci95=({payload['temporal_gain']['all_sessions']['ci95_low']:.3f}, {payload['temporal_gain']['all_sessions']['ci95_high']:.3f})")
    print(f"regional_significant_mean={payload['regional_drop']['significant_sessions']['mean']:.3f}")
    print(f"regional_significant_ci95=({payload['regional_drop']['significant_sessions']['ci95_low']:.3f}, {payload['regional_drop']['significant_sessions']['ci95_high']:.3f})")


if __name__ == "__main__":
    main()
