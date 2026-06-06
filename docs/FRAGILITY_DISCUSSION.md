# Fragility discussion: expanded Allen `go_response` cohort

## Scope

This document explains the 9 fragile sessions identified in the 29-session
strict usable `go_response` cohort. It is intended as a discussion-ready
scientific interpretation, not as a post-hoc exclusion rule.

The stability label combines five evidence checks:

1. positive `pre_response` gain;
2. significant temporal permutation result;
3. positive visual-cortex ablation drop;
4. positive fast-latency gain;
5. positive slow-latency gain.

Fragile sessions pass fewer than two of these five checks.

## Main Finding

The 9 fragile sessions are scientifically meaningful negative cases:

- 6 are `global_temporal_null` sessions. The primary temporal effect is absent
  or non-significant and both fast/slow latency strata fail.
- 3 are `weak_or_non_significant_temporal_effect` sessions. They retain at
  least one subordinate positive check, but the primary temporal effect is too
  weak or uncertain.

The fragile sessions are:

```text
1044594870
1064644573
1067588044
1087720624
1090803859
1092283837
1092466205
1122903357
1125713722
```

## Independent Explanation Tests

To avoid circularity, the explanation analysis excludes the temporal,
regional-ablation and latency-stratum gains used to define fragility. Fragile
sessions were compared with the 20 mixed/robust sessions using 20,000
label-permutation tests per numeric covariate.

| candidate explanation | fragile mean | other mean | standardized difference | permutation p | interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| labeled `go_response` trials | 224.778 | 244.800 | -0.469 | 0.250 | unsupported |
| `go_response` minority fraction | 0.299 | 0.347 | -0.559 | 0.178 | weak balance candidate |
| mean latency ms | 556.340 | 529.544 | 0.196 | 0.628 | unsupported |
| median latency ms | 449.847 | 433.008 | 0.140 | 0.748 | unsupported |
| zero-latency fraction | 0.225 | 0.273 | -0.395 | 0.331 | unsupported |
| coarse region count | 4.444 | 4.300 | 0.296 | 0.673 | unsupported |
| unit count | 2345.111 | 2520.350 | -0.547 | 0.186 | weak recording-coverage candidate |
| probe count | 5.778 | 6.000 | -0.926 | 0.088 | weak recording-coverage candidate |
| complete session metadata | 1.000 | 1.000 | 0.000 | 1.000 | unsupported |

No independent coarse covariate currently qualifies as a supported
explanation. Probe count, unit count and target minority fraction are weak
candidates, but none passes the permutation threshold. The earlier apparent
metadata-completeness difference was caused by an incomplete local metadata
join and disappeared after the project metadata CSV was made authoritative.

## Animal And Task Effects

Animal identity does not provide a sufficient explanation:

- animal `560771` contributes two fragile sessions;
- animal `556014` contributes one fragile and one mixed session;
- animals `548721`, `553253` and `555304` each span mixed and robust states;
- animal `578003` contributes two robust sessions.

This pattern allows an animal-level susceptibility hypothesis, but it also
shows that session state matters within animals.

Experience level and image set do not cleanly separate fragile from
non-fragile sessions. Fragile sessions include both Familiar/G and Novel/H
conditions. The corrected metadata join provides these fields for all current
usable sessions.

## Scientific Explanation

The most defensible current explanation is **partly state-dependent and partly
persistent session/circuit heterogeneity, potentially compounded by recording
coverage**.

The evidence argues against three simpler explanations:

- fragility is not merely target-class imbalance, because all 9 sessions pass
  the strict target-usability threshold;
- fragility is not adequately explained by fewer labeled trials or slower
  responses;
- fragility is not adequately explained by coarse region count, task
  experience or image set.

The six global temporal-null sessions are especially important. Their failure
across the primary window and both latency strata suggests that the current
compact neural features do not capture a universal pre-response signature.
Possible explanations include latent engagement/arousal state, probe placement
within coarse regions, cell-type composition, within-session nonstationarity,
or a genuinely alternative neural strategy.

## Alternative Windows

