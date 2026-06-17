import json

import numpy as np

from mousebrainbench.benchmarks.sensorium_predictive_mis import run_sensorium_benchmark
from mousebrainbench.benchmarks.sensorium_synthetic_smoke import run
from mousebrainbench.data.loaders.sensorium import SensoriumTrialTable


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


def test_sensorium_benchmark_marks_reliability_not_estimable_without_repeats(tmp_path) -> None:
    table = SensoriumTrialTable(
        root=tmp_path,
        modality="dynamic",
        stimulus_features=np.arange(20, dtype=float).reshape(4, 5),
        context_features=np.empty((4, 0), dtype=float),
        responses=np.arange(12, dtype=float).reshape(4, 3),
        tiers=np.asarray(["train", "train", "oracle", "oracle"]),
        trial_ids=np.arange(4),
        stimulus_ids=np.arange(4),
        neuron_ids=np.arange(3),
    )

    output = run_sensorium_benchmark(
        table, output=tmp_path / "no_repeats.json", eval_tiers=("oracle",)
    )
    payload = json.loads(output.read_text())

    assert payload["metrics"]["reliability"] == 0.0
    assert not payload["metrics"]["reliability_estimable"]
    assert payload["metrics"]["reliability_repeated_stimuli"] == 0.0
