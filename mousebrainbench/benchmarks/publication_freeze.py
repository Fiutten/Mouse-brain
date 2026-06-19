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
    microns_analysis: Path = Path("results/microns_structure_function_pilot/summary.json"),
    microns_expanded_gate: Path = Path("results/microns_pilot_gate/expanded_summary.json"),
    microns_expanded_analysis: Path = Path(
        "results/microns_structure_function_pilot/expanded_summary.json"
    ),
    proposal_status: Path = Path("docs/PROPOSAL_STATUS.md"),
) -> dict[str, Any]:
    """Aggregate current evidence into a publication-route decision."""

    official = _load(official_audit)
    robust = _load(sensitivity)
    microns = _load(microns_gate)
    microns_sf = _load(microns_analysis) if microns_analysis.exists() else {}
    microns_expanded = _load(microns_expanded_gate) if microns_expanded_gate.exists() else {}
    microns_expanded_sf = (
        _load(microns_expanded_analysis) if microns_expanded_analysis.exists() else {}
    )
    official_ready = bool(official["official_baseline_viable"])
    official_stack_forward_ok = bool(official.get("official_stack_forward_ok", False))
    official_trained_available = bool(official.get("official_trained_baseline_available", False))
    official_q1_qualified = bool(official.get("official_q1_baseline_qualified", False))
    microns_ready = bool(microns["approved"])
    microns_micro_ready = bool(microns.get("micro_pilot_approved", False))
    microns_positive = bool(microns_sf.get("positive_structure_function_result", False))
    microns_expanded_q1_ready = bool(microns_expanded.get("q1_pilot_approved", False))
    microns_expanded_positive = bool(
        microns_expanded_sf.get("positive_structure_function_result", False)
    )

    q1_ready = official_ready or (microns_expanded_q1_ready and microns_expanded_positive)
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
            "microns_analysis": str(microns_analysis),
            "microns_expanded_gate": str(microns_expanded_gate),
            "microns_expanded_analysis": str(microns_expanded_analysis),
            "proposal_status": str(proposal_status),
        },
        "official_sensorium_baseline_viable": official_ready,
        "official_sensorium_stack_forward_ok": official_stack_forward_ok,
        "official_sensorium_trained_available": official_trained_available,
        "official_sensorium_q1_qualified": official_q1_qualified,
        "microns_pilot_approved": microns_ready,
        "microns_micro_pilot_approved": microns_micro_ready,
        "microns_structure_function_positive": microns_positive,
        "microns_structure_function_decision": microns_sf.get("scientific_decision"),
        "microns_expanded_q1_pilot_approved": microns_expanded_q1_ready,
        "microns_expanded_structure_function_positive": microns_expanded_positive,
        "microns_expanded_structure_function_decision": microns_expanded_sf.get(
            "scientific_decision"
        ),
        "sensitivity_decision": robust["decision"],
        "publication_route": route,
        "q1_ready": q1_ready,
        "methodological_paper_ready": True,
        "claims_allowed": [
            "MouseBrainBench separates prediction, OOD, reliability, and mechanistic gates.",
            "Allen VBN is a real negative case: reproducible but not mechanistically identifiable.",
            "Sensorium/Dynamic Sensorium provide modern predictive cases with local NN control.",
            "Sensorium static provides partial positive reliability/topographic evidence.",
            "The official Sensorium stack can run local forward-pass and bounded training/evaluation artifacts.",
            "MICrONS now provides a real CAVE-backed micro-pilot, but current structure-function signal is negative/inconclusive.",
            "MICrONS expanded pilot reaches Q1-scale data volume, but current distance-controlled structure-function result is not positive.",
        ],
        "claims_blocked": [
            "A complete digital twin of mouse brain.",
            "A SOTA Sensorium predictor.",
            "A Q1-qualified official Sensorium baseline until the published budget/configuration or official checkpoint is evaluated.",
            "Causal mechanistic identifiability in Dynamic Sensorium.",
            "MICrONS Q1 structure-function claims until the expanded real-edge pilot produces a positive distance/degree-controlled result.",
        ],
        "next_required_piece": (
            "None for a methodological benchmark paper; for Q1, qualify the "
            "official Sensorium baseline with published-scale training/checkpoints "
            "or improve the expanded MICrONS analysis beyond the current negative "
            "distance-controlled result."
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
        f"- Official Sensorium trained available: `{payload['official_sensorium_trained_available']}`",
        f"- Official Sensorium Q1-qualified: `{payload['official_sensorium_q1_qualified']}`",
        f"- Official Sensorium baseline viable: `{payload['official_sensorium_baseline_viable']}`",
        f"- MICrONS pilot approved: `{payload['microns_pilot_approved']}`",
        f"- MICrONS micro-pilot approved: `{payload['microns_micro_pilot_approved']}`",
        f"- MICrONS structure-function positive: `{payload['microns_structure_function_positive']}`",
        f"- MICrONS expanded Q1-scale pilot approved: `{payload['microns_expanded_q1_pilot_approved']}`",
        f"- MICrONS expanded structure-function positive: `{payload['microns_expanded_structure_function_positive']}`",
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
