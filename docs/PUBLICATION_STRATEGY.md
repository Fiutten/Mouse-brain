# Publication strategy

## Purpose

This document separates publishable scientific contributions from the broader
long-term digital-twin ambition. It is a decision aid, not a commitment to
submit every possible story.

## Current evidence boundary

The project has a reproducible but falsified dynamic-window result in Allen
Visual Behavior Neuropixels:

- 29 strict usable `go_response` sessions from 23 animals;
- positive aggregate dynamic `pre_response` gain with a session-bootstrap
  interval above zero;
- substantial session and within-session heterogeneity;
- persistent negative cases retained in the analysis;
- no causal regional, mechanistic-microcircuit or digital-twin claim.

The main threat has been confirmed: `pre_response` ends are derived from actual
response time on response trials, and timing-only window metadata predicts
`go_response` with mean balanced accuracy `0.985`. The dynamic-window neural
result must therefore be withdrawn as primary biological evidence. A fixed
early window retains descriptive predictive gain, but its neural contribution
is not confirmed after direct running/pupil adjustment because the
session-bootstrap interval crosses zero.

## Route A: empirical computational neuroscience

### Candidate question

Are neural population signals preceding action stable across mouse
visual-behavior sessions, or are they conditional on internal state, recording
coverage and session context?

### Potential contribution

- quantify reproducible pre-action predictivity without discarding null cases;
- distinguish state-dependent failures from persistent null sessions;
- estimate animal-level and session-level heterogeneity;
- identify which measured state and anatomical variables explain that
  heterogeneity;
- replicate the result in a second dataset or genuinely held-out cohort.

### Minimum evidence required

- response-independent fixed-window or landmark result;
- blocked temporal and animal-aware predictive validation;
- multiple-comparison control;
- direct state variables, preferably running and pupil;
- external or preregistered held-out replication.

### Current readiness

Not ready as a positive neural-discovery paper. The most credible current
framing concerns temporal-alignment leakage, state sensitivity and
heterogeneous failure modes. A positive biological route requires new
confirmatory fixed-window evidence.

## Route B: state-conditioned NeuroAI method

### Candidate question

Can a hierarchical or state-conditioned model generalize neural-behavior
prediction across sessions and animals better than global and session-specific
baselines?

### Potential contribution

- a model that separates shared neural signal from animal/session state;
- calibrated uncertainty for new animals;
- explicit handling of persistent-null and state-dependent sessions;
- cross-dataset evaluation.

### Minimum evidence required

- meaningful improvement over logistic, hierarchical GLM, GLM-HMM and simple
  nonlinear baselines;
- leave-one-animal-out prediction, not only descriptive aggregation;
- calibration and failure analysis;
- external dataset replication.

### Current readiness

Not ready. The current latent model is negative and the agent/graph layers are
not an AI-method contribution by themselves.

## Route C: auditable computational-science infrastructure

### Candidate question

Can an evidence graph and executable reviewer rules reduce unsupported claims
and improve reproducibility in computational neuroscience workflows?

### Potential contribution

- machine-readable claim/evidence states;
- deterministic blocking of causal or mechanistic overclaims;
- reproducibility manifests and negative-result retention;
- evaluation over multiple datasets and research questions.

### Minimum evidence required

- formal claim ontology;
- comparison with conventional analysis workflows;
- blinded or multi-user evaluation;
- quantitative measures of detected errors, reproducibility and false claims.

### Current readiness

Useful internal infrastructure, but not yet independently validated as a
research method.

## Route D: digital twin

This route is intentionally deferred.

A defensible digital twin must predict unseen neural activity or behavior,
adapt to an individual animal, produce counterfactuals and validate those
counterfactuals against empirical perturbations. The current surrogate and
microcircuit do not meet this definition.

## Publication decision rule

1. If response-independent and landmark analyses become confirmatorily
   positive after state adjustment, prioritize
   Route A and develop Route B as its modeling contribution.
2. The dynamic `pre_response` result has failed the timing-leakage control. Do
   not preserve the original biological claim. Evaluate whether the
   leakage/falsification result is sufficiently general to support a
   methodological paper.
3. Do not lead with the graph, LLM, microcircuit or digital-twin language until
   each has independent empirical validation.
