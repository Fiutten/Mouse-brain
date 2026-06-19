# Sensorium Official Baseline Audit

- Decision: `official_sensorium_stack_integrated_training_pending`
- Official stack forward OK: `True`
- Official trained baseline available: `False`
- Official baseline Q1-viable: `False`
- Local MLP available: `True`
- Recommended action: Treat the official stack as integrated at smoke-test level, but keep the tracked compact PyTorch MLP as the evaluated NN control until an official trained baseline summary exists.

## Package probes

| Package | Available | Purpose |
|---|---:|---|
| `sensorium` | `True` | official Sensorium data/model helper package |
| `neuralpredictors` | `True` | standard Ecker/Sinz lab neural predictor models |
| `nnfabrik` | `True` | model/dataloader factory used by official examples |
| `datajoint` | `True` | metadata/backend dependency used by the ecosystem |
| `torch` | `True` | PyTorch runtime required by official Sensorium models |
| `torchvision` | `True` | implicit neuralpredictors dependency for convolutional cores |

## Interpretation

Official Sensorium baselines are the preferred external control, but they only count for Q1 when trained/evaluated predictions are available. A forward-pass smoke test proves integration, not leaderboard-level performance.
