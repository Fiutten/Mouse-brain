"""Contract tests for the Phase 3 anatomical-functional benchmark."""

from __future__ import annotations

import json

import numpy as np
import pytest

from mousebrainbench.benchmarks.allen_visual_phase3 import (
    _derive_drive,
    _permuted_weights,
    _validate_plan,
    simulate_target,
)
from mousebrainbench.data.loaders.allen_connectivity import load_allen_visual_connectivity


def test_allen_visual_connectivity_has_explicit_orientation_and_zero_diagonal() -> None:
    regions, connectivity, payload = load_allen_visual_connectivity(
        "mousebrainbench/data/reference/allen_visual_connectivity.json",
        ("VISp", "VISl", "VISal", "VISrl", "VISpm", "VISam"),
    )
    assert [region.acronym for region in regions] == ["VISp", "VISl", "VISal", "VISrl", "VISpm", "VISam"]
    np.testing.assert_array_equal(np.diag(connectivity.dense_weights()), 0.0)
    assert payload["aggregation"].startswith("median normalized_projection_volume")


def test_phase3_permutation_preserves_weights_and_zero_diagonal() -> None:
    weights = np.arange(36, dtype=float).reshape(6, 6)
    np.fill_diagonal(weights, 0.0)
    permuted = _permuted_weights(weights, seed=3)
    mask = ~np.eye(6, dtype=bool)
    np.testing.assert_array_equal(np.sort(permuted[mask]), np.sort(weights[mask]))
    np.testing.assert_array_equal(np.diag(permuted), 0.0)
    assert not np.array_equal(permuted, weights)


def test_phase3_simulation_and_drive_are_finite() -> None:
    time = np.arange(-0.225, 0.775, 0.05)
    targets = np.zeros((2, len(time), 2))
    targets[:, np.flatnonzero(time > 0)[0], :] = [[1.0, -0.5], [0.8, -0.4]]
    drive = _derive_drive(targets, time)
    prediction = simulate_target(
        "linear_rate",
        {"tau": 0.1, "coupling": 0.5, "drive_scale": 1.0},
        np.asarray([[0.0, 0.2], [0.7, 0.0]]),
        drive,
        time,
        "temporal_derivative",
    )
    assert prediction.shape == targets.shape[1:]
    assert np.all(np.isfinite(prediction))


def test_phase3_confirmation_rejects_connectivity_drift(tmp_path) -> None:
    connectivity = tmp_path / "connectivity.json"
    connectivity.write_text(json.dumps({"version": 1}))
    target = {"transformation": "temporal_derivative"}
    thresholds = {"minimum": 0.0}
    config = {
        "data": {"connectivity_path": str(connectivity)},
        "target": target,
        "analysis": {"thresholds": thresholds},
    }
    plan = {
        "sealed_before_confirmation": True,
        "connectivity_sha256": "wrong",
        "target": target,
        "thresholds": thresholds,
    }
    with pytest.raises(ValueError, match="connectivity file differs"):
        _validate_plan(plan, config)
