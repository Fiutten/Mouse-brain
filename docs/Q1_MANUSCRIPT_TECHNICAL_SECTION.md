# Q1 manuscript technical section: replicated MICRONS benchmark

## Core claim

MouseBrainBench provides a reproducible benchmark for auditing local
structure-function claims in partial mouse-brain digital models. In MICRONS
co-registered functional/EM data, synaptically connected directed pairs show
closer functional readout-location similarity than matched non-connected pairs.
The result replicates across a discovery cohort and an offset hold-out cohort.

## What is being tested

Primary endpoint:

```text
all_pairs / readout_location
```

For each co-registered MICRONS cohort, all directed non-self pairs are
constructed. Real connected pairs are compared against non-connected pairs under
three controls:

- random null;
- distance-matched null;
- degree-matched null.

The reported manuscript endpoint is only accepted if it is positive after
distance/degree matching and FDR correction in both discovery and hold-out
cohorts.

## Definitive result

| Cohort | Units | Synapses | Edge pairs | Confirmed tests | Distance delta | Distance q | Degree delta | Degree q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery | 1000 | 2267 | 2095 | 28 | 0.0215146 | 0.00755766 | 0.040264 | 0.00526746 |
| Hold-out offset1000 | 992 | 2161 | 1926 | 30 | 0.0210337 | 0.00703644 | 0.0380016 | 0.00622454 |

## Bootstrap stability

Unit-cluster bootstrap with 300 resamples:

| Cohort | Distance median | Distance CI95 | Degree median | Degree CI95 |
|---|---:|---:|---:|---:|
| Discovery | 0.0218114 | [0.0166454, 0.0262839] | 0.0405107 | [0.0348647, 0.0454170] |
| Hold-out offset1000 | 0.0209440 | [0.0142179, 0.0262773] | 0.0377419 | [0.0321422, 0.0430936] |

The lower bound is positive in both cohorts and both matched-control families.
This supports a replicated local structure-function association.

## Allowed interpretation

Allowed:

- replicated local MICRONS structure-function association;
- connected pairs have closer readout-location similarity than distance- and
  degree-matched non-connected pairs;
- MouseBrainBench prevents broad digital-twin claims from being inferred from a
  narrow positive result.

Blocked:

- causal mechanism;
- whole-brain mouse digital twin;
- behavioral digital twin;
- Sensorium SOTA predictor;
- measured whole-brain single-neuron connectome.

## Manuscript position

The strongest paper angle is not "we built a mouse brain twin". The defensible
angle is:

```text
MouseBrainBench is a reproducible claim-audit benchmark for partial mouse-brain
digital models, with a replicated MICRONS structure-function case demonstrating
how local synaptic evidence can be separated from causal or whole-brain claims.
```
