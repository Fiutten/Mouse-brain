# Sensorium Official Baseline Audit

- Decision: `official_sensorium_baseline_not_locally_viable_use_tracked_torch_mlp`
- Official baseline viable: `False`
- Local MLP available: `True`
- Recommended action: Use the tracked compact PyTorch MLP as the local NN control, while stating explicitly that it is not an official/SOTA Sensorium model.

## Package probes

| Package | Available | Purpose |
|---|---:|---|
| `sensorium` | `False` | official Sensorium data/model helper package |
| `neuralpredictors` | `False` | standard Ecker/Sinz lab neural predictor models |
| `nnfabrik` | `False` | model/dataloader factory used by official examples |
| `datajoint` | `False` | metadata/backend dependency used by the ecosystem |
| `pytorch_lightning` | `False` | training loop dependency used by many baselines |

## Interpretation

Official Sensorium baselines are the preferred external control, but they are only acceptable for this project when the environment can run them reproducibly. Otherwise the local MLP remains a neural-network control rather than a SOTA claim.
