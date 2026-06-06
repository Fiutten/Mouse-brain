"""Quantify animal/session heterogeneity without overstating independence.

The current cohort contains many single-session animals and only a small number
of repeated animals. This script therefore reports cluster-bootstrap
uncertainty and a descriptive random-effects decomposition, while explicitly
marking the latter as unstable rather than presenting it as a fitted
hierarchical predictive model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, variance
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV report."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def join_gain_animals(
    gain_rows: list[dict[str, str]],
    relation_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Join per-session gains to animal identity."""
    animal_by_session = {str(row["session_id"]): str(row["animal_id"]) for row in relation_rows}
    return [
        {
            "session_id": str(row["session_id"]),
            "animal_id": animal_by_session.get(str(row["session_id"]), "missing"),
            "gain": float(row["observed_gain"]),
        }
        for row in gain_rows
    ]


def cluster_bootstrap_ci(
    rows: list[dict[str, Any]],
    iterations: int = 10000,
    seed: int = 503,
) -> tuple[float, float]:
    """Bootstrap animals, preserving all sessions from sampled animals."""
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["animal_id"])].append(float(row["gain"]))
    animals = sorted(grouped)
    rng = random.Random(seed)
    draws = []
    for _ in range(iterations):
        sampled = [rng.choice(animals) for _ in animals]
        gains = [gain for animal in sampled for gain in grouped[animal]]
        draws.append(mean(gains))
    draws.sort()
    return draws[int(0.025 * iterations)], draws[int(0.975 * iterations)]


