# Allen real-data audit and benchmark

## Scope

This report documents the current real-data validation pass for normalized Allen
Visual Behavior Neuropixels sessions.

Current normalized sessions:

```text
1053709239
1064415305
1065449881
1087720624
1087992708
1090800639
1090803859
1091039902
1092283837
1093638203
1093864136
1096620314
1098119201
1111013640
1119946360
```

Generated reports:

```text
artifacts/reports/allen/<session_id>/audit.json
artifacts/reports/allen/<session_id>/benchmark.json
artifacts/reports/allen/<session_id>/multisplit.json
artifacts/reports/allen/<session_id>/permutation.json
artifacts/reports/allen/multisession_summary.json
artifacts/reports/allen/evidence_report.json
artifacts/reports/allen/target_diagnostics.json
artifacts/reports/allen_targets/go_response_usable/multisession_summary.json
artifacts/reports/allen_targets/go_response_usable/evidence_report.json
artifacts/reports/allen_targets/target_evidence_status.json
artifacts/reports/allen_targets/go_response_session_relations.json
artifacts/reports/allen_targets/go_response_session_relations.csv
artifacts/reports/allen_targets/go_response_session_relations.md
artifacts/reports/allen_targets/go_response_regional_ablation.json
artifacts/reports/allen_targets/go_response_regional_ablation.csv
artifacts/reports/allen_targets/go_response_regional_ablation.md
artifacts/reports/allen_targets/response_made_usable/multisession_summary.json
artifacts/reports/allen_targets/response_made_usable/evidence_report.json
artifacts/reports/allen_targets/response_made_regional_ablation.json
artifacts/reports/allen_targets/response_made_regional_ablation.csv
artifacts/reports/allen_targets/response_made_regional_ablation.md
artifacts/reports/allen_targets/temporal_reexport_status.json
artifacts/reports/allen_targets/go_response_temporal_windows.json
artifacts/reports/allen_targets/go_response_temporal_windows.csv
artifacts/reports/allen_targets/go_response_temporal_windows.md
artifacts/reports/allen_targets/go_response_pre_response_permutation.json
artifacts/reports/allen_targets/go_response_pre_response_permutation.csv
artifacts/reports/allen_targets/go_response_pre_response_permutation.md
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.json
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.csv
artifacts/reports/allen_targets/go_response_pre_response_permutation_500.md
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.json
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.csv
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation.md
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.json
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.csv
artifacts/reports/allen_targets/go_response_pre_response_regional_ablation_all_sessions.md
artifacts/reports/allen_targets/go_response_pre_response_uncertainty.json
artifacts/reports/allen_targets/go_response_pre_response_uncertainty.md
```

## What was implemented

- Dataset audit module: `neurotwin_mvp/audit.py`.
- Benchmark module: `neurotwin_mvp/benchmark.py`.
- Evidence synthesis module: `neurotwin_mvp/evidence.py`.
- Behavioral-target diagnostics module: `neurotwin_mvp/behavioral_targets.py`.
- Target-aware export orchestrator: `scripts/export_until_target_evidence.py`.
- CLI scripts for audit, benchmark, multi-split reports, permutation tests,
  evidence synthesis, target diagnostics and Allen batch export.
- Tests for audit, benchmark, multi-split, permutation-test, evidence-synthesis,
  behavioral-target behavior and target-driven export orchestration.

The benchmark uses chronological splits and reports balanced accuracy because
the Allen behavioral labels are often imbalanced.

## Current whole-cohort status

The broad Allen cohort currently contains 15 normalized sessions. The generic
all-valid-trials benchmark is useful as a control, but it is not the main
publication target because it mixes behavioral regimes and target definitions.

Whole-cohort evidence:

| statistic | value |
| --- | ---: |
| sessions | 15 |
| total valid trials | 4005 |
| mean multi-split neural gain | 0.008 |
| mean permutation observed gain | 0.031 |
| formal decision | negative_or_null_trend |

