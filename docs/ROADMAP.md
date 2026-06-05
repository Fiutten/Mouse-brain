# Roadmap

## Phase 0: Project hardening

Status: in progress.

Goals:

- local virtual environment;
- package metadata;
- test workflow;
- reproducible command set;
- basic documentation.
- local experiment registry.

Exit criteria:

- `make verify` or equivalent passes;
- demo produces lesion sensitivity output;
- project can be understood from README and architecture docs.
- registered run stores manifest, config snapshot and report.

## Phase 1: Real data ingestion

Target dataset:

- Allen Visual Behavior Neuropixels.

Secondary dataset:

- IBL brain-wide decision-making.

Deliverables:

- data loader interface;
- session metadata model;
- spike/event extraction;
- region mapping;
- train/test split protocol.

Exit criteria:

- load at least one public session;
- extract stimulus, action, timing and region-level neural features;
- run a trivial baseline.

Current status:

- Session interface exists.
- Synthetic Neuropixels-like fixture exists.
- Behavioral baseline interface exists.
- Allen and IBL adapter contracts exist.
- Real Allen/IBL loader not yet implemented.

## Phase 2: Baselines

Baselines:

- majority/action-prior baseline;
- logistic regression on stimulus/task variables;
- simple temporal state model;
- non-biological recurrent baseline.

Exit criteria:

- baseline report with metrics;
- leakage checks;
- stable splits across sessions/animals.

## Phase 3: Regional Level-0 model on real data

Deliverables:

- trainable regional model;
- neural + behavioral objective;
- lesion sweep on trained model;
- ablations against non-regional model.

Exit criteria:

- regional structure improves at least one defensible axis: generalization, interpretability or contrafactual coherence.

## Phase 4: Knowledge-guided workflow

Deliverables:

- curated paper matrix;
- structured evidence graph;
- hypothesis registry;
- reviewer agent checks;
- experiment audit trail.

Exit criteria:

- every lesion experiment maps to evidence and expected deficit;
- reviewer agent blocks unsupported claims.

## Phase 5: Selective biological detail

Possible additions:

- E/I population split;
- region-specific gain;
- thalamocortical microcircuit;
- basal-ganglia action selection module.

Exit criteria:

- added detail improves a metric or explains an observed failure.

## Phase 6: Publication package

Deliverables:

- reproducible code;
- dataset protocol;
- figures;
- ablation tables;
- limitations section;
- preprint draft.