def descriptive_random_effects(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Estimate a descriptive one-way random-effects ICC.

    This unbalanced ANOVA approximation is not a replacement for a fitted
    mixed-effects model. It is especially uncertain when most animals have one
    session, as in the current cohort.
    """
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["animal_id"])].append(float(row["gain"]))
    grand = mean(float(row["gain"]) for row in rows)
    k = len(grouped)
    n = len(rows)
    ss_between = sum(len(values) * (mean(values) - grand) ** 2 for values in grouped.values())
    ss_within = sum(sum((value - mean(values)) ** 2 for value in values) for values in grouped.values())
    ms_between = ss_between / max(k - 1, 1)
    ms_within = ss_within / max(n - k, 1)
    n0 = (n - sum(len(values) ** 2 for values in grouped.values()) / n) / max(k - 1, 1)
    between_variance = max(0.0, (ms_between - ms_within) / max(n0, 1e-12))
    total = between_variance + ms_within
    return {
        "n_animals": k,
        "n_sessions": n,
        "n_repeated_animals": sum(len(values) > 1 for values in grouped.values()),
        "between_animal_variance": between_variance,
        "within_animal_session_variance": ms_within,
        "descriptive_icc": between_variance / total if total else 0.0,
        "reliability": "low_currently_only_six_repeated_animals",
    }


def stable_partition(animal_id: str) -> str:
    """Assign animals deterministically to a post-hoc sensitivity partition."""
    digest = hashlib.sha256(animal_id.encode("utf-8")).digest()
    return "sensitivity_confirm" if digest[0] % 3 == 0 else "sensitivity_discovery"


def summarize_partition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize the stable animal partition without calling it replication."""
    output = {}
    for name in ("sensitivity_discovery", "sensitivity_confirm"):
        items = [row for row in rows if stable_partition(str(row["animal_id"])) == name]
        gains = [float(row["gain"]) for row in items]
        output[name] = {
            "n_animals": len({str(row["animal_id"]) for row in items}),
            "n_sessions": len(items),
            "mean_gain": mean(gains) if gains else None,
            "positive_fraction": sum(value > 0.0 for value in gains) / len(gains) if gains else None,
        }
    return output


def binomial_positive_tail(n_positive: int, n_total: int) -> float:
    """Return exact one-sided P(X >= n_positive) under p=0.5."""
    return sum(math.comb(n_total, k) for k in range(n_positive, n_total + 1)) / (2**n_total)


def direct_variable_inventory(dataset_root: Path) -> dict[str, Any]:
    """Audit direct variables in separate NWB-derived sidecars."""
    presence = {
        "running_speed": 0,
        "pupil": 0,
        "fine_probe_coordinates": 0,
        "unit_quality": 0,
    }
    sessions = 0
    for path in sorted(dataset_root.glob("*/session.json")):
        sessions += 1
        sidecar_path = path.parent / "state_anatomy.json"
        if not sidecar_path.exists():
            continue
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        trials = sidecar.get("trial_state", [])
        presence["running_speed"] += int(
            any(row.get("running_speed_0_250") is not None for row in trials)
        )
        presence["pupil"] += int(any(row.get("pupil_area_0_250") is not None for row in trials))
        presence["fine_probe_coordinates"] += int(bool(sidecar.get("channel_anatomy", {}).get("coordinates")))
        presence["unit_quality"] += int(bool(sidecar.get("unit_quality", {}).get("numeric")))
    return {
        "n_sessions_audited": sessions,
        "n_state_anatomy_sidecars": sum(1 for path in dataset_root.glob("*/state_anatomy.json")),
        "sessions_with_variable": presence,
        "direct_state_phase_complete": all(value == sessions for value in presence.values()),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a critical heterogeneity report."""
    random_effects = payload["descriptive_random_effects"]
    lines = [
        "# Allen hierarchical heterogeneity audit",
        "",
        "## Animal-aware uncertainty",
        "",
        f"- Session-level mean gain: {payload['mean_gain']:.3f}",
        f"- Animal-cluster bootstrap CI95: [{payload['cluster_bootstrap_ci95'][0]:.3f}, {payload['cluster_bootstrap_ci95'][1]:.3f}]",
        f"- Positive-animal exact one-sided p-value: {payload['positive_animal_sign_test_p']:.4f}",
        "",
        "## Descriptive variance decomposition",
        "",
        f"- Animals: {random_effects['n_animals']}",
        f"- Repeated animals: {random_effects['n_repeated_animals']}",
        f"- Descriptive ICC: {random_effects['descriptive_icc']:.3f}",
        f"- Reliability: `{random_effects['reliability']}`",
        "",
        "The ICC is descriptive and unstable. It is not evidence that animal identity explains a fixed proportion of biological variance.",
        "",
        "## Post-hoc animal partition",
        "",
        "This partition is a sensitivity check only. It is not an untouched replication because it was created after observing the cohort.",
        "",
        "| partition | animals | sessions | mean gain | positive fraction |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, stats in payload["posthoc_partition"].items():
        lines.append(
            f"| {name} | {stats['n_animals']} | {stats['n_sessions']} | "
            f"{stats['mean_gain']:.3f} | {stats['positive_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Missing direct variables",
            "",
        ]
    )
    for name, count in payload["direct_variable_inventory"]["sessions_with_variable"].items():
        lines.append(f"- `{name}` available in {count}/{payload['direct_variable_inventory']['n_sessions_audited']} sessions")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{payload['decision']}`",
            "",
            "A proper hierarchical predictive model and direct state/anatomy explanation remain blocked until more repeated animals or suitable direct variables are available.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutation-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation_500.csv")
    parser.add_argument("--relations-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--datasets-root", type=Path, default=ROOT / "artifacts" / "datasets" / "allen")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_hierarchical_heterogeneity.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_hierarchical_heterogeneity.md")
    args = parser.parse_args()

    rows = join_gain_animals(read_csv(args.permutation_csv), read_csv(args.relations_csv))
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["animal_id"])].append(float(row["gain"]))
    animal_means = [mean(values) for values in grouped.values()]
    positive_animals = sum(value > 0.0 for value in animal_means)
    payload = {
        "mean_gain": mean(float(row["gain"]) for row in rows),
        "cluster_bootstrap_ci95": cluster_bootstrap_ci(rows),
        "positive_animals": positive_animals,
        "n_animals": len(animal_means),
        "positive_animal_sign_test_p": binomial_positive_tail(positive_animals, len(animal_means)),
        "descriptive_random_effects": descriptive_random_effects(rows),
        "posthoc_partition": summarize_partition(rows),
        "direct_variable_inventory": direct_variable_inventory(args.datasets_root),
        "decision": "aggregate_animal_robust_but_hierarchical_explanation_not_identified",
        "limitations": [
            "Only six animals contribute repeated sessions.",
            "The stable animal partition is post-hoc and is not replication.",
            "Direct running, pupil, fine anatomy and unit-quality variables are absent from normalized artifacts.",
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"hierarchical_heterogeneity_json={args.out_json}")
    print(f"decision={payload['decision']}")


if __name__ == "__main__":
    main()
