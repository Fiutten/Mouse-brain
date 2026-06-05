# Experiment trace

This document tracks the real-data tests performed so far, their commands,
artifacts and scientific interpretation. It is intentionally conservative:
engineering success, exploratory signal and publishable evidence are kept
separate.

## Current dataset state

- Dataset: Allen Visual Behavior Neuropixels.
- Normalized sessions: 39.
- Strict primary target: `go_response`.
- Strict usable `go_response` sessions: 24/39.
- Non-usable `go_response` sessions: 15/39, all due to class imbalance.
- Latest broad evidence decision: `inconclusive_mixed_evidence`.
- Raw Allen cache size at latest checkpoint: 119 GB.
- Free disk at latest checkpoint: 635 GiB.

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
| `go_response` | 24/39 | 9422 | primary signal target |
| `response_made` | 33/39 | 10773 | broader control |
| `task_success` | 25/39 | 10773 | correctness control, outcome-confounded |
| `choice` | 33/39 | 10773 | continuity baseline |
| `rewarded` | 34/39 | 10773 | outcome-derived control |
| `catch_response` | 0/39 | 1351 | underpowered/imbalanced |

Interpretation: target viability, not download failure, explains why some
sessions are excluded from the strict `go_response` cohort.

## 50-usable-session expansion checkpoint

Command:

```bash
.venv/bin/python scripts/export_until_target_evidence.py \
  --target-name go_response \
  --target-usable-sessions 50 \
  --max-new-sessions 63 \
  --candidate-limit 80 \
  --screening-permutations 20 \
  --final-permutations 200 \
  --min-free-gb 120
```

Supporting verification:

```bash
.venv/bin/python scripts/analyze_allen_session_relations.py --target-name go_response
.venv/bin/python -m unittest discover -s tests
df -h .
du -sh data/allen artifacts/datasets/allen artifacts/reports
```

Artifacts:

```text
artifacts/reports/allen/target_diagnostics.json
artifacts/reports/allen/evidence_report.json
artifacts/reports/allen/export_batch_status.json
artifacts/reports/allen_targets/go_response_session_relations.json
artifacts/reports/allen_targets/go_response_session_relations.csv
artifacts/reports/allen_targets/go_response_session_relations.md
```

Result:

| metric | value |
| --- | ---: |
| normalized sessions | 39 |
| usable `go_response` sessions | 24 |
| non-usable `go_response` sessions | 15 |
| `go_response` labeled trials | 9422 |
| permutation-significant sessions in strict relation report | 3 |
| broad mean multi-split gain | 0.022 |
| broad mean permutation gain | 0.030 |
| broad evidence decision | `inconclusive_mixed_evidence` |
| raw Allen cache | 119 GB |
| normalized Allen artifacts | 23 MB |
| free disk | 635 GiB |
| unit tests | 83/83 OK |

The run was stopped at a safe checkpoint after a new pending session,
`1048196054`, had started downloading. That partial NWB is resumable because
the downloader uses `curl -C -`; the partial size recorded by the batch status
was 399892480 bytes.

Interpretation: the expansion did not fail technically. The limiting factor is
target viability: all 15 non-usable `go_response` sessions are rejected because
the minority class falls below 0.20. Several sessions are valid Allen sessions
and usable for broader controls such as `choice`, `response_made` or `rewarded`,
but not defensible for a balanced hit-versus-miss `go_response` analysis.

Scientific consequence: reaching 50 usable `go_response` sessions likely
requires downloading substantially more than 50 NWB files. The next expansion
should be metadata- and behavior-aware, prioritizing candidates likely to have
balanced go hit/miss labels instead of blindly following the broad metadata
ranking.

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

Latest relation checkpoint:

- 39 sessions analyzed.
- 24 usable `go_response` sessions.
- 15 non-usable `go_response` sessions.
- 15/15 non-usable sessions fail due to `go_response` class imbalance below
  minority fraction 0.20.
- 3 sessions in the strict evidence cohort are permutation-significant.

Interpretation: the same failure mode persists at larger scale. This strengthens
the argument that we need target-aware candidate selection and stratification,
not just more downloads.

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

## Advanced evidence layer

Command:

```bash
make allen-advanced-evidence
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_pre_response_stability_matrix.json
artifacts/reports/allen_targets/go_response_pre_response_stability_matrix.md
artifacts/reports/allen_targets/go_response_latent_temporal_baseline.json
artifacts/reports/allen_targets/go_response_latent_temporal_baseline.md
artifacts/reports/allen_targets/go_response_pre_response_graph_evidence_registry.json
artifacts/reports/allen_targets/go_response_pre_response_graph_evidence_registry.md
artifacts/reports/allen_targets/go_response_session_generator_v2.json
artifacts/reports/allen_targets/go_response_session_generator_v2.md
artifacts/reports/allen_targets/go_response_advanced_scientific_agent.json
artifacts/reports/allen_targets/go_response_advanced_scientific_agent.md
```

Stability matrix:

| metric | value |
| --- | ---: |
| sessions | 10 |
| mean stability score | 0.560 |
| robust sessions | 4 |
| mixed sessions | 3 |
| fragile sessions | 3 |

Robust sessions: `1091039902`, `1093864136`, `1096620314`,
`1119946360`.

Interpretation: the aggregate effect is not uniform. Four sessions support a
stronger follow-up, three are mixed, and three are fragile. Future mechanistic
work should focus first on robust and mixed sessions, while fragile sessions
should be treated as failure cases to explain.

