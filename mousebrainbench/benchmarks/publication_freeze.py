"""Freeze the current publication decision from tracked benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from mousebrainbench import __version__
from mousebrainbench.artifacts import code_revision


DEFAULT_OUTPUT = Path("results/publication_freeze/summary.json")
DEFAULT_MARKDOWN = Path("results/publication_freeze/summary.md")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build_freeze_payload(
    *,
    official_audit: Path = Path("results/sensorium_official_baseline_audit/summary.json"),
    sensitivity: Path = Path("results/q1_sensitivity/summary.json"),
    microns_gate: Path = Path("results/microns_pilot_gate/summary.json"),
    proposal_status: Path = Path("docs/PROPOSAL_STATUS.md"),
) -> dict[str, Any]:
    """Aggregate current evidence into a publication-route decision."""

    official = _load(official_audit)
    robust = _load(sensitivity)
    microns = _load(microns_gate)
    official_ready = bool(official["official_baseline_viable"])
    official_stack_forward_ok = bool(official.get("official_stack_forward_ok", False))
    microns_ready = bool(microns["approved"])

    q1_ready = official_ready or microns_ready
    route = (
        "q1_candidate_after_external_baseline_or_microns_pilot"
        if q1_ready
        else "methodological_benchmark_paper_now_q1_requires_external_piece"
    )
    return {
        "version": __version__,
        "git_revision": code_revision(),
        "inputs": {
            "official_audit": str(official_audit),
            "sensitivity": str(sensitivity),
            "microns_gate": str(microns_gate),
            "proposal_status": str(proposal_status),
        },
        "official_sensorium_baseline_viable": official_ready,
        "official_sensorium_stack_forward_ok": official_stack_forward_ok,
        "microns_pilot_approved": microns_ready,
        "sensitivity_decision": robust["decision"],
        "publication_route": route,
        "q1_ready": q1_ready,
        "methodological_paper_ready": True,
        "claims_allowed": [
            "MouseBrainBench separates prediction, OOD, reliability, and mechanistic gates.",
            "Allen VBN is a real negative case: reproducible but not mechanistically identifiable.",
            "Sensorium/Dynamic Sensorium provide modern predictive cases with local NN control.",
            "Sensorium static provides partial positive reliability/topographic evidence.",
            "The official Sensorium stack can run a local forward-pass smoke test.",
        ],
        "claims_blocked": [
            "A complete digital twin of mouse brain.",
            "A SOTA Sensorium predictor.",
            "An official trained Sensorium baseline until trained/evaluated predictions exist.",
            "Causal mechanistic identifiability in Dynamic Sensorium.",
            "MICrONS structure-function claims without an approved bounded pilot.",
        ],
        "next_required_piece": (
            "None for a methodological benchmark paper; for Q1, train/evaluate an "
            "official Sensorium baseline or execute an approved bounded MICrONS pilot."
        ),
    }


def write_outputs(payload: dict[str, Any], output: Path, markdown: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    lines = [
        "# Publication Freeze",
        "",
        f"- Publication route: `{payload['publication_route']}`",
        f"- Methodological paper ready: `{payload['methodological_paper_ready']}`",
        f"- Q1 ready now: `{payload['q1_ready']}`",
        f"- Official Sensorium stack forward OK: `{payload['official_sensorium_stack_forward_ok']}`",
        f"- Official Sensorium baseline viable: `{payload['official_sensorium_baseline_viable']}`",
        f"- MICrONS pilot approved: `{payload['microns_pilot_approved']}`",
        "",
        "## Claims allowed",
        "",
    ]
    lines.extend(f"- {claim}" for claim in payload["claims_allowed"])
    lines.extend(["", "## Claims blocked", ""])
    lines.extend(f"- {claim}" for claim in payload["claims_blocked"])
    lines.extend(["", "## Next required piece", "", payload["next_required_piece"], ""])
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines))


def run(output: Path = DEFAULT_OUTPUT, markdown: Path = DEFAULT_MARKDOWN) -> Path:
    payload = build_freeze_payload()
    write_outputs(payload, output, markdown)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    print(json.dumps({"output": str(run(args.output, args.markdown).resolve())}))


if __name__ == "__main__":
    main()
