# Experiment management

## Purpose

The project must preserve reproducibility from the beginning. Every meaningful
run should be traceable to:

- code version;
- configuration;
- seed;
- data source;
- metrics;
- lesion results;
- hypothesis/reviewer output.

The current registry is intentionally local and dependency-free.

## Directory policy

### `configs/`

Versioned experiment/model configuration.

### `data/`

Local dataset caches. These files are not versioned.

- `data/allen/`: AllenSDK / Visual Behavior Neuropixels cache.
- `data/ibl/`: IBL ONE/OpenAlyx cache.

### `artifacts/experiments/`

Registered workflow runs. These are not versioned by default because they can
grow quickly and may include dataset-derived outputs.

Each run contains:

- `manifest.json`: run metadata;
- `report.json`: workflow output;
- `config_snapshot.json`: exact config used.

### `artifacts/reports/`

Generated reports, figures and paper-facing summaries.

Current Allen real-data reports:

```text
artifacts/reports/allen/<session_id>/audit.json
artifacts/reports/allen/<session_id>/benchmark.json
artifacts/reports/allen/<session_id>/multisplit.json
artifacts/reports/allen/<session_id>/permutation.json
artifacts/reports/allen/multisession_summary.json
artifacts/reports/allen/evidence_report.json
artifacts/reports/allen/target_diagnostics.json
artifacts/reports/allen/export_batch_status.json
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
artifacts/reports/allen_targets/go_response_pre_response_controls.json
artifacts/reports/allen_targets/go_response_pre_response_controls.md
artifacts/reports/allen_targets/go_response_pre_response_latency_strata.csv
artifacts/reports/allen_targets/go_response_pre_response_functional_graph.json
artifacts/reports/allen_targets/go_response_pre_response_functional_graph.md
artifacts/reports/allen_targets/go_response_pre_response_generative_surrogate.json
artifacts/reports/allen_targets/go_response_pre_response_generative_surrogate.md
artifacts/reports/allen_targets/go_response_scientific_agent.json
artifacts/reports/allen_targets/go_response_scientific_agent.md
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
artifacts/study_manifests/allen_go_response_pre_response.json
```

Current normalized Allen sessions:

```text
Current checkpoint: 39 normalized sessions as of 2026-06-05.
The complete machine-readable list is in
artifacts/reports/allen/target_diagnostics.json and the human-readable
usable/non-usable explanation is in
artifacts/reports/allen_targets/go_response_session_relations.md.

Initial 15-session checkpoint:
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

## Register a run

```bash
make register
```

Equivalent:

```bash
.venv/bin/python scripts/run_registered_experiment.py
```

## Current registry limits

The registry does not yet store:

- git commit hash;
- dependency lockfile;
- real dataset version;
- execution duration;
- figures;
- trained model weights.

These should be added before manuscript-grade experiments.

## Current Allen stabilization pipeline

Run:

```bash
make allen-stabilize
```

This target rebuilds the current reproducible evidence layer:

- cross-session uncertainty;
- response-window and latency-stratified controls;
- empirical functional graph;
- calibrated generative surrogate;
- deterministic scientific-agent audit;
- study manifest with artifact hashes;
- unit tests.

The command intentionally consumes normalized artifacts in
`artifacts/datasets/allen` and does not require AllenSDK/NWB access.

Run the advanced evidence layer:

```bash
make allen-advanced-evidence
```

This target adds:

- session x control stability matrix;
- PCA temporal latent baseline;
- graph-edge evidence registry;
- calibrated normalized session generator v2;
- advanced deterministic audit.

The current advanced audit allows focused microcircuit design but blocks strong
latent-representation claims because the PCA latent baseline has negative mean
gain and only 0.200 positive-gain fraction.

## Required rules

Do not use an unregistered run for scientific interpretation once real data are
integrated.

Keep `docs/EXPERIMENT_TRACE.md` updated after every meaningful real-data test.
It is the project-level audit trail for commands, artifacts, results and
scientific interpretation.

For large Allen expansion runs, always record:

- target threshold and candidate limit;
- `--min-free-gb` value;
- raw `data/allen` disk usage;
- normalized artifact disk usage;
- free disk after checkpoint;
- partial NWB session id and byte count if the run is paused.

Do not interpret raw accuracy on imbalanced real-data behavioral labels without
balanced accuracy or an equivalent imbalance-aware metric.

Do not interpret high-dimensional image/task models on a single session as
confirmatory evidence. If the number of learned features is large relative to
training trials, treat the result as exploratory until validated across sessions
or by permutation/confidence-interval analysis.

Do not make a positive neural-contribution claim unless the relevant
target-specific evidence report returns `positive_evidence`. The broad
`artifacts/reports/allen/evidence_report.json` is a diagnostic control; for the
current primary candidate, use:

```text
artifacts/reports/allen_targets/go_response_usable/evidence_report.json
```

Current decision labels such as `negative_or_null_trend` or
`inconclusive_mixed_evidence` mean the correct action is more validation or
target/feature redesign, not biological-layer expansion.

Do not promote a behavioral target into the main benchmark unless
`artifacts/reports/allen/target_diagnostics.json` shows enough labeled trials
and acceptable class balance across multiple sessions. At the current
15-session stage, `go_response` is the first serious task-native candidate,
`response_made` is a broader action/no-action control, `choice` is a continuity
baseline, `rewarded` and `task_success` are outcome-related controls, and
`catch_response` is underpowered.

For target-specific reports, keep all-labeled and usable-only cohorts separate.
The strict usable-session `go_response` cohort currently has the strongest
signal, but it remains `inconclusive_mixed_evidence` because the effect is not
consistent enough across sessions.

When a downloaded session does not enter a strict target cohort, check the
session-relation report before interpreting the failure. For the current
`go_response` cohort, the non-usable sessions failed because hit/miss labels are
too imbalanced, not because the Allen export or neural benchmark failed.

```bash
make allen-session-relations
```

Use the generated markdown for reviewer-facing interpretation and the CSV/JSON
outputs for stratification or candidate-selection scripts.

Regional ablations are feature ablations, not biological lesions. They are
allowed for hypothesis prioritization only:

```bash
make allen-regional-ablation
```

Do not describe a region as causally necessary unless the result survives
target-specific evidence checks, temporal controls and an empirical
perturbation/literature link.

Temporal-window benchmarks require artifacts with
`trial.metadata["region_rates_by_window"]`. Re-export cached Allen sessions
before running them:

```bash
make allen-temporal-reexport
make allen-temporal-windows
```

The default decision window is post-stimulus and may include response/motor
activity. Treat it as peri-response predictivity until pre-response and
response-aligned controls are added.

The current `pre_response` candidate passes negative window controls against
baseline and stimulus windows, but latency-stratified checks show heterogeneity.
Treat this as controlled predictive evidence, not mechanism.

The functional graph and generative surrogate are allowed only as design and
stress-test layers. They must not be cited as anatomical connectivity, causal
lesion evidence or independent empirical validation.

## Allen metadata smoke test

Run:

```bash
make allen-smoke
```

This test should only load project metadata. It must not call
`get_ecephys_session(...)`, because that downloads full NWB files that can be
several GB per session.

If AllenSDK is blocked by Python/dependency compatibility, run the direct S3
metadata fallback:

```bash
make allen-smoke-s3
```

The direct S3 backend downloads only `project_metadata/ecephys_sessions.csv`
from the public Allen S3 bucket.
