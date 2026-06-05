"""Run the deterministic advanced scientific-agent audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.scientific_agent import audit_advanced_evidence


ROOT = Path(__file__).resolve().parents[1]


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen advanced scientific-agent audit",
        "",
        f"- Decision: `{payload['decision']}`",
        "",
        "## Findings",
        "",
        "| severity | claim | evidence | recommendation |",
        "| --- | --- | --- | --- |",
    ]
    if payload["findings"]:
        for finding in payload["findings"]:
            lines.append(
                "| {severity} | {claim} | {evidence} | {recommendation} |".format(**finding)
            )
    else:
        lines.append("| info | No blocking findings under advanced rules. |  |  |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in payload["next_actions"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stability-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_stability_matrix.json")
    parser.add_argument("--graph-registry-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_graph_evidence_registry.json")
    parser.add_argument("--latent-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_latent_temporal_baseline.json")
    parser.add_argument("--generator-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_session_generator_v2.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_advanced_scientific_agent.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_advanced_scientific_agent.md")
    args = parser.parse_args()

    stability = json.loads(args.stability_json.read_text(encoding="utf-8"))
    graph_registry = json.loads(args.graph_registry_json.read_text(encoding="utf-8"))
    latent = json.loads(args.latent_json.read_text(encoding="utf-8"))
    generator = json.loads(args.generator_json.read_text(encoding="utf-8"))
    report = audit_advanced_evidence(
        stability_summary=stability["summary"],
        graph_registry_summary=graph_registry["summary"],
        latent_summary=latent["summary"],
        generator_warnings=list(generator.get("warnings", [])),
    )
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"advanced_agent_json={args.out_json}")
    print(f"advanced_agent_md={args.out_md}")
    print(f"decision={payload['decision']}")
    print(f"n_findings={len(payload['findings'])}")


if __name__ == "__main__":
    main()
