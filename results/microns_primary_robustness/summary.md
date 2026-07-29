# MICRONS Primary Endpoint Robustness

- Decision: `microns_primary_endpoint_survives_harder_controls`
- Primary endpoint: `all_pairs/readout_location`
- All cohorts robust: `True`

| Cohort | Units | Connected pairs | Combined delta | Combined p | Shuffle delta | Robust |
|---|---:|---:|---:|---:|---:|---:|
| `discovery` | `1000` | `2095` | `0.0149217` | `0.00199601` | `0.0213116` | `True` |
| `holdout_offset1000` | `992` | `1926` | `0.017478` | `0.00199601` | `0.0208397` | `True` |
| `holdout_offset2000` | `999` | `1922` | `0.0146847` | `0.00199601` | `0.0178503` | `True` |

## Interpretation

Positive results remain local and observational. Combined matching and within-distance shuffling reduce obvious degree and spatial confounds, but they do not establish causality or independent biological replication.
