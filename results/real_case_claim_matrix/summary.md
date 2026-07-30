# Real-Case Claim Matrix

- Decision: `real_case_claim_gate_consistent`
- Cases: `5`

## Cases

| Case | Expected claims | Source |
|---|---|---|
| `allen_vbn_negative_identifiability` | `predictive`, `reproducible` | `results/allen_vbn_mechanistic_identifiability_score.json` |
| `sensorium_static_predictive_interoperability` | `predictive`, `reproducible`, `topology_specific` | `results/sensorium_static_model_comparator/summary.json` |
| `dynamic_sensorium_predictive_temporal_case` | `predictive`, `reproducible` | `results/dynamic_sensorium_model_comparator/summary.json` |
| `microns_local_structure_function` | `predictive`, `reproducible`, `structure_function` | `results/microns_primary_robustness/summary.json` |
| `synthetic_causal_graph_positive_control` | `predictive`, `reproducible`, `topology_specific`, `directed`, `mechanistic`, `causal` | `synthetic_calibration_case` |

## Aggregate Confusion

| Evaluator | TP | FP | TN | FN | ORI | CI |
|---|---:|---:|---:|---:|---:|---:|
| `claim_gate` | `16` | `0` | `24` | `0` | `0.000` | `0.000` |
| `compensatory_score` | `13` | `1` | `23` | `3` | `0.042` | `0.188` |
| `correlation_only` | `12` | `12` | `12` | `4` | `0.500` | `0.250` |
| `leaderboard_only` | `10` | `8` | `16` | `6` | `0.333` | `0.375` |
