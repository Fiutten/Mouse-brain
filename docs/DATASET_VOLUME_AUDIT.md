# Dataset Volume Audit Before Manuscript

## Purpose

This audit checks whether the datasets used by MouseBrainBench are sufficiently
large for their intended scientific role. It does not ask whether every dataset
is large in absolute terms; it asks whether each layer is large enough for the
claim we plan to make.

## Decision Summary

| Layer | Dataset | Current volume | Intended role | Volume status | Action |
|---|---|---:|---|---|---|
| Main empirical claim | MICRONS CAVE structure-function | 3 cohorts, 2991 units, 6575 synapses, 5943 connected pairs | Primary Q1 local structure-function benchmark | Green | Sufficient; stop exploratory cohort mining |
| Negative mechanistic control | Allen Visual Behavior Neuropixels | 20-21 analyzed sessions depending on phase; metadata cache has 153 sessions | Demonstrate reproducible prediction can fail mechanistic identifiability | Green/amber | Sufficient for negative control; do not make it a positive claim |
| Static predictive case | Sensorium 2022 static | 7 validation mice, 5 repeated-test mice, 43805 validation trials, 54569 validation neurons | Positive predictive/reliability auxiliary case | Amber | Adequate as auxiliary; not enough for central Q1 claim without official/SOTA baseline |
| Dynamic predictive case | Dynamic Sensorium 2023 current | 5 public mice | Temporal predictive stress test | Amber/red | Adequate for method demo; short for strong predictive claim |
| Dynamic OOD check | Dynamic Sensorium legacy OOD | 5 mice | External OOD sanity check | Amber | Useful as consistency check; not enough as main contribution |
| Synthetic benchmark | Controlled simulated cases | 4 designed cases | Validate MIS logic under known truth | Green for unit logic | Keep as methods validation, not empirical evidence |

## MICRONS

MICRONS is now the only layer with enough data volume to carry the positive Q1
empirical claim.

| Cohort | Units | Synapses | Connected edge pairs | Candidate directed pairs |
|---|---:|---:|---:|---:|
| Discovery | 1000 | 2267 | 2095 | 999000 |
| Hold-out offset1000 | 992 | 2161 | 1926 | 983072 |
| Hold-out offset2000 | 999 | 2147 | 1922 | 997002 |
| Total | 2991 | 6575 | 5943 | 2979074 |

Decision: sufficient for a local observational structure-function benchmark
claim because the same primary endpoint replicates across discovery and two
hold-outs and remains positive under unit-cluster bootstrap.

Boundary: still not a causal, behavioral, or whole-brain digital-twin claim.

## Allen Visual Behavior Neuropixels

Allen/VBN is used as a negative mechanistic-identifiability control:

- phase 2C confirmation: 20 successful sessions;
- phase 3 anatomical connectivity test: 20 sessions, 20 unique mice;
- phase 4 directed identifiability test: 21 sessions, 19 unique mice;
- cached project metadata: 153 session rows.

Key result:

- reproducibility passes;
- topology specificity fails;
- directed identifiability fails;
- final MIS decision: `reproducible_target_without_mechanistic_identifiability`.

Decision: the volume is acceptable for a negative-control layer because the
claim is not "Allen proves our model"; the claim is "MouseBrainBench blocks
mechanistic overclaiming when reproducibility is present but topology and
directionality fail."

Risk: if Allen becomes a central empirical section, we should expand from the
20-session analysis to a broader predeclared subset of the cached metadata.
For the current manuscript route, that is not required.

## Sensorium Static

Sensorium static is used as an auxiliary positive predictive/reliability case.

Current volume:

- 7 downloaded validation mice;
- 5 repeated-test mice;
- 43805 validation trials across 54569 neurons;
- 29891 repeated-test trials across 39255 neurons;
- 5/5 topographic-constraint checks pass in the current local test.

Key result:

- validation median best predictive correlation: 0.327945;
- repeated-test median reliability: 0.642032;
- repeated-test median best predictive correlation: 0.340952;
- MIS remains incomplete because predictive reliability is not causal or
  interventional evidence.

Decision: adequate as an auxiliary layer showing that MouseBrainBench separates
prediction/reliability/topography from mechanistic identifiability.

Risk: not enough for a central Q1 claim unless we add either a stronger official
Sensorium/SOTA baseline or a more formal structural/mechanistic constraint.

## Dynamic Sensorium

Dynamic Sensorium is currently a predictive stress-test layer, not a mechanistic
pillar.

Current volume:

- 5 current public Dynamic Sensorium mice;
- 5 legacy OOD mice;
- several transparent local baselines: mean response, summary adapter,
  temporal filterbank, temporal SVD, random feature, Torch MLP, and bounded
  official Sensorium baseline.

Key result:

- current temporal filterbank improves over summary descriptors in 4/5 mice;
- current Torch MLP improves over mean in 5/5 mice;
- bounded official Sensorium improves over mean in 4/5 mice, but remains far
  below local temporal/SVD/MLP baselines;
- legacy OOD temporal filterbank improves over summary in 5/5 mice;
- reliability is not estimable in the available dynamic artifacts;
- MIS passed count remains 0.

Decision: useful as a predictive benchmark and stress test. It is short for a
strong Q1 empirical claim because only 5 current mice and 5 OOD mice are active,
and the official Sensorium baseline is not Q1-qualified locally.

Required if promoted to a stronger paper component:

1. Add more Dynamic Sensorium public mice if accessible from the same release.
2. Freeze a predeclared inclusion rule.
3. Re-run all local baselines and the official baseline under the same split.
4. Report uncertainty across mice and avoid SOTA language unless using official
   leaderboard-equivalent training/evaluation.

## Synthetic MIS Benchmark

The synthetic benchmark has 4 controlled cases and is sufficient for logic
validation:

- directed truth;
- common drive;
- structure without temporal direction;
- timing without region-specific topology.

Decision: sufficient as a test of the MIS acceptance logic. It is not empirical
evidence about mouse brain data.

## Final Recommendation

The manuscript should use MICRONS as the main empirical contribution. Allen,
Sensorium static, Dynamic Sensorium, and synthetic experiments should be framed
as benchmark layers that demonstrate the audit logic:

- Allen: reproducible but mechanistically negative;
- Sensorium static: predictive and partly topographic, but not causal;
- Dynamic Sensorium: predictive temporal stress test, currently underpowered for
  central claims;
- synthetic: sanity check with known truth.

Do not download more MICRONS for exploratory endpoint selection. If more data
collection is needed before submission, prioritize Dynamic Sensorium or an
official Sensorium baseline only if we want that layer to become a stronger
secondary contribution.
