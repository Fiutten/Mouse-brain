"""Contract tests for the real-data Allen VBN loader using a tiny NWB fixture."""

from __future__ import annotations

import hashlib
import json

import h5py
import numpy as np
import pandas as pd
import pytest

from mousebrainbench.data.loaders.allen_vbn import AllenVBNRepository
from mousebrainbench.benchmarks.allen_vbn import run_benchmark
from mousebrainbench.benchmarks.allen_vbn_phase2b import run_phase2b
from mousebrainbench.benchmarks.allen_vbn_phase2c import (
    _validate_confirmation_plan,
    run_development,
    transform_timecourse,
)


def _repository_fixture(tmp_path) -> AllenVBNRepository:
    root = tmp_path / "visual-behavior-neuropixels-0.5.0"
    metadata = root / "project_metadata"
    metadata.mkdir(parents=True)
    units = pd.DataFrame(
        {
            "unit_id": list(range(1, 9)),
            "ecephys_session_id": [101] * 4 + [102] * 4,
            "structure_acronym": ["VISp", "VISp", "VISl", "VISl"] * 2,
            "quality": ["good"] * 8,
            "valid_data": [True] * 8,
            "amplitude_cutoff": [0.01] * 8,
            "presence_ratio": [0.99] * 8,
            "isi_violations": [0.01] * 8,
        }
    )
    sessions = pd.DataFrame(
        {
            "ecephys_session_id": [101, 102],
            "mouse_id": [9, 10],
            "experience_level": ["Familiar", "Novel"],
        }
    )
    files = {
        "units": units.to_csv(index=False),
        "ecephys_sessions": sessions.to_csv(index=False),
        "probes": "id\n",
        "channels": "id\n",
        "behavior_sessions": "id\n",
    }
    manifest_metadata = {}
    for name, content in files.items():
        path = metadata / f"{name}.csv"
        path.write_text(content)
        manifest_metadata[name] = {"file_hash": hashlib.blake2b(path.read_bytes()).hexdigest()}
    manifest = {
        "manifest_version": "0.5.0",
        "data_pipeline": [{"name": "fixture", "version": "1"}],
        "metadata_files": manifest_metadata,
    }
    (tmp_path / "visual-behavior-neuropixels_project_manifest_v0.5.0.json").write_text(
        json.dumps(manifest)
    )
    for session_id, unit_ids in ((101, [1, 2, 3, 4]), (102, [5, 6, 7, 8])):
        session_dir = root / "behavior_ecephys_sessions" / str(session_id)
        session_dir.mkdir(parents=True)
        with h5py.File(session_dir / f"ecephys_session_{session_id}.nwb", "w") as nwb:
            unit_group = nwb.create_group("units")
            unit_group.create_dataset("id", data=np.array(unit_ids))
            unit_group.create_dataset(
                "spike_times",
                data=np.array(
                    [
                        0.2,
                        1.2,
                        2.2,
                        3.2,
                        0.3,
                        1.3,
                        2.3,
                        3.3,
                        0.4,
                        1.4,
                        2.4,
                        3.4,
                        0.5,
                        1.5,
                        2.5,
                        3.5,
                    ]
                ),
            )
            unit_group.create_dataset("spike_times_index", data=np.array([4, 8, 12, 16]))
            spontaneous = nwb.create_group("intervals/spontaneous_presentations")
            spontaneous.create_dataset("start_time", data=np.array([0.0]))
            spontaneous.create_dataset("stop_time", data=np.array([4.0]))
            image_set = "G" if session_id == 101 else "H"
            presentations = nwb.create_group(
                f"intervals/Natural_Images_Lum_Matched_set_ophys_{image_set}_2019_presentations"
            )
            presentations.create_dataset("start_time", data=np.array([0.5, 1.5, 2.5, 3.5]))
            presentations.create_dataset("is_change", data=np.ones(4))
            presentations.create_dataset("omitted", data=np.zeros(4))
            presentations.create_dataset("active", data=np.ones(4, dtype=bool))
    return AllenVBNRepository(root)


def test_allen_metadata_hashes_and_qualification(tmp_path) -> None:
    repository = _repository_fixture(tmp_path)
    assert all(repository.verify_metadata_hashes().values())
    decision = repository.qualify_sessions(("VISp", "VISl"), min_units_per_region=2)[0]
    assert decision.accepted
    assert decision.mouse_id == 9


def test_allen_spontaneous_activity_extraction(tmp_path) -> None:
    repository = _repository_fixture(tmp_path)
    activity = repository.extract_spontaneous_activity(
        101, ("VISp", "VISl"), bin_size_seconds=1.0, min_units_per_region=2
    )
    assert activity.activity_hz.shape == (4, 2)
    np.testing.assert_array_equal(activity.activity_hz, np.ones((4, 2)))
    assert activity.metadata["biological"] is True


