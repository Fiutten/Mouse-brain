"""Contract tests for directed-signature diagnostics in Phase 4."""

from __future__ import annotations

import numpy as np

from mousebrainbench.benchmarks.allen_vbn_phase4 import (
    latency_signature,
    lead_lag_signature,
    resolvable_pair_fraction,
)


def test_latency_signature_returns_peak_bins_after_onset() -> None:
    time = np.asarray([-0.05, 0.05, 0.10, 0.15])
    activity = np.asarray(
        [
            [1.0, 1.0],
            [2.0, 1.0],
            [1.0, 3.0],
            [1.0, 1.0],
        ]
    )
    np.testing.assert_allclose(latency_signature(activity, time, 0.15), [0.05, 0.10])


def test_resolvable_pair_fraction_requires_one_bin_difference() -> None:
    latencies = np.asarray([0.05, 0.05, 0.10, 0.20])
    assert resolvable_pair_fraction(latencies, 0.05) == 5 / 6


def test_lead_lag_signature_detects_delayed_second_region() -> None:
    time = np.arange(-0.05, 0.30, 0.05)
    first = np.asarray([0, 0, 1, 0, 0, 0, 0], dtype=float)
    second = np.asarray([0, 0, 0, 1, 0, 0, 0], dtype=float)
    activity = np.column_stack((first, second))
    signature = lead_lag_signature(activity, time, response_stop=0.25, max_lag_bins=2)
    np.testing.assert_array_equal(signature, [1])


def test_lead_lag_signature_marks_synchronous_regions_as_zero() -> None:
    time = np.arange(-0.05, 0.30, 0.05)
    pulse = np.asarray([0, 0, 1, 0, 0, 0, 0], dtype=float)
    activity = np.column_stack((pulse, pulse))
    signature = lead_lag_signature(activity, time, response_stop=0.25, max_lag_bins=2)
    np.testing.assert_array_equal(signature, [0])
