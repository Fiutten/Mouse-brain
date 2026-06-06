"""Analyze whether recording coverage plausibly explains fragile sessions."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def region_presence(rows: list[dict[str, str]], fragile_ids: set[str], n_permutations: int, seed: int) -> list[dict[str, Any]]:
    """Compare coarse region-presence fractions between fragile and other sessions."""
    regions = sorted({region for row in rows for region in str(row.get("regions", "")).split(",") if region})
    output = []
    labels = [str(row["session_id"]) in fragile_ids for row in rows]
    rng = random.Random(seed)
    for region in regions:
        values = [region in str(row.get("regions", "")).split(",") for row in rows]
        fragile_values = [value for value, fragile in zip(values, labels, strict=True) if fragile]
        other_values = [value for value, fragile in zip(values, labels, strict=True) if not fragile]
        difference = mean(fragile_values) - mean(other_values)
        extreme = 0
        n_fragile = len(fragile_values)
        for _ in range(n_permutations):
            shuffled = list(values)
            rng.shuffle(shuffled)
            null = mean(shuffled[:n_fragile]) - mean(shuffled[n_fragile:])
            extreme += abs(null) >= abs(difference)
        output.append(
            {
                "region": region,
                "fragile_presence_fraction": mean(fragile_values),
                "other_presence_fraction": mean(other_values),
                "difference": difference,
                "permutation_p_value": (extreme + 1) / (n_permutations + 1),
            }
        )
    return output


def missing_metadata(rows: list[dict[str, str]], fragile_ids: set[str]) -> dict[str, Any]:
    """Summarize recording metadata completeness by group."""
    fields = ["unit_count", "probe_count", "session_type", "image_set", "experience_level"]
    result = {}
    for field in fields:
        result[field] = {
            "fragile_missing": sum(row.get(field) in (None, "") for row in rows if row["session_id"] in fragile_ids),
            "other_missing": sum(row.get(field) in (None, "") for row in rows if row["session_id"] not in fragile_ids),
        }
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen recording-coverage analysis",
        "",
        "## Coarse Region Presence",
        "",
        "| region | fragile presence | other presence | difference | permutation p |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["region_presence"]:
        lines.append(
            f"| {row['region']} | {row['fragile_presence_fraction']:.3f} | "
            f"{row['other_presence_fraction']:.3f} | {row['difference']:.3f} | "
            f"{row['permutation_p_value']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Coarse region presence does not measure probe placement, depth, unit quality or cell-type coverage.",
            "- Missing probe/unit metadata is itself a technical confound and should be recovered before attributing fragility to coverage.",
            "- A non-significant coarse-region comparison cannot exclude fine anatomical coverage effects.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-permutations", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=109)
    parser.add_argument("--relations-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_relations.csv")
    parser.add_argument("--stability-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.csv")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_recording_coverage.json")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_recording_coverage.csv")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_recording_coverage.md")
    args = parser.parse_args()

    relations = read_csv(args.relations_csv)
    usable_ids = {
        str(row["session_id"])
        for row in read_csv(args.stability_csv)
    }
    fragile_ids = {
        str(row["session_id"])
        for row in read_csv(args.stability_csv)
        if str(row["status"]) == "fragile"
    }
    usable_relations = [row for row in relations if str(row["session_id"]) in usable_ids]
    regions = region_presence(usable_relations, fragile_ids, args.n_permutations, args.seed)
    payload = {
        "n_sessions": len(usable_relations),
        "n_fragile": len(fragile_ids),
        "region_presence": regions,
        "missing_metadata": missing_metadata(usable_relations, fragile_ids),
        "limitations": [
            "No fine probe-placement coordinates are present in normalized session artifacts.",
            "Coarse region presence cannot measure within-region coverage or unit quality.",
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out_csv, regions)
    write_markdown(args.out_md, payload)
    print(f"recording_coverage_json={args.out_json}")
    print(f"recording_coverage_md={args.out_md}")


if __name__ == "__main__":
    main()
