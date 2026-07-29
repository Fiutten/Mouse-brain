# Claim Adversarial Benchmark

- Decision: `claim_gate_blocks_adversarial_overclaims`
- Cases: `8`
- Claim types: `8`

## Aggregate Confusion

| Evaluator | TP | FP | TN | FN | FPR | FNR |
|---|---:|---:|---:|---:|---:|---:|
| `claim_gate` | `31` | `0` | `33` | `0` | `0.000` | `0.000` |
| `compensatory_score` | `26` | `6` | `27` | `5` | `0.182` | `0.161` |
| `correlation_only` | `28` | `20` | `13` | `3` | `0.606` | `0.097` |

## False-Positive Claims By Case

| Case | Evaluator | False-positive claims |
|---|---|---|
| `directed_mechanistic_truth` | `correlation_only` | `structure_function` |
| `common_drive_high_prediction` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `topology_without_direction` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `direction_without_topology` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `local_structure_function_truth` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `causal_component_truth` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth` | `compensatory_score` | `structure_function` |
| `topology_without_direction` | `compensatory_score` | `directed`, `mechanistic`, `structure_function` |
| `causal_component_truth` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth` | `compensatory_score` | `structure_function` |

## Interpretation

The benchmark is useful only if simple evaluators over-authorize claims in designed adversarial cases while the non-compensatory gate blocks them. That is the methodological gap MouseBrainBench should emphasize.
