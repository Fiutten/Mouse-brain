# Experiment trace

This document tracks the real-data tests performed so far, their commands,
artifacts and scientific interpretation. It is intentionally conservative:
engineering success, exploratory signal and publishable evidence are kept
separate.

## Current dataset state

- Dataset: Allen Visual Behavior Neuropixels.
- Normalized sessions: 15.
- Strict primary target: `go_response`.
- Strict usable `go_response` sessions: 10/15.
- Non-usable `go_response` sessions: 5/15, all due to class imbalance.

## Target viability

Command:

```bash
make allen-targets
```

Artifact:

```text
artifacts/reports/allen/target_diagnostics.json
```

Current target status:

| target | usable sessions | labeled trials | status |
| --- | ---: | ---: | --- |
| `go_response` | 10/15 | 3507 | primary signal target |
| `response_made` | 12/15 | 4005 | broader control, weaker evidence |
| `task_success` | 10/15 | 4005 | correctness control, outcome-confounded |
| `choice` | 12/15 | 4005 | continuity baseline |
| `rewarded` | 12/15 | 4005 | outcome-derived control |
| `catch_response` | 0/15 | 498 | underpowered |

Interpretation: target viability, not download failure, explains why some
sessions are excluded from the strict `go_response` cohort.

## Strict target evidence

Command:

```bash
.venv/bin/python scripts/export_until_target_evidence.py \
  --target-name go_response \
  --target-usable-sessions 10 \
  --final-permutations 500
```

Artifact:

```text
artifacts/reports/allen_targets/go_response_usable/evidence_report.json
```

Result:

| metric | value |
| --- | ---: |
| sessions | 10 |
| strict evidence trials | 2332 |
| mean multi-split gain | 0.034 |
| mean permutation gain | 0.056 |
| positive multi-split fraction | 0.700 |
| significant permutation fraction | 0.300 |
| decision | `inconclusive_mixed_evidence` |

Interpretation: real but mixed signal. Not yet a positive evidence claim.

## Session relationship analysis

Command:

```bash
make allen-session-relations
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_session_relations.json
artifacts/reports/allen_targets/go_response_session_relations.csv
artifacts/reports/allen_targets/go_response_session_relations.md
```

Result:

- 15 sessions analyzed.
- 10 usable `go_response` sessions.
- 5 non-usable sessions.
- 5/5 non-usable sessions fail due to class imbalance below minority fraction
  0.20.
- 3/10 usable sessions are permutation-significant.

Interpretation: failed sessions are target failures, not benchmark failures.

## Target redesign screen

Command:

```bash
.venv/bin/python scripts/run_allen_multisession_reports.py \
  --target-name response_made \
  --require-usable-target \
  --reports-root artifacts/reports/allen_targets/response_made_usable \
  --n-permutations 50

.venv/bin/python scripts/run_allen_evidence_report.py \
  --reports-root artifacts/reports/allen_targets/response_made_usable \
  --out artifacts/reports/allen_targets/response_made_usable/evidence_report.json \
  --min-sessions-for-claim 10
```

Result:

| target | usable sessions | mean multi-split gain | mean permutation gain | decision |
| --- | ---: | ---: | ---: | --- |
| `go_response` | 10 | 0.034 | 0.056 | `inconclusive_mixed_evidence` |
| `response_made` | 12 | 0.003 | 0.036 | `negative_or_null_trend` |

Interpretation: `response_made` is useful as a control but should not replace
`go_response` as the primary target.

## Regional ablation screen

Command:

```bash
make allen-regional-ablation
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_regional_ablation.json
artifacts/reports/allen_targets/go_response_regional_ablation.csv
artifacts/reports/allen_targets/go_response_regional_ablation.md
```

Result for strict usable `go_response`:

| region | mean drop | positive drop fraction |
| --- | ---: | ---: |
| visual_cortex | 0.025 | 0.600 |
| visual_thalamus | 0.015 | 0.500 |
| arousal_midbrain | 0.004 | 0.200 |

Interpretation: visual cortex and visual thalamus are the leading predictive
regional hypotheses. This is feature ablation, not causal lesion evidence.

## Temporal-window screen

Commands:

```bash
make allen-temporal-reexport
make allen-temporal-windows
```

Artifacts:

```text
artifacts/reports/allen_targets/temporal_reexport_status.json
artifacts/reports/allen_targets/go_response_temporal_windows.json
artifacts/reports/allen_targets/go_response_temporal_windows.csv
artifacts/reports/allen_targets/go_response_temporal_windows.md
```

Result over 10 strict usable `go_response` sessions:

| window | mean gain | median gain | positive gain fraction | valid trial fraction |
| --- | ---: | ---: | ---: | ---: |
| decision | 0.186 | 0.166 | 0.900 | 1.000 |
| pre_response | 0.143 | 0.079 | 0.700 | 0.953 |
| baseline | 0.058 | 0.022 | 0.500 | 1.000 |
| stimulus | 0.056 | 0.029 | 0.600 | 1.000 |

Mean all-window gain: 0.219.

Interpretation: the strongest signal is post-stimulus/peri-response. The
dynamic `pre_response` control keeps substantial signal while reducing direct
motor contamination, but this remains predictive evidence only.

## Temporal permutation screen

Command:

```bash
make allen-temporal-permutation
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_permutation.json
artifacts/reports/allen_targets/go_response_pre_response_permutation.csv
artifacts/reports/allen_targets/go_response_pre_response_permutation.md
```

Result over 10 strict usable `go_response` sessions:

| metric | value |
| --- | ---: |
| permutations per session | 50 |
| mean observed gain | 0.143 |
| median observed gain | 0.079 |
| positive gain fraction | 0.700 |
| significant fraction | 0.500 |
| mean valid-trial fraction | 0.953 |

Significant sessions:

```text
1087992708
1091039902
1093864136
1096620314
1119946360
```

Interpretation: `pre_response` survives a shuffled temporal-window alignment
screen in 5/10 sessions. This justifies region-by-window analysis, but 50
permutations are screening-level only; a confirmatory run needs more
permutations.

Confirmatory command:

```bash
make allen-temporal-permutation-confirm
```

Confirmatory artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.json
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.csv
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.md
```

Confirmatory result over the same 10 strict usable sessions:

| metric | value |
| --- | ---: |
| permutations per session | 500 |
| mean observed gain | 0.143 |
| median observed gain | 0.079 |
| positive gain fraction | 0.700 |
| significant fraction | 0.500 |
| mean valid-trial fraction | 0.953 |

The five significant sessions remain the same, now with p = 0.002:

```text
1087992708
1091039902
1093864136
1096620314
1119946360
```

Interpretation: the temporal `pre_response` signal survives the stronger
permutation screen. It is still heterogeneous across sessions, so the correct
claim is "robust in a reproducible subset", not "universal across Allen
sessions".

## Temporal region-by-window ablation

Main command:

```bash
make allen-temporal-regional-ablation
```

Sensitivity command:

```bash
.venv/bin/python scripts/run_allen_temporal_regional_ablation.py \
  --target-name go_response \
  --window-name pre_response \
  --require-usable-target \
  --out-json artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.json \
  --out-csv artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.csv \
  --out-md artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.md
```

Main artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.json
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.csv
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.md
```

Main result over the 5 temporal-permutation-significant sessions:

| region | sessions | mean drop | positive drop fraction |
| --- | ---: | ---: | ---: |
| visual_cortex | 5 | 0.119 | 1.000 |
| basal_ganglia | 3 | 0.078 | 0.667 |
| arousal_midbrain | 5 | 0.024 | 0.400 |
| visual_thalamus | 5 | 0.008 | 0.400 |
| hippocampus | 5 | -0.000 | 0.200 |

Sensitivity over all 10 usable sessions:

| region | sessions | mean drop | positive drop fraction |
| --- | ---: | ---: | ---: |
| visual_cortex | 10 | 0.059 | 0.600 |
| basal_ganglia | 6 | 0.037 | 0.333 |
| arousal_midbrain | 10 | 0.008 | 0.200 |

Interpretation: visual cortex is the most stable pre-response regional
hypothesis. Basal ganglia is plausible but less stable because it appears in
fewer sessions. This is still predictive feature ablation, not causal evidence.

