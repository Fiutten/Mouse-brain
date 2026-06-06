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
| unit count | 2411.833 | 2557.053 | -0.473 | 0.333 | unsupported; missing metadata |
| probe count | 5.667 | 6.000 | -1.384 | 0.054 | weak recording-coverage candidate |
| complete session metadata | 0.667 | 0.950 | -0.857 | 0.073 | technical confound candidate |

No independent coarse covariate currently qualifies as a supported
explanation. Probe count and metadata completeness are the strongest weak
candidates, but both are affected by missing metadata in 3/9 fragile sessions.
Among the six fragile sessions with known probe count, two have five probes and
four have six probes.

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
conditions. Three fragile sessions lack these metadata fields, limiting formal
categorical interpretation.

## Scientific Explanation

The most defensible current explanation is **unresolved session-state or
circuit heterogeneity, potentially compounded by recording coverage**.

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

## Discussion-Ready Language

A substantial minority of behaviorally usable sessions lacked the candidate
pre-response signature. These failures were not adequately explained by class
balance, trial count, response latency, coarse region count, experience level,
or image set. The pattern therefore argues against a universal temporal
mechanism and favors a state-dependent or circuit-heterogeneous account. A
possible contribution from recording coverage remains, because lower probe
count appeared as a weak candidate under incomplete metadata. Fragile sessions
should be retained as explicit negative cases for future state, anatomy and
recording-quality stratification rather than removed from the cohort.

## Claim Boundary

Defensible:

- the expanded cohort contains a reproducible positive aggregate
  `pre_response` signal and a substantial negative-case subgroup;
- the negative subgroup is not explained by the current coarse behavioral
  covariates;
- the current model should be described as state/session-dependent.

Not defensible:

- claiming a universal pre-response mechanism;
- excluding fragile sessions to strengthen the aggregate claim;
- attributing fragility to probe count without complete placement/coverage
  metadata;
- interpreting the current regional or microcircuit layers as causal.

## Required Follow-Up

1. Complete the 500-permutation confirmation for all 29 usable sessions.
2. Recover missing session metadata and quantify probe placement/unit coverage
   within each coarse region.
3. Add within-session state features such as engagement, running/pupil proxies,
   block position and temporal nonstationarity.
4. Perform animal-aware hierarchical or leave-one-animal-out validation.
5. Test whether fragile sessions use alternative windows or regional patterns
   instead of treating them only as absent-signal cases.
