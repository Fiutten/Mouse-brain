# MICRONS Q1 Replicated Structure-Function Package

- Primary endpoint: `all_pairs/readout_location`
- Q1 package ready: `True`
- Bootstrap cluster: `unit`
- Bootstrap samples: `300`

## Definitive Cohort Table

| Cohort | Units | Synapses | Edge pairs | Confirmed tests | Distance delta | Distance q | Degree delta | Degree q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `discovery` | `1000` | `2267` | `2095` | `28` | `0.0215146` | `0.00755766` | `0.040264` | `0.00526746` |
| `holdout_offset1000` | `992` | `2161` | `1926` | `30` | `0.0210337` | `0.00703644` | `0.0380016` | `0.00622454` |
| `holdout_offset2000` | `999` | `2147` | `1922` | `25` | `0.0178845` | `0.00869131` | `0.0286419` | `0.00827744` |

## Unit-Cluster Bootstrap Stability

| Cohort | Distance median | Distance CI95 | Degree median | Degree CI95 |
|---|---:|---:|---:|---:|
| `discovery` | `0.0218114` | `[0.0166454, 0.0262839]` | `0.0405107` | `[0.0348647, 0.045417]` |
| `holdout_offset1000` | `0.020944` | `[0.0142179, 0.0262773]` | `0.0377419` | `[0.0321422, 0.0430936]` |
| `holdout_offset2000` | `0.0181306` | `[0.0115043, 0.0237966]` | `0.0287003` | `[0.0228738, 0.035367]` |

## Claims Allowed

- Replicated local MICRONS structure-function association.
- Connected pairs show closer readout-location similarity than distance- and degree-matched controls.
- MouseBrainBench provides a reproducible claim-audit benchmark for partial mouse-brain digital models.

## Claims Blocked

- Causal mechanism.
- Whole-brain mouse digital twin.
- Behavioral digital twin.
- Sensorium SOTA predictor.