def test_allen_benchmark_runs_end_to_end(tmp_path) -> None:
    repository = _repository_fixture(tmp_path)
    config = {
        "data": {
            "root": str(repository.root),
            "regions": ["VISp", "VISl"],
            "min_units_per_region": 2,
            "bin_size_seconds": 1.0,
        },
        "analysis": {"minimum_sessions": 2, "permutations": 5, "seed": 3},
        "output": {"root": str(tmp_path / "outputs"), "name": "fixture"},
    }
    output = run_benchmark(config)
    metrics = json.loads((output / "metrics.json").read_text())
    assert metrics["dataset"]["successfully_extracted_sessions"] == 2
    assert all(metrics["dataset"]["metadata_hashes_valid"].values())


def test_allen_change_response_and_phase2b_run_end_to_end(tmp_path) -> None:
    repository = _repository_fixture(tmp_path)
    response = repository.extract_change_response_profile(
        101, ("VISp", "VISl"), min_units_per_region=2, window_seconds=0.25
    )
    assert response.response_hz.shape == (2,)
    assert response.event_count == 4
    config = {
        "data": {
            "root": str(repository.root),
            "regions": ["VISp", "VISl"],
            "min_units_per_region": 2,
        },
        "analysis": {
            "base_bin_seconds": 1.0,
            "sensitivity_bin_seconds": [1.0],
            "sensitivity_window_seconds": [2],
            "evoked_window_seconds": 0.25,
            "minimum_sessions": 2,
            "permutations": 5,
            "bootstrap_samples": 10,
            "seed": 3,
            "candidate_thresholds": {
                "median_cross_mouse_correlation_gt": 0.5,
                "median_split_half_correlation_gt": 0.5,
                "fraction_above_null_95_gte": 0.5,
            },
        },
        "output": {"root": str(tmp_path / "outputs"), "name": "phase2b-fixture"},
    }
    output = run_phase2b(config)
    metrics = json.loads((output / "metrics.json").read_text())
    assert set(metrics["candidate_results"]) == {
        "spontaneous_fc",
        "spontaneous_rate_profile",
        "visual_change_response_profile",
    }


def test_allen_temporal_response_and_phase2c_development(tmp_path) -> None:
    repository = _repository_fixture(tmp_path)
    response = repository.extract_change_response_timecourse(
        101,
        ("VISp", "VISl"),
        min_units_per_region=2,
        start_seconds=-0.25,
        stop_seconds=0.75,
        bin_size_seconds=0.25,
    )
    assert response.activity_hz.shape == (4, 2)
    assert transform_timecourse(response.activity_hz, response.time, "baseline_subtracted").shape == (
        4,
        2,
    )
    config = {
        "data": {
            "root": str(repository.root),
            "regions": ["VISp", "VISl"],
            "min_units_per_region": 2,
        },
        "target": {
            "start_seconds": -0.25,
            "stop_seconds": 0.75,
            "bin_size_seconds": 0.25,
            "candidates": ["baseline_subtracted"],
        },
        "analysis": {
            "permutations": 5,
            "bootstrap_samples": 10,
            "seed": 3,
            "thresholds": {
                "median_cross_mouse_correlation_gt": -1.0,
                "median_split_half_correlation_gt": -1.0,
                "fraction_above_null_95_gte": 0.0,
                "bootstrap_lower_bound_gt": -1.0,
            },
        },
        "output": {"root": str(tmp_path / "outputs"), "development_name": "phase2c"},
    }
    output = run_development(config)
    assert (output / "development_arrays.npz").exists()


def test_phase2c_confirmation_rejects_configuration_drift() -> None:
    target = {
        "start_seconds": -0.25,
        "stop_seconds": 0.75,
        "bin_size_seconds": 0.05,
        "candidates": ["temporal_derivative"],
    }
    thresholds = {
        "median_cross_mouse_correlation_gt": 0.5,
        "median_split_half_correlation_gt": 0.7,
        "fraction_above_null_95_gte": 0.5,
        "bootstrap_lower_bound_gt": 0.0,
    }
    plan = {
        "sealed_before_download": True,
        "selected_target": "temporal_derivative",
        "target": target,
        "thresholds": thresholds,
    }
    config = {"target": target, "analysis": {"thresholds": thresholds | {"extra": 1.0}}}

    with pytest.raises(ValueError, match="thresholds differ"):
        _validate_confirmation_plan(plan, config)
