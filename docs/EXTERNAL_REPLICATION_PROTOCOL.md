# Frozen external replication protocol

## Status

Protocol prepared; external replication not executed.

The current IBL adapter does not normalize real sessions and no normalized IBL
sessions exist locally. This document freezes the intended replication logic
before external neural outcomes are inspected.

An isolated `.venv-ibl` creation was attempted on 2026-06-06 and failed during
Conda verification because the local Python/setuptools package cache was
corrupted. The Allen environment was deliberately not reused or modified.

## Replication type

An exact replication of Allen `go_response` is not appropriate in IBL because
the tasks and target definitions differ. The external study will be a
**conceptual replication** of response-independent pre-action neural
predictivity.

## Primary external question

Do fixed neural features measured before movement add held-out information
about the animal's subsequent action beyond task variables, behavioral history
and directly observed state?

## Required IBL target and landmarks

- Primary target: left versus right choice on valid choice trials.
- Movement alignment: use observed first-movement onset only to exclude trials
  whose movement has already begun; never use future movement time to define a
  neural feature window.
- Primary landmark: a fixed stimulus-aligned horizon selected before inspecting
  neural prediction results.
- Direct state adjustment: running/wheel state and other available movement or
  arousal covariates measured no later than the landmark.

The IBL target is not equivalent to Allen hit versus miss. Results must be
reported as conceptual generalization, not target replication.

## Frozen model comparison

1. Task/history baseline.
2. Task/history plus direct state.
3. Task/history plus direct state plus fixed neural features.

Primary metric:

- held-out balanced accuracy gain of model 3 over model 2.

Required validation:

- chronological blocked splits within session;
- leave-one-animal-out prediction;
- animal-cluster bootstrap interval;
- session-level shuffled-alignment null;
- Benjamini-Hochberg correction across prespecified session tests.

## Success criterion

External support requires:

- positive animal-cluster bootstrap lower bound for state-adjusted neural gain;
- positive gain in at least half of animals;
- no dependence on a single animal;
- transparent reporting of sessions that fail target or quality gates.

Failure to meet these criteria is a negative replication and must remain in the
study record.

## Required implementation before execution

1. Install and pin ONE-api in an isolated environment.
2. Implement ONE-to-`Session` normalization with tests.
3. Select sessions using behavioral/anatomical criteria only.
4. Freeze the landmark and feature mapping.
5. Register a replication manifest before running neural prediction.

The first item is currently blocked until the local Conda package cache or
Miniforge installation is repaired.

## Prohibited interpretation

- Do not call adapter availability replication.
- Do not tune the landmark after inspecting IBL neural results.
- Do not describe IBL left/right choice as the same target as Allen
  `go_response`.
- Do not pool Allen and IBL effect sizes without a task-aware hierarchical
  model.