The 9 fragile sessions were tested with 50 permutation iterations in the
`baseline`, `stimulus` and `decision` windows.

| result | sessions |
| --- | ---: |
| no alternative-window rescue | 4 |
| decision-window rescue, motor contamination possible | 3 |
| stimulus-window rescue | 1 |
| baseline-state signal | 1 |

The decision window is positive in 4/9 fragile sessions and significant in
3/9. This is not a pre-response rescue: it may indicate later decision-related
or motor-linked activity. Only session `1125713722` shows a stimulus-window
rescue, and only `1092283837` shows a baseline-state signal.

These results split the fragile group. Five sessions contain predictive
information outside the candidate window, while four remain broad
alternative-window nulls under the current coarse features.

## Within-Session State Dependence

The full 29-session usable cohort was split into early/middle/late
chronological thirds and low/high engagement states. Each state used a
20-permutation screen.

| classification | sessions |
| --- | ---: |
| state-dependent supported | 21 |
| no supported state | 7 |
| state-invariant supported | 1 |

The middle chronological block is the strongest aggregate state, with mean gain
`0.163` and significant fraction `0.552`. This indicates substantial
within-session nonstationarity across the cohort.

Within the fragile subgroup:

- `1067588044` is supported in middle and late blocks;
- `1122903357` is supported only in the early block;
- `1125713722` is supported in middle and late blocks;
- the other six fragile sessions have no positively supported state.

Thus, three fragile sessions are better described as state-dependent failures
of the whole-session analysis. Six remain persistent null/weak cases across the
tested state partitions.

## Discussion-Ready Language

A substantial minority of behaviorally usable sessions lacked the candidate
pre-response signature. These failures were not adequately explained by class
balance, trial count, response latency, coarse region count, experience level,
or image set. The pattern therefore argues against a universal temporal
mechanism and favors a state-dependent or circuit-heterogeneous account. A
possible contribution from recording coverage remains, because lower probe and
unit counts appeared as weak candidates. Fragile sessions
should be retained as explicit negative cases for future state, anatomy and
recording-quality stratification rather than removed from the cohort.

## Claim Boundary

Defensible:

- the expanded cohort contains a reproducible positive aggregate dynamic-window
  prediction result and a substantial negative-case subgroup;
- the negative subgroup is not explained by the current coarse behavioral
  covariates;
- the dynamic-window result is largely target-timing contaminated and should
  be retained as a falsification result, not biological evidence;
- fixed-window predictivity is state/session-dependent and not yet confirmed
  beyond direct running/pupil adjustment.

Not defensible:

- using dynamic `pre_response` as clean neural evidence;
- claiming a universal pre-response mechanism;
- excluding fragile sessions to strengthen the aggregate claim;
- attributing fragility to probe/unit count without fine placement, depth and
  unit-quality metadata;
- interpreting the current regional or microcircuit layers as causal.

## Required Follow-Up

1. Confirm fixed-window/landmark neural gain after direct state adjustment.
2. Add finer fixed neural time bins for a discrete-time hazard analysis.
3. Extend the completed leave-one-animal-out summary into a hierarchical
   predictive model.
4. Validate the state-dependent/persistent-null split in a second dataset.

## Completed Validation Addendum

- The expanded 29-session dynamic `pre_response` computation is reproducible
  with 500 permutations per session: mean gain `0.149`, significant fraction
  `0.552`. It is not clean neural evidence because target-derived window timing
  alone predicts the target.
- Leave-one-animal-out aggregate gain remains positive for all 23 animals:
  minimum `0.128`, maximum `0.160`.
- Coarse presence of visual cortex, visual thalamus, hippocampus and
  arousal-midbrain is identical across fragile and other sessions.
- The metadata join was corrected so Allen project metadata, rather than the
  latest batch snapshot, is authoritative. All 29 usable sessions now have
  probe/unit/task metadata in the relationship analysis.
- Direct running, pupil, unit-quality and channel-coordinate sidecars were
  exported for all 30 locally available NWBs. No simple session-level feature
  explains gain after 20,000-permutation tests and BH correction.
