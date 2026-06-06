"""Test direct state/anatomy covariates against session temporal gains.

The analysis is exploratory and session-level. It uses sidecar artifacts
exported directly from local NWB files and applies label-permutation tests plus
Benjamini-Hochberg correction across the prespecified compact feature set.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def finite_values(values: list[Any]) -> list[float]:
    """Return finite floats from possibly missing values."""
    output = []
    for value in values:
        try:
            converted = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(converted):
            output.append(converted)
    return output


def sidecar_features(payload: dict[str, Any]) -> dict[str, float]:
    """Extract a compact prespecified session feature set."""
    trials = payload["trial_state"]
    features = {}
    for name in (
        "running_speed_0_250",
        "pupil_area_0_250",
        "running_speed_250_750",
        "pupil_area_250_750",
    ):
        values = finite_values([row.get(name) for row in trials])
        features[f"mean_{name}"] = mean(values) if values else math.nan
        features[f"coverage_{name}"] = len(values) / len(trials) if trials else 0.0
    quality = payload["unit_quality"]
    features["good_unit_fraction"] = float(quality.get("good_unit_fraction") or 0.0)
    features["mean_unit_snr"] = float(quality["numeric"]["snr"].get("mean") or 0.0)
    features["mean_presence_ratio"] = float(quality["numeric"]["presence_ratio"].get("mean") or 0.0)
    anatomy = payload["channel_anatomy"]
    features["valid_channel_fraction"] = float(anatomy.get("valid_data_fraction") or 0.0)
    dv = anatomy["coordinates"]["dorsal_ventral_ccf_coordinate"]
    features["dorsal_ventral_span"] = (
        float(dv["max"]) - float(dv["min"])
        if dv.get("max") is not None and dv.get("min") is not None
        else math.nan
    )
    return features


def ranks(values: list[float]) -> list[float]:
    """Return average ranks with deterministic tie handling."""
    order = sorted(range(len(values)), key=values.__getitem__)
    output = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and values[order[end]] == values[order[index]]:
            end += 1
        average_rank = (index + end - 1) / 2
        for position in range(index, end):
            output[order[position]] = average_rank
        index = end
    return output


def correlation(left: list[float], right: list[float]) -> float:
    """Return Pearson correlation."""
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    denominator = math.sqrt(
        sum((x - left_mean) ** 2 for x in left) * sum((y - right_mean) ** 2 for y in right)
    )
    return numerator / denominator if denominator else 0.0


def spearman_permutation(
    feature: list[float],
    gains: list[float],
    iterations: int,
    seed: int,
) -> tuple[float, float]:
    """Return Spearman correlation and a two-sided permutation p-value."""
    feature_ranks = ranks(feature)
    gain_ranks = ranks(gains)
    observed = correlation(feature_ranks, gain_ranks)
    rng = random.Random(seed)
    exceed = 0
    for _ in range(iterations):
        shuffled = list(gain_ranks)
        rng.shuffle(shuffled)
        exceed += abs(correlation(feature_ranks, shuffled)) >= abs(observed)
    return observed, (exceed + 1) / (iterations + 1)


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Return Benjamini-Hochberg adjusted p-values."""
    ranked = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [1.0] * len(p_values)
    running = 1.0
    for reverse_rank, (index, p_value) in enumerate(reversed(ranked), start=1):
        rank = len(p_values) - reverse_rank + 1
        running = min(running, p_value * len(p_values) / rank)
        adjusted[index] = min(1.0, running)
    return adjusted


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write direct-state/anatomy explanation report."""
    lines = [
        "# Allen direct state and fine-coverage explanation analysis",
        "",
        f"- Sessions with sidecars and usable gain: {payload['n_sessions']}",
        f"- Permutations per feature: {payload['n_permutations']}",
        f"- Decision: `{payload['decision']}`",
        "",
        "| feature | sessions | Spearman rho | permutation p | BH q |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['feature']} | {row['n_sessions']} | {row['spearman_rho']:.3f} | "
            f"{row['p_value']:.4f} | {row['q_value_bh']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Associations are exploratory session-level explanations, not causal effects.",
            "- BH correction applies across the prespecified compact feature set.",
            "- Pupil coverage and quality metrics may themselves reflect recording quality.",
            "- Absence of a significant association does not prove that state or anatomy is irrelevant.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-permutations", type=int, default=20000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--gain-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation_500.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_direct_state_anatomy.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_direct_state_anatomy.md")
    args = parser.parse_args()

    with args.gain_csv.open("r", encoding="utf-8", newline="") as handle:
        gain_by_session = {str(row["session_id"]): float(row["observed_gain"]) for row in csv.DictReader(handle)}
    session_features = []
    for path in sorted(args.datasets_root.glob("*/state_anatomy.json")):
        if path.parent.name not in gain_by_session:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        session_features.append(
            {
                "session_id": path.parent.name,
                "gain": gain_by_session[path.parent.name],
                **sidecar_features(payload),
            }
        )

    feature_names = sorted(
        key for key in session_features[0] if key not in {"session_id", "gain"}
    )
    rows = []
    for index, feature_name in enumerate(feature_names):
        valid = [
            row for row in session_features
            if math.isfinite(float(row[feature_name]))
        ]
        rho, p_value = spearman_permutation(
            [float(row[feature_name]) for row in valid],
            [float(row["gain"]) for row in valid],
            args.n_permutations,
            701 + index,
        )
        rows.append(
            {
                "feature": feature_name,
                "n_sessions": len(valid),
                "spearman_rho": rho,
                "p_value": p_value,
            }
        )
    q_values = benjamini_hochberg([float(row["p_value"]) for row in rows])
    for row, q_value in zip(rows, q_values, strict=True):
        row["q_value_bh"] = q_value
    supported = [row["feature"] for row in rows if float(row["q_value_bh"]) < args.alpha]
    payload = {
        "n_sessions": len(session_features),
        "n_permutations": args.n_permutations,
        "alpha": args.alpha,
        "supported_features": supported,
        "decision": (
            "direct_state_or_coverage_candidate_supported"
            if supported
            else "no_direct_state_or_coverage_explanation_supported"
        ),
        "rows": rows,
        "session_features": session_features,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"direct_state_anatomy_json={args.out_json}")
    print(f"decision={payload['decision']}")


if __name__ == "__main__":
    main()
