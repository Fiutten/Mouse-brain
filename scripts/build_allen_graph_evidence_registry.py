"""Build an evidence registry over the Allen functional graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.functional_graph import FunctionalEdge, FunctionalGraphReport, FunctionalNode, build_graph_evidence_registry


ROOT = Path(__file__).resolve().parents[1]


def load_graph(path: Path) -> FunctionalGraphReport:
    data = json.loads(path.read_text(encoding="utf-8"))
    return FunctionalGraphReport(
        target_name=data["target_name"],
        window_name=data["window_name"],
        nodes=[FunctionalNode(**node) for node in data["nodes"]],
        edges=[FunctionalEdge(**edge) for edge in data["edges"]],
        interpretation=list(data["interpretation"]),
    )


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Allen graph evidence registry: {payload['target_name']} / {payload['window_name']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Edge Records",
            "",
            "| source | relation | target | weight | state | strength | fragility | rationale |",
            "| --- | --- | --- | ---: | --- | ---: | ---: | --- |",
        ]
    )
    for record in payload["records"]:
        lines.append(
            "| {source} | {relation} | {target} | {weight:.3f} | {state} | {strength:.3f} | {fragility:.3f} | {rationale} |".format(
                **record
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Controlled edges are eligible for follow-up, not final causal claims.",
            "- Exploratory edges should guide data collection and controls.",
        ]
    )
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_functional_graph.json")
    parser.add_argument("--stability-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.json")
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--controls-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_controls.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_graph_evidence_registry.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_graph_evidence_registry.md")
    args = parser.parse_args()

    stability = json.loads(args.stability_json.read_text(encoding="utf-8"))
    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    controls = json.loads(args.controls_json.read_text(encoding="utf-8"))
    registry = build_graph_evidence_registry(
        load_graph(args.graph_json),
        stability_by_session=stability["rows"],
        temporal_ci95_low=float(uncertainty["temporal_gain"]["all_sessions"]["ci95_low"]),
        control_decision=controls["window_control"]["decision"],
    )
    payload = registry.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"graph_registry_json={args.out_json}")
    print(f"graph_registry_md={args.out_md}")
    print(f"controlled_edges={payload['summary']['controlled']}")


if __name__ == "__main__":
    main()
