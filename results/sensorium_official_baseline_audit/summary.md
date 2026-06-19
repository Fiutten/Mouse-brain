# Sensorium Official Baseline Audit

- Decision: `official_sensorium_tiny_trained_baseline_available_not_q1_qualified`
- Official stack forward OK: `True`
- Official trained baseline available: `True`
- Official trained usable mice: `5`
- Official baseline Q1-qualified: `False`
- Official baseline Q1-viable: `False`
- Local MLP available: `True`
- Recommended action: Use the bounded trained official-architecture baseline as an internal MouseBrainBench control, but do not present it as a Q1-level official Sensorium benchmark until the qualification rule is met.

## Package probes

| Package | Available | Purpose |
|---|---:|---|
| `sensorium` | `False` | official Sensorium data/model helper package |
| `neuralpredictors` | `False` | standard Ecker/Sinz lab neural predictor models |
| `nnfabrik` | `False` | model/dataloader factory used by official examples |
| `datajoint` | `False` | metadata/backend dependency used by the ecosystem |
| `torch` | `True` | PyTorch runtime required by official Sensorium models |
| `torchvision` | `False` | implicit neuralpredictors dependency for convolutional cores |

## Interpretation

Official Sensorium baselines are the preferred external control, but they only count for Q1 when trained/evaluated predictions are available. A forward-pass smoke test proves integration, not leaderboard-level performance.
