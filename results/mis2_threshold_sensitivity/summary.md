# MIS 2.0 Threshold Sensitivity

- Decision: `mis2_sensitivity_supports_conservative_gate`
- Operating cells: `60`
- Seeds per scenario: `6`

## Phase Counts

| Phase | Count | Interpretation |
|---|---:|---|
| `safe` | `30` | FPR is zero and FNR remains low. |
| `conservative` | `30` | FPR is zero, but FNR is high under weak data regimes. |
| `dangerous` | `0` | FPR is non-zero while sensitivity appears acceptable. |
| `unstable` | `0` | FPR and FNR are both problematic. |

## Nominal Profile

| Noise | Sessions | FPR | FNR | Phase |
|---:|---:|---:|---:|---|
| `0.08` | `6` | `0.000` | `0.000` | `safe` |
| `0.08` | `12` | `0.000` | `0.000` | `safe` |
| `0.08` | `24` | `0.000` | `0.000` | `safe` |
| `0.24` | `6` | `0.000` | `0.000` | `safe` |
| `0.24` | `12` | `0.000` | `0.000` | `safe` |
| `0.24` | `24` | `0.000` | `0.000` | `safe` |
| `0.45` | `6` | `0.000` | `0.000` | `safe` |
| `0.45` | `12` | `0.000` | `0.000` | `safe` |
| `0.45` | `24` | `0.000` | `0.000` | `safe` |
| `0.60` | `6` | `0.000` | `0.333` | `conservative` |
| `0.60` | `12` | `0.000` | `0.833` | `conservative` |
| `0.60` | `24` | `0.000` | `1.000` | `conservative` |

## Worst Conservative Cells

| Profile | Noise | Sessions | FPR | FNR | Phase |
|---|---:|---:|---:|---:|---|
| `nominal` | `0.60` | `24` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.08` | `6` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.08` | `12` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.08` | `24` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.24` | `6` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.24` | `12` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.24` | `24` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.45` | `6` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.45` | `12` | `0.000` | `1.000` | `conservative` |
| `strict_all` | `0.45` | `24` | `0.000` | `1.000` | `conservative` |

## Interpretation

The useful operating region is defined by zero false positives in the designed non-mechanistic cases. Conservative cells are not failures of the claim gate. They show where low SNR, few sessions, or strict thresholds prevent a true mechanistic signal from passing. Dangerous or unstable cells would require threshold redesign before using MIS 2.0 as a stronger methodological claim.
