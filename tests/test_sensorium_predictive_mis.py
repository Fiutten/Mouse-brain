import json

from mousebrainbench.benchmarks.sensorium_synthetic_smoke import run


def test_sensorium_smoke_separates_prediction_from_mechanism(tmp_path) -> None:
    output = run(tmp_path / "sensorium_smoke.json")
    payload = json.loads(output.read_text())
    blocks = {block["name"]: block for block in payload["mis"]["blocks"]}

    assert payload["metrics"]["ridge_correlation"] > 0.9
    assert payload["metrics"]["ridge_minus_mean"] > 0.2
    assert blocks["reproducibility"]["passed"]
    assert blocks["topology_specificity"]["passed"]
    assert not blocks["directed_identifiability"]["passed"]
    assert payload["decision"] == "predictive_signal_requires_extra_mechanistic_evidence"