## Cross-session uncertainty

Command:

```bash
make allen-uncertainty
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_uncertainty.json
artifacts/reports/allen_targets/go_response_pre_response_uncertainty.md
```

Result:

| metric | cohort | mean | CI95 low | CI95 high | LOO min mean | LOO max mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| pre_response gain | all 10 usable | 0.143 | 0.047 | 0.243 | 0.119 | 0.164 |
| pre_response gain | 5 significant | 0.294 | 0.219 | 0.348 | 0.277 | 0.330 |
| visual_cortex drop | all 10 usable | 0.059 | 0.008 | 0.115 | 0.040 | 0.073 |
| visual_cortex drop | 5 significant | 0.119 | 0.046 | 0.191 | 0.091 | 0.146 |

Interpretation: the temporal `pre_response` gain and visual-cortex drop have
positive session-bootstrap CIs in both all-session and significant-session
summaries. Leave-one-session-out means remain positive, so neither result
collapses when any single session is removed. The limitation remains cohort
size, not single-session domination.

## Stabilized multi-layer system

Command:

```bash
make allen-stabilize
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_controls.json
artifacts/reports/allen_targets/go_response_pre_response_controls.md
artifacts/reports/allen_targets/go_response_pre_response_latency_strata.csv
artifacts/reports/allen_targets/go_response_pre_response_functional_graph.json
artifacts/reports/allen_targets/go_response_pre_response_functional_graph.md
artifacts/reports/allen_targets/go_response_pre_response_generative_surrogate.json
artifacts/reports/allen_targets/go_response_pre_response_generative_surrogate.md
artifacts/reports/allen_targets/go_response_scientific_agent.json
artifacts/reports/allen_targets/go_response_scientific_agent.md
artifacts/study_manifests/allen_go_response_pre_response.json
```

Response-control result:

| check | value |
| --- | ---: |
| `pre_response` vs baseline margin | 0.085 |
| `pre_response` vs stimulus margin | 0.087 |
| latency strata analyzed | 20 |
| fast-stratum mean gain | 0.121 |
| fast-stratum positive fraction | 0.300 |
| slow-stratum mean gain | 0.091 |
| slow-stratum positive fraction | 0.700 |

Interpretation: the candidate `pre_response` window passes the current negative
window-control gate, but latency stratification exposes heterogeneity. The slow
stratum is more consistent than the fast stratum. This supports continued
development, but it still limits mechanistic claims.

Functional graph:

| edge | weight | interpretation |
| --- | ---: | --- |
| `window:pre_response -> target:go_response` | 0.143 | predictive temporal relation |
| `region:visual_cortex -> window:pre_response` | 0.059 | strongest regional hypothesis |
| `region:basal_ganglia -> window:pre_response` | 0.037 | weaker secondary hypothesis |

The graph is empirical and predictive. It is not an anatomical connectome.

Generative surrogate:

| metric | value |
| --- | ---: |
| empirical temporal gain mean | 0.143 |
| generated temporal gain mean | 0.152 |
| generated sessions | 10 |

The surrogate is calibrated to session-level evidence summaries. It is useful
for stress-testing graph/agent workflows, not for replacing real-data evidence.

Scientific-agent audit:

```text
decision=advance_with_controls
n_findings=0
```

The deterministic audit rules find no current blocking issue, provided the
project keeps the claim at the level of controlled predictive evidence.

## Verification

Command:

```bash
.venv/bin/python scripts/verify.py
```

Current result:

```text
75 tests OK
```

## Current scientific decision

Do not claim causal regional necessity yet.

Current defensible claim: in the strict Allen `go_response` cohort, the
`pre_response` temporal window adds predictive signal beyond task/image/history
baselines, passes current negative window controls, and motivates graph-guided
regional hypotheses centered on visual cortex. Latency-stratified heterogeneity
prevents a stronger mechanistic claim.

Next required controls:

- stronger response-aligned controls with more permutations;
- deeper reaction-time and animal/session-quality stratification;
- broader-session validation or second-dataset replication;
- region-by-window uncertainty with larger session cohorts;
- dependency lockfile and dataset-version capture in the study manifest.
