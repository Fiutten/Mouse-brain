# Claim Adversarial Benchmark

- Decision: `claim_gate_blocks_broad_adversarial_overclaims`
- Cases: `54`
- Claim types: `8`

## Aggregate Confusion

| Evaluator | TP | FP | TN | FN | ORI | CI |
|---|---:|---:|---:|---:|---:|---:|
| `ablated_claim_gate_no_directed` | `216` | `6` | `210` | `0` | `0.028` | `0.000` |
| `claim_gate` | `216` | `0` | `216` | `0` | `0.000` | `0.000` |
| `compensatory_score` | `183` | `33` | `183` | `33` | `0.153` | `0.153` |
| `correlation_only` | `198` | `126` | `90` | `18` | `0.583` | `0.083` |
| `leaderboard_only` | `195` | `123` | `93` | `21` | `0.569` | `0.097` |
| `reliability_only` | `132` | `64` | `152` | `84` | `0.296` | `0.389` |
| `topology_only` | `78` | `12` | `204` | `138` | `0.056` | `0.639` |

## False-Positive Claims By Case

| Case | Evaluator | False-positive claims |
|---|---|---|
| `directed_mechanistic_truth__nominal` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__high_prediction` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__high_reproducibility` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__low_prediction_margin` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__low_reproducibility_margin` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__ood_shift` | `correlation_only` | `structure_function` |
| `common_drive_high_prediction__nominal` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__high_prediction` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__high_reproducibility` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__low_prediction_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__low_reproducibility_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__ood_shift` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `topology_without_direction__nominal` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_prediction` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_reproducibility` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__low_prediction_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__low_reproducibility_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__ood_shift` | `correlation_only` | `directed`, `mechanistic`, `structure_function` |
| `direction_without_topology__nominal` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__high_prediction` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__high_reproducibility` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__low_prediction_margin` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__low_reproducibility_margin` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__ood_shift` | `correlation_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__nominal` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__high_prediction` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__high_reproducibility` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__low_prediction_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__low_reproducibility_margin` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__ood_shift` | `correlation_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `local_structure_function_truth__nominal` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_prediction` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_reproducibility` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__low_prediction_margin` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__low_reproducibility_margin` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__ood_shift` | `correlation_only` | `directed`, `mechanistic`, `topology_specific` |
| `causal_component_truth__nominal` | `correlation_only` | `structure_function` |
| `causal_component_truth__high_prediction` | `correlation_only` | `structure_function` |
| `causal_component_truth__high_reproducibility` | `correlation_only` | `structure_function` |
| `causal_component_truth__low_prediction_margin` | `correlation_only` | `structure_function` |
| `causal_component_truth__low_reproducibility_margin` | `correlation_only` | `structure_function` |
| `causal_component_truth__ood_shift` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__nominal` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__high_prediction` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__high_reproducibility` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__low_prediction_margin` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__low_reproducibility_margin` | `correlation_only` | `structure_function` |
| `false_digital_twin_decoy__ood_shift` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__nominal` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__high_prediction` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__high_reproducibility` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__low_prediction_margin` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__low_reproducibility_margin` | `correlation_only` | `structure_function` |
| `whole_brain_digital_twin_truth__ood_shift` | `correlation_only` | `structure_function` |
| `directed_mechanistic_truth__nominal` | `leaderboard_only` | `structure_function` |
| `directed_mechanistic_truth__high_prediction` | `leaderboard_only` | `structure_function` |
| `directed_mechanistic_truth__high_reproducibility` | `leaderboard_only` | `structure_function` |
| `directed_mechanistic_truth__low_prediction_margin` | `leaderboard_only` | `structure_function` |
| `directed_mechanistic_truth__low_reproducibility_margin` | `leaderboard_only` | `structure_function` |
| `directed_mechanistic_truth__ood_shift` | `leaderboard_only` | `structure_function` |
| `common_drive_high_prediction__nominal` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__high_prediction` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__high_reproducibility` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__low_prediction_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__low_reproducibility_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `common_drive_high_prediction__ood_shift` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `topology_without_direction__nominal` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_prediction` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_reproducibility` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__low_prediction_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__low_reproducibility_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__ood_shift` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function` |
| `direction_without_topology__nominal` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__high_prediction` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__high_reproducibility` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__low_prediction_margin` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__low_reproducibility_margin` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `direction_without_topology__ood_shift` | `leaderboard_only` | `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__nominal` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__high_prediction` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__high_reproducibility` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__low_prediction_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__low_reproducibility_margin` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `spatial_confound_structure_function__ood_shift` | `leaderboard_only` | `directed`, `mechanistic`, `structure_function`, `topology_specific` |
| `local_structure_function_truth__nominal` | `leaderboard_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_prediction` | `leaderboard_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_reproducibility` | `leaderboard_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__low_prediction_margin` | `leaderboard_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__low_reproducibility_margin` | `leaderboard_only` | `directed`, `mechanistic`, `topology_specific` |
| `causal_component_truth__nominal` | `leaderboard_only` | `structure_function` |
| `causal_component_truth__high_prediction` | `leaderboard_only` | `structure_function` |
| `causal_component_truth__high_reproducibility` | `leaderboard_only` | `structure_function` |
| `causal_component_truth__low_prediction_margin` | `leaderboard_only` | `structure_function` |
| `causal_component_truth__low_reproducibility_margin` | `leaderboard_only` | `structure_function` |
| `causal_component_truth__ood_shift` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__nominal` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__high_prediction` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__high_reproducibility` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__low_prediction_margin` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__low_reproducibility_margin` | `leaderboard_only` | `structure_function` |
| `false_digital_twin_decoy__ood_shift` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__nominal` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__high_prediction` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__high_reproducibility` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__low_prediction_margin` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__low_reproducibility_margin` | `leaderboard_only` | `structure_function` |
| `whole_brain_digital_twin_truth__ood_shift` | `leaderboard_only` | `structure_function` |
| `common_drive_high_prediction__nominal` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `common_drive_high_prediction__high_prediction` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `common_drive_high_prediction__high_reproducibility` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `common_drive_high_prediction__low_prediction_margin` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `common_drive_high_prediction__low_reproducibility_margin` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `common_drive_high_prediction__ood_shift` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `topology_without_direction__nominal` | `reliability_only` | `directed`, `mechanistic` |
| `topology_without_direction__high_prediction` | `reliability_only` | `directed`, `mechanistic` |
| `topology_without_direction__high_reproducibility` | `reliability_only` | `directed`, `mechanistic` |
| `topology_without_direction__low_prediction_margin` | `reliability_only` | `directed`, `mechanistic` |
| `topology_without_direction__low_reproducibility_margin` | `reliability_only` | `directed`, `mechanistic` |
| `topology_without_direction__ood_shift` | `reliability_only` | `directed`, `mechanistic` |
| `direction_without_topology__nominal` | `reliability_only` | `mechanistic`, `topology_specific` |
| `direction_without_topology__high_prediction` | `reliability_only` | `mechanistic`, `topology_specific` |
| `direction_without_topology__high_reproducibility` | `reliability_only` | `mechanistic`, `topology_specific` |
| `direction_without_topology__low_prediction_margin` | `reliability_only` | `mechanistic`, `topology_specific` |
| `direction_without_topology__low_reproducibility_margin` | `reliability_only` | `mechanistic`, `topology_specific` |
| `spatial_confound_structure_function__nominal` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `spatial_confound_structure_function__high_prediction` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `spatial_confound_structure_function__high_reproducibility` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `spatial_confound_structure_function__low_prediction_margin` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__nominal` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_prediction` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__high_reproducibility` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `local_structure_function_truth__low_prediction_margin` | `reliability_only` | `directed`, `mechanistic`, `topology_specific` |
| `topology_without_direction__nominal` | `topology_only` | `directed`, `mechanistic` |
| `topology_without_direction__high_prediction` | `topology_only` | `directed`, `mechanistic` |
| `topology_without_direction__high_reproducibility` | `topology_only` | `directed`, `mechanistic` |
| `topology_without_direction__low_prediction_margin` | `topology_only` | `directed`, `mechanistic` |
| `topology_without_direction__low_reproducibility_margin` | `topology_only` | `directed`, `mechanistic` |
| `topology_without_direction__ood_shift` | `topology_only` | `directed`, `mechanistic` |
| `directed_mechanistic_truth__nominal` | `compensatory_score` | `structure_function` |
| `directed_mechanistic_truth__high_prediction` | `compensatory_score` | `structure_function` |
| `directed_mechanistic_truth__high_reproducibility` | `compensatory_score` | `structure_function` |
| `directed_mechanistic_truth__low_prediction_margin` | `compensatory_score` | `structure_function` |
| `directed_mechanistic_truth__low_reproducibility_margin` | `compensatory_score` | `structure_function` |
| `directed_mechanistic_truth__ood_shift` | `compensatory_score` | `structure_function` |
| `topology_without_direction__nominal` | `compensatory_score` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_prediction` | `compensatory_score` | `directed`, `mechanistic`, `structure_function` |
| `topology_without_direction__high_reproducibility` | `compensatory_score` | `directed`, `mechanistic`, `structure_function` |
| `causal_component_truth__nominal` | `compensatory_score` | `structure_function` |
| `causal_component_truth__high_prediction` | `compensatory_score` | `structure_function` |
| `causal_component_truth__high_reproducibility` | `compensatory_score` | `structure_function` |
| `causal_component_truth__low_prediction_margin` | `compensatory_score` | `structure_function` |
| `causal_component_truth__low_reproducibility_margin` | `compensatory_score` | `structure_function` |
| `causal_component_truth__ood_shift` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__nominal` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__high_prediction` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__high_reproducibility` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__low_prediction_margin` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__low_reproducibility_margin` | `compensatory_score` | `structure_function` |
| `false_digital_twin_decoy__ood_shift` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__nominal` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__high_prediction` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__high_reproducibility` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__low_prediction_margin` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__low_reproducibility_margin` | `compensatory_score` | `structure_function` |
| `whole_brain_digital_twin_truth__ood_shift` | `compensatory_score` | `structure_function` |
| `topology_without_direction__nominal` | `ablated_claim_gate_no_directed` | `mechanistic` |
| `topology_without_direction__high_prediction` | `ablated_claim_gate_no_directed` | `mechanistic` |
| `topology_without_direction__high_reproducibility` | `ablated_claim_gate_no_directed` | `mechanistic` |
| `topology_without_direction__low_prediction_margin` | `ablated_claim_gate_no_directed` | `mechanistic` |
| `topology_without_direction__low_reproducibility_margin` | `ablated_claim_gate_no_directed` | `mechanistic` |
| `topology_without_direction__ood_shift` | `ablated_claim_gate_no_directed` | `mechanistic` |

## Interpretation

The benchmark is useful only if shortcut evaluators over-authorize claims in designed adversarial cases while the non-compensatory gate blocks them. ORI is the overclaiming risk index. CI is the conservativeness index.
