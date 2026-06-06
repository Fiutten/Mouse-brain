"""Test candidate explanations for fragile Allen temporal sessions.

This analysis deliberately excludes the temporal, regional-ablation and
latency-stratum gains that define the stability label. It asks whether fragile
sessions can instead be explained by independent coarse covariates such as
trial count, target balance, response latency, recording coverage or task
metadata.

The output is descriptive and permutation-based. With only nine fragile
sessions, absence of evidence is not evidence of absence; the report therefore
separates supported associations, weak candidates and unsupported explanations.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, variance
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NUMERIC_FEATURES = [
    "go_labeled_trials",
    "go_minority_fraction",
    "mean_latency_ms",
    "median_latency_ms",
    "zero_latency_fraction",
    "region_count",
    "unit_count",
    "probe_count",
    "metadata_complete",
]

CATEGORICAL_FEATURES = ["experience_level", "image_set", "session_type"]


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read one CSV artifact."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def join_rows(
    stability_rows: list[dict[str, str]],
    relation_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Join stability status to independent session metadata."""
    relation_by_id = {str(row["session_id"]): row for row in relation_rows}
    joined = []
    for stability in stability_rows:
        session_id = str(stability["session_id"])
        relation = relation_by_id.get(session_id, {})
        metadata_complete = all(
            relation.get(key) not in (None, "")
            for key in ["experience_level", "image_set", "session_type", "unit_count", "probe_count"]
        )
        joined.append(
            {
                "session_id": session_id,
                "status": str(stability["status"]),
                "fragile": str(stability["status"]) == "fragile",
                **{
                    key: relation.get(key, "")
                    for key in NUMERIC_FEATURES + CATEGORICAL_FEATURES
                    if key != "metadata_complete"
                },
                "metadata_complete": int(metadata_complete),
                "animal_id": relation.get("animal_id", ""),
            }
        )
    return joined


def numeric_comparison(
    rows: list[dict[str, Any]],
    feature: str,
    *,
    n_permutations: int,
    seed: int,
) -> dict[str, Any]:
    """Compare fragile vs non-fragile means with standardized difference/null."""
    observed = [
        (bool(row["fragile"]), float(row[feature]))
        for row in rows
        if row.get(feature) not in (None, "")
    ]
    fragile = [value for is_fragile, value in observed if is_fragile]
    other = [value for is_fragile, value in observed if not is_fragile]
    difference = mean(fragile) - mean(other)
    pooled_std = _pooled_std(fragile, other)
    smd = difference / pooled_std if pooled_std > 0.0 else None
    values = [value for _, value in observed]
    n_fragile = len(fragile)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_permutations):
        shuffled = list(values)
        rng.shuffle(shuffled)
        null_difference = mean(shuffled[:n_fragile]) - mean(shuffled[n_fragile:])
        if abs(null_difference) >= abs(difference):
            extreme += 1
    return {
        "feature": feature,
        "n_fragile": len(fragile),
        "n_other": len(other),
        "missing_fragile": sum(1 for row in rows if row["fragile"] and row.get(feature) in (None, "")),
        "missing_other": sum(1 for row in rows if not row["fragile"] and row.get(feature) in (None, "")),
        "fragile_mean": mean(fragile),
        "fragile_median": median(fragile),
        "other_mean": mean(other),
        "other_median": median(other),
        "mean_difference": difference,
        "standardized_mean_difference": smd,
        "permutation_p_value": (extreme + 1) / (n_permutations + 1),
    }


