# Dynamic Sensorium Model Comparator

This comparator asks whether progressively stronger transparent models improve held-out prediction and whether that improvement is allowed to count as mechanistic evidence. Current Dynamic Sensorium artifacts remain predictive evidence only because MIS does not pass.

## dynamic_sensorium2023_oracle

- Ratones comparados: `5`
- Evidencia: `predictive_benchmark_requires_reliability_or_causal_constraints`
- MIS passed: `0`
- Reliability estimable: `0`

| Comparación | Victorias modelo derecho | Mediana delta | Media delta |
|---|---:|---:|---:|
| summary_adapter_vs_temporal_filterbank | `4/5` | `0.008472` | `0.009081` |
| mean_response_vs_temporal_filterbank | `5/5` | `0.031135` | `0.028523` |
| mean_response_vs_temporal_svd | `4/5` | `0.038886` | `0.032829` |
| temporal_filterbank_vs_temporal_svd | `3/5` | `0.007751` | `0.004307` |

| Mouse | Mean | Summary | Temporal filterbank | Temporal SVD | Best |
|---|---:|---:|---:|---:|---|
| `dynamic29515` | `0.42377` | `0.422444` | `0.430917` | `0.414528` | `temporal_filterbank` |
| `dynamic29623` | `0.367982` | `0.390218` | `0.403052` | `0.427126` | `temporal_svd` |
| `dynamic29647` | `0.447155` | `0.480146` | `0.474168` | `0.486161` | `temporal_svd` |
| `dynamic29712` | `0.452984` | `0.475949` | `0.48412` | `0.49187` | `temporal_svd` |
| `dynamic29755` | `0.480565` | `0.500909` | `0.522813` | `0.516918` | `temporal_filterbank` |

## dynamic_sensorium_legacy_ood

- Ratones comparados: `5`
- Evidencia: `positive_ood_prediction_without_mechanistic_identifiability`
- MIS passed: `0`
- Reliability estimable: `0`

| Comparación | Victorias modelo derecho | Mediana delta | Media delta |
|---|---:|---:|---:|
| summary_adapter_vs_temporal_filterbank | `5/5` | `0.011062` | `0.012608` |
| mean_response_vs_temporal_filterbank | `4/5` | `0.025008` | `0.018932` |
| mean_response_vs_temporal_svd | `5/5` | `0.03091` | `0.030865` |
| temporal_filterbank_vs_temporal_svd | `5/5` | `0.005855` | `0.011933` |

| Mouse | Mean | Summary | Temporal filterbank | Temporal SVD | Best |
|---|---:|---:|---:|---:|---|
| `dynamic29156` | `0.364959` | `0.362926` | `0.391491` | `0.398837` | `temporal_svd` |
| `dynamic29228` | `0.412573` | `0.417795` | `0.428857` | `0.434712` | `temporal_svd` |
| `dynamic29234` | `0.329388` | `0.322883` | `0.323004` | `0.360298` | `temporal_svd` |
| `dynamic29513` | `0.388562` | `0.411134` | `0.421781` | `0.426574` | `temporal_svd` |
| `dynamic29514` | `0.403803` | `0.416169` | `0.428811` | `0.433187` | `temporal_svd` |