Latent temporal baseline:

| metric | value |
| --- | ---: |
| sessions | 10 |
| mean latent gain | -0.107 |
| positive gain fraction | 0.200 |
| mean explained variance fraction | 0.857 |

Interpretation: a simple PCA latent representation reconstructs much of the
temporal feature variance but usually does not improve behavior prediction over
the compact behavioral baseline. This argues against jumping directly to
heavier representation-learning claims. The next latent step should diagnose
why only sessions `1093864136` and `1096620314` show positive latent gain.

Graph evidence registry:

| edge class | count |
| --- | ---: |
| controlled | 3 |
| exploratory | 0 |
| fragile | 0 |

Controlled edges:

- `window:pre_response -> target:go_response`;
- `region:visual_cortex -> window:pre_response`;
- `region:basal_ganglia -> window:pre_response`.

These edges are eligible for follow-up, not causal conclusions.

Session generator v2:

| metric | value |
| --- | ---: |
| generated trials | 500 |
| positive rate | 0.654 |
| latency mean ms | 508.404 |
| latency std ms | 499.858 |
| regions | 5 |
| windows | 3 |

The generator now produces normalized trial-level sessions with temporal
region-window metadata. It is for stress-testing pipelines and ablation logic,
not for empirical claims.

Advanced scientific-agent audit:

```text
decision=advance_to_microcircuit_design
n_findings=1
```

Finding: the latent temporal baseline is not consistently useful
(`positive_gain_fraction=0.200`). This is a moderate, not blocking, issue for
microcircuit design because the graph/control evidence remains positive. It is
blocking for any strong claim about latent representations.

## Selected microcircuit layer

Command:

```bash
make allen-selected-microcircuit
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_selected_microcircuit.json
artifacts/reports/allen_targets/go_response_selected_microcircuit.md
```

Calibration:

| quantity | value |
| --- | ---: |
| robust sessions | 4 |
| temporal gain | 0.143 |
| visual-cortex drop | 0.059 |
| basal-ganglia drop | 0.037 |
| intact mean action probability | 0.590 |

Perturbations:

| perturbation | mean action probability | drop from intact |
| --- | ---: | ---: |
| visual excitation | 0.569 | 0.020 |
| visual inhibition | 0.593 | -0.003 |
| basal gate | 0.581 | 0.009 |

Interpretation: the selected microcircuit reproduces the expected direction for
visual excitation and basal-ganglia gating, but effects are modest. Visual
inhibition slightly increases the action probability when suppressed, which is
directionally coherent. This is a mechanistic scaffold for hypothesis
prioritization, not causal biological evidence.

## Microcircuit external validation

Command:

```bash
make allen-microcircuit-validation
```

Artifacts:

```text
artifacts/reports/allen_targets/go_response_microcircuit_validation.json
artifacts/reports/allen_targets/go_response_microcircuit_validation.csv
artifacts/reports/allen_targets/go_response_microcircuit_validation.md
```

Result over the 10 strict usable `go_response` sessions:

| metric | value |
| --- | ---: |
| decision | `weak_partial_robust_fragile_alignment` |
| probability/stability correlation | 0.641 |
| robust minus fragile probability | 0.009 |
| robust minus mixed probability | 0.006 |

Robustness controls with 1000 bootstrap resamples and 1000 label-permutation
nulls:

| metric | estimate | ci95 low | ci95 high | null p-value |
| --- | ---: | ---: | ---: | ---: |
| robust minus fragile probability | 0.010 | 0.002 | 0.016 | 0.014 |
| probability/stability correlation | 0.644 | 0.193 | 0.937 | 0.021 |

Group means:

| status | mean action probability | mean stability score |
| --- | ---: | ---: |
| fragile | 0.573 | 0.133 |
| mixed | 0.577 | 0.467 |
| robust | 0.583 | 0.950 |

Interpretation: the fixed robust-calibrated microcircuit tracks the stability
ordering in the expected direction and shows a moderate positive correlation
with the stability score. Bootstrap intervals do not cross zero and
label-permutation controls are positive at alpha 0.05. However, the absolute
separation in predicted action probability remains small. This supports using
the microcircuit as a statistically non-trivial hypothesis prioritizer, but it
is still not strong enough to claim a validated mechanistic model or a
publishable biological mechanism.

## Verification

Command:

```bash
.venv/bin/python scripts/verify.py
```

Current result:

```text
83 tests OK
```

## Current scientific decision

Do not claim causal regional necessity yet.

Current defensible claim: in the strict Allen `go_response` cohort, the
`pre_response` temporal window adds predictive signal beyond task/image/history
baselines, passes current negative window controls, and motivates graph-guided
regional hypotheses centered on visual cortex. The advanced stability matrix
identifies four robust sessions, but latency/session heterogeneity and the weak
PCA latent baseline prevent a strong representation-learning claim. The first
selected microcircuit provides a focused mechanistic scaffold. Its external
validation is directionally aligned with session stability and passes current
bootstrap/permutation robustness checks, but the probability separation is weak;
it must therefore be treated as a statistically supported hypothesis generator
that requires larger cohorts, second-dataset replication or perturbation
evidence before any mechanistic claim.

Next required controls:

- stronger response-aligned controls with more permutations;
- deeper reaction-time and animal/session-quality stratification;
- broader-session validation or second-dataset replication;
- region-by-window uncertainty with larger session cohorts;
- failure analysis of fragile sessions and latent-negative sessions;
- dependency lockfile and dataset-version capture in the study manifest.
