"""Summarize Sensorium 2022 static results as a cross-dataset comparator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any


def _median(values: list[float]) -> float | None:
    return median(values) if values else None


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 6)


def build_static_comparison(input_summary: Path) -> dict[str, Any]:
    """Build a compact comparison from existing Sensorium 2022 static artifacts."""

    payload = json.loads(input_summary.read_text())
    rows = payload["rows"]
    validation = [row for row in rows if row["eval_tier"] == "validation"]
    repeated_test = [
        row
        for row in rows
        if row["eval_tier"] == "test" and float(row.get("reliability", 0.0)) > 0.0
    ]

    def summarize(selected: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "n": len(selected),
            "median_reliability": _median([float(row["reliability"]) for row in selected]),
            "median_best_predictive_correlation": _median(
                [float(row["best_predictive_correlation"]) for row in selected]
            ),
            "median_best_minus_mean": _median(
                [float(row["best_predictive_minus_mean"]) for row in selected]
            ),
            "median_best_minus_scrambled": _median(
                [float(row["best_predictive_minus_scrambled"]) for row in selected]
            ),
            "mis_passed_count": sum(bool(row["mis_passed"]) for row in selected),
            "median_mis_score": _median([float(row["mis_score"]) for row in selected]),
        }

    return {
        "comparison": "sensorium2022_static_cross_dataset_comparator",
        "input_summary": str(input_summary),
        "validation_all_mice": summarize(validation),
        "pretraining_test_repeated": summarize(repeated_test),
        "rows": rows,
        "interpretation": (
            "Sensorium 2022 static is the current positive reliability case: "
            "repeated-test mice have estimable response reliability and positive "
            "stimulus-specific prediction, but MIS still rejects mechanistic "
            "identifiability because structural/causal constraints are absent."
        ),
    }


def write_outputs(payload: dict[str, Any], output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2))
    lines = [
        "# Sensorium 2022 Static Comparator",
        "",
        payload["interpretation"],
        "",
        "| Cohorte | n | Reliability | Best corr | Best - mean | Best - scrambled | MIS passed | MIS score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("validation_all_mice", "pretraining_test_repeated"):
        row = payload[label]
        lines.append(
            "| "
            f"{label} | `{row['n']}` | `{_round(row['median_reliability'])}` | "
            f"`{_round(row['median_best_predictive_correlation'])}` | "
            f"`{_round(row['median_best_minus_mean'])}` | "
            f"`{_round(row['median_best_minus_scrambled'])}` | "
            f"`{row['mis_passed_count']}` | `{_round(row['median_mis_score'])}` |"
        )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-summary",
        type=Path,
        default=Path("results/sensorium_real/summary_sensorium2022_static_mis.json"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/sensorium_static_model_comparator/summary.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/sensorium_static_model_comparator/summary.md"),
    )
    args = parser.parse_args()
    payload = build_static_comparison(args.input_summary)
    write_outputs(payload, args.output_json, args.output_md)
    print(json.dumps({"output_json": str(args.output_json)}))


if __name__ == "__main__":
    main()
