import json

from mousebrainbench.benchmarks.microns_pilot_gate import evaluate_manifest


def test_microns_gate_defers_without_manifest(tmp_path) -> None:
    payload = evaluate_manifest(tmp_path / "missing.json")

    assert not payload["approved"]
    assert payload["decision"] == "defer_microns_until_small_manifest_available"


def test_microns_gate_approves_bounded_manifest(tmp_path) -> None:
    manifest = tmp_path / "pilot_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "n_neurons": 1200,
                "has_spatial_coordinates": True,
                "has_functional_responses": True,
                "has_structural_edges": True,
                "estimated_download_gb": 1.5,
            }
        )
    )

    payload = evaluate_manifest(manifest)

    assert payload["approved"]
    assert payload["decision"] == "approve_bounded_microns_structure_function_pilot"
