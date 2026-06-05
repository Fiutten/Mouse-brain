"""Run the deterministic scientific-agent audit over current Allen layers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from neurotwin_mvp.scientific_agent import audit_current_evidence


ROOT = Path(__file__).resolve().parents[1]


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write an auditable agent report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Allen scientific-agent audit",
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
                "| {severity} | {claim} | {evidence} | {recommendation} |".format(
                    severity=finding["severity"],
                    claim=finding["claim"],
                    evidence=finding["evidence"],
                    recommendation=finding["recommendation"],
                )
            )
    else:
        lines.append("| info | No blocking findings under current deterministic rules. |  |  |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in payload["next_actions"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uncertainty-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_uncertainty.json")
    parser.add_argument("--controls-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_controls.json")
    parser.add_argument("--generative-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_pre_response_generative_surrogate.json")
    parser.add_argument("--out-json", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_scientific_agent.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "artifacts" / "reports" / "allen_targets" / "go_response_scientific_agent.md")
    args = parser.parse_args()

    uncertainty = json.loads(args.uncertainty_json.read_text(encoding="utf-8"))
    controls = json.loads(args.controls_json.read_text(encoding="utf-8"))
    generative = json.loads(args.generative_json.read_text(encoding="utf-8"))
    temporal = uncertainty["temporal_gain"]["all_sessions"]
    regional = uncertainty["regional_drop"]["all_sessions"]
    report = audit_current_evidence(
        temporal_ci95=[float(temporal["ci95_low"]), float(temporal["ci95_high"])],
        temporal_positive_fraction=float(temporal["positive_fraction"]),
        regional_ci95=[float(regional["ci95_low"]), float(regional["ci95_high"])],
        control_decision=controls["window_control"]["decision"],
        generative_warnings=list(generative.get("warnings", [])),
    )
    payload = report.to_dict()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(args.out_md, payload)
    print(f"scientific_agent_json={args.out_json}")
    print(f"scientific_agent_md={args.out_md}")
    print(f"decision={payload['decision']}")
    print(f"n_findings={len(payload['findings'])}")


if __name__ == "__main__":
    main()
