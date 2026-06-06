# Scientific execution phases before digital-twin development

## Operating rule

Every phase has an explicit completion criterion. Implemented code is not
equivalent to completed science, and an unavailable dataset is not a positive
result.

## Phase 1: falsify the current temporal result

### Questions

- Does `pre_response` predict behavior because its end time depends on the
  observed response?
- Does response-independent neural activity predict later response?
- Does the result survive blocked temporal validation and structured nulls?

### Required analyses

1. Predict the target from window duration/validity metadata alone.
2. Test fixed response-independent windows.
3. Run landmark analyses containing only trials still at risk at the horizon.
4. Compare random-shuffle and temporally structured nulls.
5. Correct session/window hypothesis tests for multiple comparisons.
6. Repeat across chronological splits.

### Completion criterion

At least one response-independent neural analysis must show positive aggregate
gain with uncertainty above zero and survive the prespecified controls.
Otherwise the original pre-response interpretation is rejected.

## Phase 2: model response timing and heterogeneity

### Questions

- Is the neural signal associated with whether the animal responds, when it
  responds, or both?
- How much heterogeneity lies between animals, between sessions and within
  sessions?

### Required analyses

1. Landmark response-risk models at fixed horizons.
2. A discrete-time hazard model once suitably binned neural features exist.
3. Animal-cluster bootstrap and variance decomposition.
4. Leave-one-animal-out predictive validation.
5. State-conditioned comparison using measured state variables.

### Completion criterion

The model must improve prediction for held-out animals or clearly establish
that effects are session-specific. Descriptive leave-one-animal-out averages
alone are insufficient.

## Phase 3: explain heterogeneity with measured variables

### Required variables

- running speed and pupil measurements;
- reward and response history;
- block position and temporal drift;
- probe coordinates, depth and fine anatomy;
- unit quality and, where available, cell-class proxies.

### Completion criterion

Candidate explanations must be evaluated out of sample with uncertainty and
multiple-comparison control. Proxy engagement and coarse region presence cannot
support a strong state or anatomy claim.

## Phase 4: replication

### Internal confirmation

Use a frozen analysis on a cohort that was not used to select targets, windows,
thresholds or model structure. A post-hoc partition of the current cohort is a
sensitivity analysis, not a true replication.

### External replication

Normalize a compatible IBL or other public dataset and test a
task-harmonized claim. Dataset-specific target differences must be declared;
conceptual replication is not exact replication.

### Completion criterion

The frozen primary analysis passes on a genuinely untouched cohort or a
task-harmonized external dataset. Until then, the claim remains
dataset-specific.

## Phase 5: digital twin

Deferred by project decision. It begins only after the preceding phases
establish a stable empirical target and validated generalization boundary.

## Current status

| phase | status | reason |
| --- | --- | --- |
| Phase 1 | dynamic claim falsified; fixed route active | timing-only metadata predicts the dynamic target at balanced accuracy 0.985; fixed 0-250 ms and landmark analyses require confirmation |
| Phase 2 | active/partial | landmark and animal-cluster analyses exist; full hazard and leave-one-animal-out predictive models do not |
| Phase 3 | active/partial | running, pupil, unit quality and channel coordinates were exported for 30 local NWBs; no simple session-level explanation is supported |
| Phase 4 | protocol frozen/blocked | no external normalized cohort; isolated IBL environment creation failed due corrupted local Conda packages |
| Phase 5 | deferred | intentionally postponed |

## Current critical result

The fixed 0-250 ms neural window has positive mean gain across several
chronological splits. However, after excluding responses before 250 ms and
adjusting trial by trial for running and pupil in the same interval, the mean
neural gain is `0.027` with CI95 `[-0.031, 0.078]`. Therefore an independent
fixed-window neural contribution is not currently confirmed.

The dynamic `pre_response` construction is no longer eligible as primary
neural evidence. Window duration/end/validity alone predict `go_response` with
mean balanced accuracy `0.985`, demonstrating target-timing leakage.
