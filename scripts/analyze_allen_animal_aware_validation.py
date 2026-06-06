"""Validate Allen temporal evidence while respecting animal clustering."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def join_by_animal(
    permutation_rows: list[dict[str, str]],
    relation_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Join temporal outcomes to animal ids."""
    animal_by_session = {str(row["session_id"]): str(row["animal_id"]) for row in relation_rows}
    return [
        {
            "session_id": str(row["session_id"]),
            "animal_id": animal_by_session.get(str(row["session_id"]), "missing"),
            "observed_gain": float(row["observed_gain"]),
            "p_value": float(row["p_value"]),
        }
        for row in permutation_rows
    ]


def summarize_animals(rows: list[dict[str, Any]], alpha: float) -> list[dict[str, Any]]:
    """Aggregate sessions within animal before cohort interpretation."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["animal_id"])].append(row)
    output = []
    for animal_id, items in sorted(grouped.items()):
        gains = [float(item["observed_gain"]) for item in items]
        output.append(
            {
                "animal_id": animal_id,
                "n_sessions": len(items),
                "mean_gain": mean(gains),
                "positive_fraction": sum(value > 0.0 for value in gains) / len(gains),
                "significant_fraction": sum(float(item["p_value"]) < alpha for item in items) / len(items),
                "session_ids": "; ".join(str(item["session_id"]) for item in items),
            }
        )
    return output


def leave_one_animal_out(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Measure aggregate temporal gain after excluding each animal."""
    animals = sorted({str(row["animal_id"]) for row in rows})
    output = []
    for animal_id in animals:
        remaining = [float(row["observed_gain"]) for row in rows if str(row["animal_id"]) != animal_id]
        output.append(
            {
                "left_out_animal_id": animal_id,
                "n_remaining_sessions": len(remaining),
                "mean_gain": mean(remaining),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    lines = [
        "# Allen animal-aware validation",
        "",
        "## Summary",
        "",
        f"- Sessions: {summary['n_sessions']}",
        f"- Animals: {summary['n_animals']}",
        f"- Multi-session animals: {summary['n_multi_session_animals']}",
        f"- Mean animal-level gain: {summary['mean_animal_gain']:.3f}",
        f"- Positive animal fraction: {summary['positive_animal_fraction']:.3f}",
        f"- LOO-animal minimum session-level mean gain: {summary['loo_min_mean_gain']:.3f}",
        f"- LOO-animal maximum session-level mean gain: {summary['loo_max_mean_gain']:.3f}",
        "",
        "## Interpretation",
        "",
        "- Positive leave-one-animal-out means show that no single animal creates the aggregate temporal effect.",
        "- Animal-level aggregation reduces pseudoreplication but does not replace a hierarchical predictive model.",
        "- Animals with multiple discordant sessions support session-state heterogeneity.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--permutation-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_permutation_500.csv")
    parser.add_argument("--relations-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_animal_aware_validation.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_animal_aware_validation.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_animal_aware_validation.md")
    args = parser.parse_args()

    rows = join_by_animal(read_csv(args.permutation_csv), read_csv(args.relations_csv))
    animals = summarize_animals(rows, args.alpha)
    loo = leave_one_animal_out(rows)
    animal_gains = [float(row["mean_gain"]) for row in animals]
    summary = {
        "n_sessions": len(rows),
        "n_animals": len(animals),
        "n_multi_session_animals": sum(int(row["n_sessions"]) > 1 for row in animals),
        "mean_animal_gain": mean(animal_gains),
        "positive_animal_fraction": sum(value > 0.0 for value in animal_gains) / len(animal_gains),
        "loo_min_mean_gain": min(float(row["mean_gain"]) for row in loo),
        "loo_max_mean_gain": max(float(row["mean_gain"]) for row in loo),
    }
    payload = {"summary": summary, "animals": animals, "leave_one_animal_out": loo}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, animals)
    write_markdown(args.out_md, payload)
    print(f"animal_aware_json={args.out_json}")
    print(f"animal_aware_md={args.out_md}")
    print(f"n_animals={summary['n_animals']}")
    print(f"loo_min_mean_gain={summary['loo_min_mean_gain']:.3f}")


if __name__ == "__main__":
    main()