Critical interpretation: the whole-cohort result does not support a positive
global neural-contribution claim. It is mainly a diagnostic view.

## Behavioral-target redesign

The original binary `choice` target is retained as a historical benchmark, but
it is no longer treated as the only scientifically meaningful target. Allen
Visual Behavior is not a clean balanced two-choice task; therefore target choice
must be diagnosed before adding biological complexity.

Current target diagnostics over 15 normalized sessions:

| target | usable sessions | labeled trials | interpretation |
| --- | ---: | ---: | --- |
| `choice` | 12/15 | 4005 | useful continuity baseline |
| `go_response` | 10/15 | 3507 | primary task-native target candidate |
| `catch_response` | 0/15 | 498 | scientifically interesting but underpowered |
| `rewarded` | 12/15 | 4005 | useful control, partly outcome-derived |
| `response_made` | 12/15 | 4005 | stronger coverage, weaker neural evidence in screening |
| `task_success` | 10/15 | 4005 | correctness target; useful but outcome-confounded |

The strict `go_response` usable-session cohort is the strongest current signal.
It uses only sessions that pass the target usability filter and was rebuilt with
500 neural-label permutations per session.

| statistic | value |
| --- | ---: |
| sessions | 10 |
| labeled go trials used in strict evidence | 2332 |
| labeled go trials across all normalized sessions | 3507 |
| mean multi-split gain | 0.034 |
| mean multi-split gain CI95 | [0.012, 0.060] |
| mean permutation observed gain | 0.056 |
| mean permutation gain CI95 | [0.004, 0.110] |
| positive multi-split fraction | 0.700 |
| significant permutation fraction | 0.300 |
| formal decision | inconclusive_mixed_evidence |

## Critical interpretation

The current result is real but not yet publication-grade positive evidence.

Positive signs:

- The target-driven export reached the pre-set threshold of 10 usable
  `go_response` sessions.
- Aggregate multi-split and permutation gain confidence intervals are positive
  in the strict usable-session cohort.
- Three sessions show significant permutation evidence at 500-permutation
  resolution.

Blocking scientific limitations:

- Only 3/10 usable sessions reject the shuffled-neural null.
- Several sessions still carry quality flags, including low trial count,
  non-positive permutation gain or response-time extraction warnings.
- `go_response` labels are stimulus-sign degenerate, so stimulus-rule baselines
  are not meaningful for this target; interpretation must be framed as neural
  contribution beyond behavioral baselines, not as a full task model.
- The evidence synthesizer deliberately returns `inconclusive_mixed_evidence`,
  so the current state cannot support a strong positive claim.

## Session relationship analysis

The current relation report is generated by:

```bash
make allen-session-relations
```

It joins target diagnostics, normalized session artifacts, export metadata and
the strict `go_response` evidence report. Its purpose is to explain why some
downloaded sessions entered the strict cohort and others did not, and why only
some usable sessions produced significant permutation evidence.

Current findings:

- 15 downloaded/normalized sessions were analyzed.
- 10 sessions are usable for the strict `go_response` target.
- 5 sessions are not usable for `go_response`.
- All 5 non-usable sessions fail because the `go_response` labels are
  imbalanced and the minority class is below 0.20.
- 3/10 usable sessions are permutation-significant at alpha 0.05.

Interpretation: the first failure mode is behavioral-target viability, not
download failure or benchmark execution failure. Sessions with very high hit
rates contain too few misses to support a balanced hit-versus-miss target. Among
the usable sessions, evidence remains heterogeneous; therefore the correct
scientific next step is stratification and target redesign, not a strong
positive neural-contribution claim.

The descriptive correlations in the strict 10-session cohort are hypothesis
generators only. With this sample size they must not be treated as causal
evidence or as stable selection rules.

## Target redesign screening

Two additional task-native candidates were added:

- `response_made`: hit or false alarm versus miss or correct reject.
- `task_success`: hit or correct reject versus miss or false alarm.

`response_made` improves target viability to 12/15 sessions, but the exploratory
50-permutation evidence screen is weaker than `go_response`:

| target | usable sessions | mean multi-split gain | mean permutation gain | significant permutation fraction | decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `go_response` | 10 | 0.034 | 0.056 | 0.300 | `inconclusive_mixed_evidence` |
| `response_made` | 12 | 0.003 | 0.036 | 0.583 | `negative_or_null_trend` |

Interpretation: `response_made` is a useful control target because it covers
more sessions and uses both go/catch outcomes, but it should not replace
`go_response` as the primary signal target unless stronger confirmatory runs
contradict the current screen.

## Regional ablation screening

Regional ablation currently means leave-one-region-out feature ablation, not a
biological lesion. It estimates whether each coarse region's spike-rate feature
adds predictive signal beyond task, image and behavioral-history covariates.

For strict usable `go_response`, the full regional model has mean neural gain
0.056. The largest mean drops when removing a region are:

| region | mean drop | positive drop fraction |
| --- | ---: | ---: |
| visual_cortex | 0.025 | 0.600 |
| visual_thalamus | 0.015 | 0.500 |
| arousal_midbrain | 0.004 | 0.200 |

For usable `response_made`, the full regional model has mean neural gain 0.036.
The ranking remains visually dominated:

| region | mean drop | positive drop fraction |
| --- | ---: | ---: |
| visual_cortex | 0.022 | 0.750 |
| visual_thalamus | 0.008 | 0.667 |
| arousal_midbrain | 0.006 | 0.417 |

This supports visual cortex and visual thalamus as the first regional
hypotheses to investigate with stronger temporal features and stricter controls.
It does not yet support causal lesion language.

## Temporal-window screening

The Allen normalizer now exports three region-rate windows per trial:

- `baseline`: -0.250 to 0.000 s relative to change/stimulus time.
- `stimulus`: 0.000 to 0.250 s.
- `decision`: 0.250 to 0.750 s.
- `pre_response`: starts at 0.250 s and is dynamically truncated 0.050 s
  before response time when a response exists.

The original `Trial.region_rates` field remains the stimulus-window rate for
backward compatibility. The full temporal features are stored in
`trial.metadata["region_rates_by_window"]`.

The 10 strict usable `go_response` sessions were re-exported with temporal
metadata and screened with a temporal-window benchmark. Each window is compared
against the same task/image/history baseline.

| window | mean gain | median gain | positive gain fraction |
| --- | ---: | ---: | ---: |
| `decision` | 0.186 | 0.166 | 0.900 |
| `pre_response` | 0.143 | 0.079 | 0.700 |
| `baseline` | 0.058 | 0.022 | 0.500 |
| `stimulus` | 0.056 | 0.029 | 0.600 |
| all windows | 0.219 |  |  |

Interpretation: the first temporal screen strongly prioritizes the post-stimulus
decision/peri-response window. This is promising, but it is also the window most
likely to contain response/motor activity. It should be treated as a
peri-response predictivity result. The dynamic `pre_response` control keeps a
substantial signal with mean gain 0.143 and mean valid-trial coverage 0.953,
which weakens but does not eliminate the motor-contamination concern.

## Temporal permutation and region-by-window screen

The `pre_response` window was tested against a shuffled temporal-window null.
The null keeps task/image/history features fixed and shuffles `pre_response`
neural rows across trials. A screening run with 50 permutations was followed by
a 500-permutation confirmatory run.

| metric | value |
| --- | ---: |
| sessions | 10 |
| permutations per session | 500 |
| mean observed gain | 0.143 |
| median observed gain | 0.079 |
| positive gain fraction | 0.700 |
| significant session fraction | 0.500 |
| mean valid-trial fraction | 0.953 |

The five significant sessions remain significant at the 500-permutation
resolution, with p = 0.002. This supports a robust temporal signal in a
reproducible subset, not a universal session-level effect.

Region-by-window ablation was then run for `pre_response`. The main
interpretation uses only the 5 sessions that reject the shuffled temporal-window
null:

