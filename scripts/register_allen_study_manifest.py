"""Register the canonical Allen study state for reproducibility.

This is a lightweight manifest, not a workflow runner. It records the command
sequence, exact input/output artifact paths, SHA-256 hashes for existing files,
and current dataset/session inventory. The purpose is to make the study state
auditable before adding more model complexity.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neurotwin_mvp.registry import sha256_file


ROOT = Path(__file__).resolve().parents[1]


CANONICAL_COMMANDS = [
    "make allen-temporal-windows",
    "make allen-temporal-permutation-confirm",
    "make allen-temporal-regional-ablation",
    "make allen-uncertainty",
    "make allen-response-controls",
    "make allen-functional-graph",
    "make allen-generative-surrogate",
    "make allen-scientific-agent",
    "make allen-advanced-evidence",
    "make allen-fragility-analysis",
    "make allen-fragility-explanations",
    "make allen-fragile-alternative-windows",
    "make allen-within-session-states",
    "make allen-animal-aware-validation",
    "make allen-recording-coverage",
    "make test",
]


CANONICAL_ARTIFACTS = [
    "artifacts/reports/allen_targets/go_response_temporal_windows.json",
    "artifacts/reports/allen_targets/go_response_pre_response_permutation_500.json",
    "artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.csv",
    "artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.csv",
    "artifacts/reports/allen_targets/go_response_pre_response_uncertainty.json",
    "artifacts/reports/allen_targets/go_response_pre_response_controls.json",
    "artifacts/reports/allen_targets/go_response_pre_response_functional_graph.json",
    "artifacts/reports/allen_targets/go_response_pre_response_generative_surrogate.json",
    "artifacts/reports/allen_targets/go_response_scientific_agent.json",
    "artifacts/reports/allen_targets/go_response_pre_response_stability_matrix.json",
    "artifacts/reports/allen_targets/go_response_latent_temporal_baseline.json",
    "artifacts/reports/allen_targets/go_response_pre_response_graph_evidence_registry.json",
    "artifacts/reports/allen_targets/go_response_session_generator_v2.json",
    "artifacts/reports/allen_targets/go_response_advanced_scientific_agent.json",
    "artifacts/reports/allen_targets/go_response_selected_microcircuit.json",
    "artifacts/reports/allen_targets/go_response_microcircuit_validation.json",
    "artifacts/reports/allen_targets/go_response_fragile_sessions.json",
    "artifacts/reports/allen_targets/go_response_fragility_explanations.json",
    "artifacts/reports/allen_targets/go_response_fragile_alternative_windows.json",
    "artifacts/reports/allen_targets/go_response_within_session_states.json",
    "artifacts/reports/allen_targets/go_response_animal_aware_validation.json",
    "artifacts/reports/allen_targets/go_response_recording_coverage.json",
]


def hash_optional(path: Path) -> dict[str, Any]:
    """Return existence and hash metadata for one expected artifact."""
    if not path.exists():
        return {"path": str(path.relative_to(ROOT)), "exists": False, "sha256": None, "bytes": None}
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": True,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / "study_manifests" / "allen_go_response_pre_response.json")
    args = parser.parse_args()

    session_paths = sorted((ROOT / "artifacts" / "datasets" / "allen").glob("*/session.json"))
    payload = {
        "study_id": "allen_go_response_pre_response",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Canonical reproducibility manifest for Allen go_response/pre_response evidence layers.",
        "commands": CANONICAL_COMMANDS,
        "dataset_inventory": {
            "normalized_allen_sessions": len(session_paths),
            "session_ids": [path.parent.name for path in session_paths],
        },
        "artifacts": [hash_optional(ROOT / relative) for relative in CANONICAL_ARTIFACTS],
        "environment_notes": [
            "Core analyses run in .venv and consume normalized JSON artifacts.",
            "AllenSDK/NWB extraction remains isolated in .venv-allen; outputs cross environments through artifacts/datasets/allen.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    missing = [item["path"] for item in payload["artifacts"] if not item["exists"]]
    print(f"study_manifest={args.out}")
    print(f"normalized_allen_sessions={payload['dataset_inventory']['normalized_allen_sessions']}")
    print(f"missing_artifacts={len(missing)}")


if __name__ == "__main__":
    main()