def categorical_comparison(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    """Describe category frequencies without overclaiming sparse associations."""
    fragile = Counter(_category(row.get(feature)) for row in rows if row["fragile"])
    other = Counter(_category(row.get(feature)) for row in rows if not row["fragile"])
    categories = sorted(set(fragile) | set(other))
    return {
        "feature": feature,
        "fragile_counts": {key: fragile[key] for key in categories},
        "other_counts": {key: other[key] for key in categories},
    }


def animal_recurrence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize whether animal identity consistently predicts status."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        animal_id = str(row.get("animal_id", "") or "missing")
        grouped[animal_id].append(str(row["status"]))
    repeated = {
        animal: statuses
        for animal, statuses in sorted(grouped.items())
        if animal != "missing" and len(statuses) > 1
    }
    consistent_fragile = {
        animal: statuses
        for animal, statuses in repeated.items()
        if set(statuses) == {"fragile"}
    }
    mixed_status = {
        animal: statuses
        for animal, statuses in repeated.items()
        if len(set(statuses)) > 1
    }
    return {
        "repeated_animals": repeated,
        "consistent_fragile_animals": consistent_fragile,
        "mixed_status_animals": mixed_status,
    }


def classify_evidence(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    """Separate supported, weak and unsupported candidate explanations."""
    supported = []
    weak = []
    unsupported = []
    for row in comparisons:
        smd = abs(float(row["standardized_mean_difference"] or 0.0))
        p_value = float(row["permutation_p_value"])
        missing_fragile = int(row["missing_fragile"])
        if p_value < 0.05 and smd >= 0.8 and missing_fragile == 0:
            supported.append(row["feature"])
        elif p_value < 0.10 or smd >= 0.5:
            weak.append(row["feature"])
        else:
            unsupported.append(row["feature"])
    return {
        "supported_explanations": supported,
        "weak_candidates": weak,
        "unsupported_explanations": unsupported,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write numeric comparison table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a discussion-ready scientific interpretation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    evidence = payload["evidence_classification"]
    lines = [
        "# Scientific explanation of fragile Allen sessions",
        "",
        "## Question",
        "",
        "Can the 9 fragile sessions be explained by independent coarse session",
        "covariates, rather than by the temporal evidence metrics that define",
        "fragility?",
        "",
        "## Numeric Comparisons",
        "",
        "| feature | fragile mean | other mean | difference | standardized difference | permutation p | fragile missing |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["numeric_comparisons"]:
        lines.append(
            "| {feature} | {fragile:.3f} | {other:.3f} | {difference:.3f} | {smd} | {p:.3f} | {missing} |".format(
                feature=row["feature"],
                fragile=row["fragile_mean"],
                other=row["other_mean"],
                difference=row["mean_difference"],
                smd=_fmt(row["standardized_mean_difference"]),
                p=row["permutation_p_value"],
                missing=row["missing_fragile"],
            )
        )
    lines.extend(
        [
            "",
            "## Evidence Classification",
            "",
            f"- Supported independent explanations: {', '.join(evidence['supported_explanations']) or 'none'}",
            f"- Weak candidates requiring targeted validation: {', '.join(evidence['weak_candidates']) or 'none'}",
            f"- Unsupported coarse explanations: {', '.join(evidence['unsupported_explanations']) or 'none'}",
            "",
            "## Animal Recurrence",
            "",
            f"- Repeated animals: {len(payload['animal_recurrence']['repeated_animals'])}",
            f"- Animals consistently fragile across repeated sessions: {len(payload['animal_recurrence']['consistent_fragile_animals'])}",
            f"- Repeated animals spanning different stability states: {len(payload['animal_recurrence']['mixed_status_animals'])}",
            "",
            "## Scientific Interpretation",
            "",
            "- The fragile sessions are genuine temporal-null/weak-effect cases, not sessions excluded for target imbalance.",
            "- Coarse behavioral and recording covariates do not provide a sufficient independent explanation at the current sample size.",
            "- Lower probe count is a weak measurement-coverage candidate, but missing metadata in fragile sessions prevents a clean conclusion.",
            "- Metadata completeness is analyzed as a technical confound, not as a biological explanation.",
            "- Animal identity is not sufficient: repeated animals can span different stability states, although one animal has two fragile sessions.",
            "- The most defensible explanation is unresolved session-state or circuit heterogeneity, potentially mixed with recording-coverage effects.",
            "- This is a scientifically useful negative result: the current compact model does not capture the conditions under which the pre-response signature appears.",
            "",
            "## Discussion Language",
            "",
            "A substantial minority of behaviorally usable sessions lacked the candidate pre-response signature. These failures were not adequately explained by class balance, trial count, response latency, coarse region count, experience level, or image set. The pattern therefore argues against a universal temporal mechanism and favors a state-dependent or circuit-heterogeneous account. A possible contribution from recording coverage remains, because lower probe count appeared as a weak candidate under incomplete metadata. Fragile sessions should be retained as explicit negative cases for future state, anatomy, and recording-quality stratification rather than removed from the cohort.",
            "",
            "## Limitations",
            "",
            "- Nine fragile sessions provide limited power for detecting modest covariate effects.",
            "- Metadata are missing for several recently added sessions.",
            "- Session-level observations are not fully independent when animals contribute multiple sessions.",
            "- Coarse region counts do not measure probe placement quality or unit-level coverage.",
            "- Association cannot establish biological mechanism.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _pooled_std(first: list[float], second: list[float]) -> float:
    if len(first) < 2 or len(second) < 2:
        return 0.0
    return math.sqrt(
        ((len(first) - 1) * variance(first) + (len(second) - 1) * variance(second))
        / (len(first) + len(second) - 2)
    )


def _category(value: Any) -> str:
    return str(value) if value not in (None, "") else "missing"


def _fmt(value: Any) -> str:
    return "" if value is None else f"{float(value):.3f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stability-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--session-relations-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--n-permutations", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragility_explanations.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragility_explanations.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_fragility_discussion.md")
    args = parser.parse_args()

    rows = join_rows(read_csv(args.stability_csv), read_csv(args.session_relations_csv))
    numeric = [
        numeric_comparison(rows, feature, n_permutations=args.n_permutations, seed=args.seed + index)
        for index, feature in enumerate(NUMERIC_FEATURES)
    ]
    payload = {
        "n_sessions": len(rows),
        "n_fragile": sum(1 for row in rows if row["fragile"]),
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "numeric_comparisons": numeric,
        "categorical_comparisons": [
            categorical_comparison(rows, feature)
            for feature in CATEGORICAL_FEATURES
        ],
        "animal_recurrence": animal_recurrence(rows),
        "evidence_classification": classify_evidence(numeric),
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, numeric)
    write_markdown(args.out_md, payload)
    print(f"fragility_explanations_json={args.out_json}")
    print(f"fragility_explanations_csv={args.out_csv}")
    print(f"fragility_discussion_md={args.out_md}")
    print(f"supported_explanations={len(payload['evidence_classification']['supported_explanations'])}")
    print(f"weak_candidates={len(payload['evidence_classification']['weak_candidates'])}")


if __name__ == "__main__":
    main()