| region | sessions | mean drop | positive drop fraction |
| --- | ---: | ---: | ---: |
| visual_cortex | 5 | 0.119 | 1.000 |
| basal_ganglia | 3 | 0.078 | 0.667 |
| arousal_midbrain | 5 | 0.024 | 0.400 |
| visual_thalamus | 5 | 0.008 | 0.400 |
| hippocampus | 5 | -0.000 | 0.200 |

Sensitivity over all 10 usable sessions preserves visual cortex as the leading
region but with weaker effect:

| region | sessions | mean drop | positive drop fraction |
| --- | ---: | ---: | ---: |
| visual_cortex | 10 | 0.059 | 0.600 |
| basal_ganglia | 6 | 0.037 | 0.333 |
| arousal_midbrain | 10 | 0.008 | 0.200 |

Interpretation: the most defensible current regional hypothesis is that
visual-cortex activity in the pre-response window carries task-relevant
predictive signal. Basal-ganglia results are interesting but weaker because
coverage is available in fewer sessions. This remains predictive feature
evidence, not causal lesion evidence.

Cross-session uncertainty was then estimated with 5000 session-bootstrap
resamples and leave-one-session-out sensitivity:

| metric | cohort | mean | CI95 low | CI95 high | LOO min mean | LOO max mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `pre_response` gain | all 10 usable | 0.143 | 0.047 | 0.243 | 0.119 | 0.164 |
| `pre_response` gain | 5 significant | 0.294 | 0.219 | 0.348 | 0.277 | 0.330 |
| visual-cortex drop | all 10 usable | 0.059 | 0.008 | 0.115 | 0.040 | 0.073 |
| visual-cortex drop | 5 significant | 0.119 | 0.046 | 0.191 | 0.091 | 0.146 |

Interpretation: the current effect is not dominated by a single session. The
main limitation is small cohort size and dataset/task specificity, not a single
outlier driving the mean.

## Stabilized control, graph and surrogate layers

The current integrated reconstruction command is:

```bash
make allen-stabilize
```

Response-window controls compare the `pre_response` candidate with negative
windows from the temporal benchmark:

| check | margin |
| --- | ---: |
| `pre_response` over baseline | 0.085 |
| `pre_response` over stimulus | 0.087 |

The current gate decision is `passes_window_controls`.

Latency-stratified controls remain mixed:

| stratum | sessions | mean gain | positive fraction | significant fraction |
| --- | ---: | ---: | ---: | ---: |
| fast | 10 | 0.121 | 0.300 | 0.300 |
| slow | 10 | 0.091 | 0.700 | 0.600 |

Interpretation: the temporal effect is not simply weaker than baseline or
stimulus controls, but it is heterogeneous across response-latency strata. This
is a serious limitation for mechanistic language.

The empirical functional graph currently contains these weighted predictive
edges:

| source | relation | target | weight |
| --- | --- | --- | ---: |
| `window:pre_response` | predicts | `target:go_response` | 0.143 |
| `region:visual_cortex` | contributes_to | `window:pre_response` | 0.059 |
| `region:basal_ganglia` | contributes_to | `window:pre_response` | 0.037 |

The graph is a hypothesis-organization layer. It is not an anatomical
connectome.

The calibrated generative surrogate produces session-level synthetic evidence
with generated mean temporal gain 0.152 against empirical mean 0.143. This
validates software integration, not biology.

The deterministic scientific-agent audit currently returns
`advance_with_controls` with no blocking findings. This means the project can
add abstraction layers while keeping the claim at controlled predictive
evidence.

## Decision

Do not claim causal neural mechanism yet.

Proceed with:

- increase latency/control permutations and add animal/session-quality
  stratification;
- expand or replicate the cohort before making strong general claims;
- use the functional graph to prioritize region-window hypotheses;
- use the generative surrogate and deterministic agent to stress-test the
  system architecture;
- continue requiring permutation tests, CIs and explicit control gates before
  biological-layer expansion.
