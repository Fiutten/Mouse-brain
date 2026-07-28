# MIS 2.0 Synthetic Calibration

- Decision: `mis2_nominal_synthetic_suite_passed`
- Runs: `108`
- False-positive rate: `0.0000`
- False-negative rate: `0.1667`

## Scenario Summary

| Scenario | Truth | MIS pass rate | FP | FN | Repro | Topology | Direction |
|---|---:|---:|---:|---:|---:|---:|---:|
| `clean_directed_truth` | `True` | `1.000` | `0` | `0` | `1.000` | `1.000` | `1.000` |
| `noisy_directed_truth` | `True` | `1.000` | `0` | `0` | `1.000` | `1.000` | `1.000` |
| `low_sample_directed_truth` | `True` | `1.000` | `0` | `0` | `1.000` | `1.000` | `1.000` |
| `low_snr_directed_truth` | `True` | `0.333` | `0` | `8` | `0.333` | `1.000` | `1.000` |
| `common_drive_high_reproducibility` | `False` | `0.000` | `0` | `0` | `1.000` | `0.000` | `0.000` |
| `topology_without_direction` | `False` | `0.000` | `0` | `0` | `1.000` | `1.000` | `0.000` |
| `direction_without_topology` | `False` | `0.000` | `0` | `0` | `1.000` | `0.000` | `1.000` |
| `prediction_without_true_topology` | `False` | `0.000` | `0` | `0` | `1.000` | `0.000` | `0.000` |
| `noisy_common_drive` | `False` | `0.000` | `0` | `0` | `1.000` | `0.000` | `0.000` |

## Interpretation

This calibration is intentionally synthetic. A zero false-positive rate in these cases means the current non-compensatory MIS gate rejects the designed non-mechanistic failure modes. False negatives identify conservative low-SNR or low-sample regions of the gate and should be interpreted as sensitivity, not biological failure.
