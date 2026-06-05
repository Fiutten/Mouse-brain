"""Build the Allen empirical functional graph from current evidence reports."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from neurotwin_mvp.functional_graph import build_functional_graph


ROOT = Path(__file__).resolve().parents[1]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mean_region_drops(path: Path) -> dict[str, float]:
    """Aggregate temporal regional-ablation drops across sessions."""
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in read_csv_rows(path):
        grouped[str(row["region"])].append(float(row["drop_from_full"]))
    return {region: mean(values) for region, values in grouped.items()}


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a reviewer-readable graph summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen functional graph: {payload['target_name']} / {payload['window_name']}",
        "",
        "## Edges",
        "",
        "| source | relation | target | weight | evidence |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for edge in payload["edges"]:
        lines.append(
            "| {source} | {relation} | {target} | {weight} | {evidence} |".format(
                source=edge["source"],
                relation=edge["relation"],
                target=edge["target"],
                weight=f"{float(edge['weight']):.3f}",
                evidence=edge["evidence"],
            )
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in payload["interpretation"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-name", default="go_response")
    parser.add_argument("--window-name", default="pre_response")
    parser.add_argument("--region-drop-csv", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_regional_ablation_all_sessions.csv")
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--minimum-region-drop", type=float, default=0.02)
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_functional_graph.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_functional_graph.md")
    args = parser.parse_args()

    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    temporal = uncertainty["temporal_gain"]["all_sessions"]
    report = build_functional_graph(
        target_name=args.target_name,
        window_name=args.window_name,
        temporal_gain_mean=float(temporal["mean"]),
        temporal_gain_ci95=[float(temporal["ci95_low"]), float(temporal["ci95_high"])],
        regional_drops=mean_region_drops(args.region_drop_csv),
        minimum_region_drop=args.minimum_region_drop,
    )
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"functional_graph_json={args.out_json}")
    print(f"functional_graph_md={args.out_md}")
    print(f"n_nodes={len(payload['nodes'])}")
    print(f"n_edges={len(payload['edges'])}")


if __name__ == "__main__":
    main()
